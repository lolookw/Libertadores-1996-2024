from pathlib import Path
import pandas as pd


RUTA_DATOS = "datos/intermedios/partidos_rsssf.csv"
CARPETA_REPORTES_QA = Path("reportes/qa")
CARPETA_PROCESADOS = Path("datos/procesados")


COLUMNAS_OBLIGATORIAS = [
    "temporada", "competicion", "fase", "instancia", "fecha",
    "pais_sede", "ciudad_sede", "estadio",
    "equipo_local", "equipo_visitante", "pais_local", "pais_visitante",
    "goles_local", "goles_visitante", "resultado",
    "fuente", "url_fuente", "id_partido_fuente", "observaciones",
]


def cargar_datos(ruta: str) -> pd.DataFrame:
    return pd.read_csv(ruta)


def chequear_columnas_obligatorias(df: pd.DataFrame) -> list[str]:
    faltantes = [c for c in COLUMNAS_OBLIGATORIAS if c not in df.columns]
    return faltantes


def normalizar_resultado(df: pd.DataFrame) -> pd.DataFrame:
    mapeo = {
        "LOCAL": "L",
        "VISITANTE": "V",
        "EMPATE": "E",
        "L": "L",
        "V": "V",
        "E": "E",
    }
    df = df.copy()
    df["resultado_norm"] = (
        df["resultado"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map(mapeo)
    )
    return df


def parsear_fecha(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fecha_parseada"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df


def chequear_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    columnas_clave = ["temporada", "fecha", "equipo_local", "equipo_visitante"]
    return df[df.duplicated(subset=columnas_clave, keep=False)].copy()


def chequear_temporada_fuera_rango(df: pd.DataFrame, min_anio=1996, max_anio=2024) -> pd.DataFrame:
    return df[(df["temporada"] < min_anio) | (df["temporada"] > max_anio)].copy()


def chequear_goles_invalidos(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["goles_local"] < 0) | (df["goles_visitante"] < 0)].copy()


def chequear_resultado_invalido(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["resultado_norm"].isna()].copy()


def chequear_resultado_inconsistente(df: pd.DataFrame) -> pd.DataFrame:
    condicion_l = (df["goles_local"] > df["goles_visitante"]) & (df["resultado_norm"] != "L")
    condicion_v = (df["goles_local"] < df["goles_visitante"]) & (df["resultado_norm"] != "V")
    condicion_e = (df["goles_local"] == df["goles_visitante"]) & (df["resultado_norm"] != "E")
    return df[condicion_l | condicion_v | condicion_e].copy()


def chequear_fecha_invalida(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["fecha_parseada"].isna()].copy()


def escribir_reporte(nombre: str, df: pd.DataFrame) -> None:
    CARPETA_REPORTES_QA.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_REPORTES_QA / f"{nombre}.csv"
    df.to_csv(ruta, index=False)


def main():
    df = cargar_datos(RUTA_DATOS)

    # Errores críticos: columnas obligatorias
    faltantes = chequear_columnas_obligatorias(df)
    if faltantes:
        print("❌ QA CRÍTICO: faltan columnas obligatorias:", faltantes)
        print("Se detiene el pipeline. Corregí el CSV de entrada.")
        raise SystemExit(1)

    # Normalizaciones / parseos
    df = normalizar_resultado(df)
    df = parsear_fecha(df)

    # Chequeos
    duplicados = chequear_duplicados(df)
    temporada_fuera_rango = chequear_temporada_fuera_rango(df)
    goles_invalidos = chequear_goles_invalidos(df)
    fecha_invalida = chequear_fecha_invalida(df)
    resultado_invalido = chequear_resultado_invalido(df)
    resultado_inconsistente = chequear_resultado_inconsistente(df)

    # Reportes
    if len(duplicados) > 0:
        escribir_reporte("duplicados", duplicados)
    if len(temporada_fuera_rango) > 0:
        escribir_reporte("temporada_fuera_rango", temporada_fuera_rango)
    if len(goles_invalidos) > 0:
        escribir_reporte("goles_invalidos", goles_invalidos)
    if len(fecha_invalida) > 0:
        escribir_reporte("fecha_invalida", fecha_invalida)
    if len(resultado_invalido) > 0:
        escribir_reporte("resultado_invalido", resultado_invalido)
    if len(resultado_inconsistente) > 0:
        escribir_reporte("resultado_inconsistente", resultado_inconsistente)

    # Clasificación válidos/ inválidos
    # Una fila es inválida si aparece en cualquiera de estos conjuntos
    indices_invalidos = set()
    for dfi in [duplicados, temporada_fuera_rango, goles_invalidos, fecha_invalida, resultado_invalido, resultado_inconsistente]:
        indices_invalidos.update(dfi.index.tolist())

    df_invalidos = df.loc[sorted(indices_invalidos)].copy()
    df_validos = df.drop(index=sorted(indices_invalidos)).copy()

    CARPETA_PROCESADOS.mkdir(parents=True, exist_ok=True)
    df_validos.to_csv(CARPETA_PROCESADOS / "partidos_rsssf1_validos.csv", index=False)
    df_invalidos.to_csv(CARPETA_PROCESADOS / "partidos_rsssf1_invalidos.csv", index=False)

    # Resumen
    print("=== QA DATASET LIBERTADORES (MOCK) ===\n")
    print(f"Total de filas: {len(df)}")
    print(f"Filas válidas: {len(df_validos)}")
    print(f"Filas inválidas: {len(df_invalidos)}\n")

    print(f"Duplicados (reporte): {len(duplicados)}")
    print(f"Temporadas fuera de rango: {len(temporada_fuera_rango)}")
    print(f"Goles inválidos: {len(goles_invalidos)}")
    print(f"Fechas inválidas: {len(fecha_invalida)}")
    print(f"Resultado inválido: {len(resultado_invalido)}")
    print(f"Resultado inconsistente: {len(resultado_inconsistente)}")

    print("\nReportes QA en:", str(CARPETA_REPORTES_QA))
    print("Procesados en:", str(CARPETA_PROCESADOS))
    print("\n=== FIN QA ===")


if __name__ == "__main__":
    main()
