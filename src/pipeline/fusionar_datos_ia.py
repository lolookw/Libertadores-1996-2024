"""
fusionar_datos_ia.py
=====================
Fusiona filas generadas por IA (o cualquier fuente externa) con el dataset enhanced.
El CSV de entrada debe tener las mismas 21 columnas que partidos_rsssf1_enhanced.csv.

Uso:
    python src/pipeline/fusionar_datos_ia.py datos/externos/completado_ia_2011.csv

El script:
  1. Valida que las columnas coincidan.
  2. Detecta y reporta duplicados entre el nuevo CSV y el existente.
  3. Aplica mini-QA: resultado consistente con goles, fechas válidas, temporada en rango.
  4. Concatena y exporta un nuevo partidos_rsssf1_enhanced.csv.
"""

from pathlib import Path
import pandas as pd
import sys


RUTA_BASE = Path("datos/procesados/partidos_rsssf1_enhanced.csv")
RUTA_SALIDA = Path("datos/procesados/partidos_rsssf1_enhanced.csv")

COLUMNAS_ESPERADAS = [
    "temporada", "competicion", "fase", "instancia", "fecha",
    "pais_sede", "ciudad_sede", "estadio",
    "equipo_local", "equipo_visitante", "pais_local", "pais_visitante",
    "goles_local", "goles_visitante", "resultado",
    "fuente", "url_fuente", "id_partido_fuente", "observaciones",
    "resultado_norm", "fecha_parseada",
]


def resultado_esperado(gl: int, gv: int) -> str:
    if gl > gv:
        return "L"
    if gl < gv:
        return "V"
    return "E"


def validar_nuevo_csv(df_nuevo: pd.DataFrame) -> list[str]:
    errores = []
    faltantes = [c for c in COLUMNAS_ESPERADAS if c not in df_nuevo.columns]
    if faltantes:
        errores.append(f"Columnas faltantes: {faltantes}")
        return errores

    for i, row in df_nuevo.iterrows():
        try:
            gl = int(row["goles_local"])
            gv = int(row["goles_visitante"])
            esperado = resultado_esperado(gl, gv)
            if str(row["resultado"]).strip() != esperado:
                errores.append(
                    f"Fila {i}: resultado '{row['resultado']}' inconsistente con goles {gl}-{gv} (esperado '{esperado}')"
                )
        except (ValueError, TypeError):
            errores.append(f"Fila {i}: goles no numéricos")

        try:
            pd.to_datetime(str(row["fecha"]))
        except Exception:
            errores.append(f"Fila {i}: fecha '{row['fecha']}' inválida")

        try:
            t = int(row["temporada"])
            if not (1996 <= t <= 2024):
                errores.append(f"Fila {i}: temporada {t} fuera de rango 1996-2024")
        except (ValueError, TypeError):
            errores.append(f"Fila {i}: temporada no válida")

    return errores


def main():
    if len(sys.argv) < 2:
        print("Uso: python src/pipeline/fusionar_datos_ia.py <ruta_csv_nuevo>")
        sys.exit(1)

    ruta_nuevo = Path(sys.argv[1])
    if not ruta_nuevo.exists():
        print(f"ERROR: no existe {ruta_nuevo}")
        sys.exit(1)

    if not RUTA_BASE.exists():
        print(f"ERROR: no existe {RUTA_BASE}. Correr el pipeline primero.")
        sys.exit(1)

    df_base = pd.read_csv(RUTA_BASE)
    df_nuevo = pd.read_csv(ruta_nuevo)

    print(f"Base: {len(df_base)} filas")
    print(f"Nuevo: {len(df_nuevo)} filas")

    # Validación
    errores = validar_nuevo_csv(df_nuevo)
    if errores:
        print(f"\n❌ QA del CSV nuevo encontró {len(errores)} error(es):")
        for e in errores[:20]:
            print(f"  - {e}")
        if len(errores) > 20:
            print(f"  ... y {len(errores) - 20} más")
        print("\nCorregí los errores antes de fusionar.")
        sys.exit(1)

    # Corregir resultado_norm y fecha_parseada automáticamente
    df_nuevo["resultado_norm"] = df_nuevo["resultado"]
    df_nuevo["fecha_parseada"] = df_nuevo["fecha"]

    # Detectar duplicados
    clave = ["temporada", "fecha", "equipo_local", "equipo_visitante"]
    claves_base = set(
        df_base[clave].dropna().astype(str).agg("|".join, axis=1)
    )
    claves_nuevo = df_nuevo[clave].dropna().astype(str).agg("|".join, axis=1)
    duplicados = claves_nuevo[claves_nuevo.isin(claves_base)]
    if len(duplicados) > 0:
        print(f"\n⚠️  {len(duplicados)} filas del CSV nuevo ya existen en la base. Se omitirán.")
        df_nuevo = df_nuevo[~claves_nuevo.isin(claves_base)]

    # Asegurar columnas en el orden correcto
    for col in COLUMNAS_ESPERADAS:
        if col not in df_nuevo.columns:
            df_nuevo[col] = ""
    df_nuevo = df_nuevo[COLUMNAS_ESPERADAS]

    # Concatenar y ordenar
    df_resultado = pd.concat([df_base, df_nuevo], ignore_index=True)
    df_resultado = df_resultado.sort_values(["temporada", "fecha"]).reset_index(drop=True)

    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df_resultado.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")

    print(f"\nOK -> {RUTA_SALIDA}")
    print(f"Filas incorporadas: {len(df_nuevo)}")
    print(f"Total dataset: {len(df_resultado)}")


if __name__ == "__main__":
    main()