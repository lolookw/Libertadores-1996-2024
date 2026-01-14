import pandas as pd


RUTA_DATOS = "datos/crudos/ejemplo_partidos_mock.csv"


def cargar_datos(ruta):
    return pd.read_csv(ruta)


def chequear_duplicados(df):
    columnas_clave = ["temporada", "fecha", "equipo_local", "equipo_visitante"]
    duplicados = df[df.duplicated(subset=columnas_clave, keep=False)]
    return duplicados


def chequear_rango_temporada(df, min_anio=1996, max_anio=2024):
    fuera_rango = df[
        (df["temporada"] < min_anio) | (df["temporada"] > max_anio)
    ]
    return fuera_rango


def chequear_goles_invalidos(df):
    goles_invalidos = df[
        (df["goles_local"] < 0) | (df["goles_visitante"] < 0)
    ]
    return goles_invalidos


def chequear_resultado_inconsistente(df):
    condicion_l = (df["goles_local"] > df["goles_visitante"]) & (df["resultado"] != "L")
    condicion_v = (df["goles_local"] < df["goles_visitante"]) & (df["resultado"] != "V")
    condicion_e = (df["goles_local"] == df["goles_visitante"]) & (df["resultado"] != "E")

    inconsistentes = df[condicion_l | condicion_v | condicion_e]
    return inconsistentes


def chequear_cobertura_temporal(df, min_anio=1996, max_anio=2024):
    temporadas_presentes = set(df["temporada"].unique())
    temporadas_esperadas = set(range(min_anio, max_anio + 1))
    faltantes = sorted(temporadas_esperadas - temporadas_presentes)
    return faltantes

def normalizar_resultado(df):
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

def chequear_resultado_inconsistente(df):
    # Si resultado_norm queda vacío (NaN), ya es inválido.
    invalidos = df[df["resultado_norm"].isna()]

    condicion_l = (df["goles_local"] > df["goles_visitante"]) & (df["resultado_norm"] != "L")
    condicion_v = (df["goles_local"] < df["goles_visitante"]) & (df["resultado_norm"] != "V")
    condicion_e = (df["goles_local"] == df["goles_visitante"]) & (df["resultado_norm"] != "E")

    inconsistentes = df[condicion_l | condicion_v | condicion_e]
    return invalidos, inconsistentes


def main():
    df = cargar_datos(RUTA_DATOS)
    df = normalizar_resultado(df)

    print("=== QA DATASET LIBERTADORES (MOCK) ===\n")
    print(f"Total de filas: {len(df)}\n")

    duplicados = chequear_duplicados(df)
    print(f"Duplicados detectados: {len(duplicados)}")

    fuera_rango = chequear_rango_temporada(df)
    print(f"Temporadas fuera de rango: {len(fuera_rango)}")

    goles_invalidos = chequear_goles_invalidos(df)
    print(f"Goles inválidos: {len(goles_invalidos)}")

    faltantes = chequear_cobertura_temporal(df)
    print(f"Temporadas faltantes: {len(faltantes)}")
    if faltantes:
        print("Años faltantes:", faltantes)

    invalidos_res, inconsistentes = chequear_resultado_inconsistente(df)
    print(f"Resultado inválido (valores fuera de Local/Visitante/Empate o L/V/E): {len(invalidos_res)}")
    print(f"Resultados inconsistentes: {len(inconsistentes)}")

    print("\n=== FIN QA ===")


if __name__ == "__main__":
    main()
