"""
generar_enhanced.py
====================
Paso 6 del pipeline. Toma el CSV enriquecido, aplica correcciones programáticas
y exporta el dataset enhanced listo para Modelo-Libertadores.

Correcciones aplicadas:
  1. Forward-fill de instancia para partidos de Grupos sin grupo asignado,
     dentro de cada temporada (el RSSSF a veces pone partidos antes del header).
  2. Normalización de campo 'resultado': asegura que sea L/V/E (no resultado_norm).

Limitaciones documentadas (requieren completado manual o via IA):
  - 1997: grupos no parseados (formato sin espacios alrededor del guion)
  - 1998: grupos parcialmente parseados
  - 2011: temporada completa ausente (formato RSSSF alternativo)
  - 2012: grupos casi ausentes (formato sin guion entre equipos)
  - Eliminatorias 2000-2024: no parseadas (ver docs/prompt_completar_datos.md)
"""

from pathlib import Path
import pandas as pd
import sys

RUTA_ENTRADA = Path("datos/procesados/partidos_rsssf1_enriquecido.csv")
RUTA_SALIDA = Path("datos/procesados/partidos_rsssf1_enhanced.csv")
RUTA_AUDITORIA = Path("reportes/auditoria_enhanced.md")

TEMPORADAS_ESPERADAS = list(range(1996, 2025))
FASES_ESPERADAS = {"Grupos", "Octavos", "Cuartos", "Semifinal", "Final"}


def corregir_instancia_grupos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mask_grupos = df["fase"] == "Grupos"
    for temporada in df["temporada"].unique():
        idx = df[(df["temporada"] == temporada) & mask_grupos].index
        df.loc[idx, "instancia"] = (
            df.loc[idx, "instancia"]
            .infer_objects(copy=False)
            .ffill()
            .bfill()
        )
    return df


def generar_auditoria(df: pd.DataFrame) -> str:
    lineas = [
        "# Auditoría dataset enhanced — Copa Libertadores 1996–2024",
        "",
        "## Resumen",
        f"- Total partidos: {len(df)}",
        f"- Temporadas cubiertas: {df['temporada'].nunique()} de {len(TEMPORADAS_ESPERADAS)}",
        f"- Rango: {df['temporada'].min()}–{df['temporada'].max()}",
        f"- Promedio goles local: {df['goles_local'].mean():.2f}",
        f"- Promedio goles visitante: {df['goles_visitante'].mean():.2f}",
        "",
        "## Cobertura por temporada",
        "",
        "| Temporada | Grupos | Octavos | Cuartos | Semifinal | Final | Total |",
        "|-----------|--------|---------|---------|-----------|-------|-------|",
    ]

    for t in TEMPORADAS_ESPERADAS:
        sub = df[df["temporada"] == t]
        if len(sub) == 0:
            lineas.append(f"| {t} | ❌ | ❌ | ❌ | ❌ | ❌ | 0 |")
            continue
        grupos = len(sub[sub["fase"] == "Grupos"])
        octavos = len(sub[sub["fase"] == "Octavos"])
        cuartos = len(sub[sub["fase"] == "Cuartos"])
        semi = len(sub[sub["fase"] == "Semifinal"])
        final = len(sub[sub["fase"] == "Final"])
        total = len(sub)

        def fmt(n, expected_min=1):
            return str(n) if n >= expected_min else f"⚠️ {n}"

        lineas.append(
            f"| {t} | {fmt(grupos,1)} | {fmt(octavos,0)} | {fmt(cuartos,1)} | {fmt(semi,1)} | {fmt(final,1)} | {total} |"
        )

    lineas += [
        "",
        "## Campos con valores faltantes (post-enhanced)",
        "",
    ]

    for col in df.columns:
        nulls = df[col].isna().sum()
        empties = (df[col].astype(str).str.strip() == "").sum() if df[col].dtype == object else 0
        total_prob = nulls + empties
        if total_prob > 0:
            lineas.append(f"- `{col}`: {total_prob} valores vacíos/nulos de {len(df)}")

    lineas += [
        "",
        "## Gaps conocidos — requieren completado via IA",
        "",
        "Ver `docs/prompt_completar_datos.md` para el prompt listo para enviar a Claude u otra IA.",
        "",
        "| Año | Tipo de gap | Estimación filas faltantes |",
        "|-----|------------|---------------------------|",
        "| 1997 | Grupos completos (formato RSSSF sin espacio) | ~60 |",
        "| 1998 | Grupos parciales (misma causa) | ~50 |",
        "| 2011 | Temporada completa (formato alternativo) | ~160 |",
        "| 2012 | Grupos casi completos (formato sin guion) | ~105 |",
        "| 2000–2024 | Eliminatorias (Octavos, Cuartos, Semifinal, Final) | ~400 |",
        "",
        "**Total estimado de filas faltantes**: ~775 partidos adicionales.",
        "",
        "Con esas filas, el dataset pasaría de ~2281 a ~3050 partidos.",
    ]

    return "\n".join(lineas) + "\n"


def main():
    if not RUTA_ENTRADA.exists():
        print(f"ERROR: no existe {RUTA_ENTRADA}. Correr el pipeline primero.")
        sys.exit(1)

    df = pd.read_csv(RUTA_ENTRADA)
    print(f"Cargado: {len(df)} filas desde {RUTA_ENTRADA}")

    # Corrección 1: instancia grupos
    antes = df["instancia"].isna().sum()
    df = corregir_instancia_grupos(df)
    despues = df["instancia"].isna().sum()
    print(f"instancia: {antes} nulls → {despues} nulls (corregidos {antes - despues})")

    # Corrección 2: resultado_norm ya está; asegurar que resultado sea L/V/E
    mapeo = {"LOCAL": "L", "VISITANTE": "V", "EMPATE": "E"}
    df["resultado"] = df["resultado"].replace(mapeo)

    # Exportar enhanced
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")
    print(f"OK -> {RUTA_SALIDA} | filas={len(df)}")

    # Auditoría
    auditoria = generar_auditoria(df)
    RUTA_AUDITORIA.parent.mkdir(parents=True, exist_ok=True)
    RUTA_AUDITORIA.write_text(auditoria, encoding="utf-8")
    print(f"Auditoría -> {RUTA_AUDITORIA}")

    # Resumen de gaps
    temporadas_sin_datos = [t for t in TEMPORADAS_ESPERADAS if t not in df["temporada"].values]
    print(f"\nTemporadas sin datos: {temporadas_sin_datos}")
    sin_eliminatorias = [
        t for t in TEMPORADAS_ESPERADAS
        if t in df["temporada"].values
        and len(df[(df["temporada"] == t) & (df["fase"] != "Grupos")]) == 0
    ]
    print(f"Temporadas sin eliminatorias: {sin_eliminatorias}")


if __name__ == "__main__":
    main()