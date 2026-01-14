from pathlib import Path
import pandas as pd

RUTA_PARTIDOS = Path("datos/procesados/partidos_rsssf1_validos_normalizado.csv")
RUTA_REF = Path("datos/referencias/equipos_referencia.csv")

RUTA_SALIDA = Path("datos/procesados/partidos_rsssf1_enriquecido.csv")
RUTA_REPORTE_FALTANTES = Path("reportes/referencias/equipos_sin_match.csv")


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def _rellenar_si_vacio(serie_base: pd.Series, serie_nueva: pd.Series) -> pd.Series:
    """
    Rellena base con nueva SOLO cuando base está vacío/NaN.
    Considera "" como vacío.
    """
    base = serie_base.copy()
    vacio = base.isna() | (base.astype(str).str.strip() == "")
    base.loc[vacio] = serie_nueva.loc[vacio]
    return base


def main():
    df = pd.read_csv(RUTA_PARTIDOS)
    ref = pd.read_csv(RUTA_REF)

    # normalizar columnas referencia
    ref = normalizar_columnas(ref)
    requeridas = {"equipo", "pais", "ciudad", "estadio_principal", "fuente_referencia", "notas"}
    faltan = requeridas - set(ref.columns)
    if faltan:
        raise ValueError(f"Faltan columnas en equipos_referencia.csv: {sorted(faltan)}")

    # limpiar claves
    df["equipo_local"] = df["equipo_local"].astype(str).str.strip()
    df["equipo_visitante"] = df["equipo_visitante"].astype(str).str.strip()
    ref["equipo"] = ref["equipo"].astype(str).str.strip()

    # armamos mapas rápidos
    mapa_pais = dict(zip(ref["equipo"], ref["pais"]))
    mapa_ciudad = dict(zip(ref["equipo"], ref["ciudad"]))
    mapa_estadio = dict(zip(ref["equipo"], ref["estadio_principal"]))

    # si no existían, las creamos
    for col in ["pais_local", "pais_visitante", "ciudad_sede", "estadio"]:
        if col not in df.columns:
            df[col] = ""

    # completar país local/visitante SOLO si está vacío
    df["pais_local"] = _rellenar_si_vacio(df["pais_local"], df["equipo_local"].map(mapa_pais))
    df["pais_visitante"] = _rellenar_si_vacio(df["pais_visitante"], df["equipo_visitante"].map(mapa_pais))

    # completar estadio/ciudad sede aproximada desde el local (SOLO si está vacío)
    df["estadio"] = _rellenar_si_vacio(df["estadio"], df["equipo_local"].map(mapa_estadio))
    df["ciudad_sede"] = _rellenar_si_vacio(df["ciudad_sede"], df["equipo_local"].map(mapa_ciudad))

    # (opcional) también país_sede si existe
    if "pais_sede" in df.columns:
        df["pais_sede"] = _rellenar_si_vacio(df["pais_sede"], df["pais_local"])

    # reporte de equipos sin match en referencia
    equipos = sorted(set(pd.concat([df["equipo_local"], df["equipo_visitante"]]).dropna().astype(str)))
    sin_match = [e for e in equipos if e not in mapa_pais]

    RUTA_REPORTE_FALTANTES.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"equipo_sin_match": sin_match}).to_csv(RUTA_REPORTE_FALTANTES, index=False, encoding="utf-8")

    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")

    print(f"OK -> {RUTA_SALIDA} | filas={len(df)} | equipos_sin_match={len(sin_match)}")
    print(f"Reporte -> {RUTA_REPORTE_FALTANTES}")


if __name__ == "__main__":
    main()
