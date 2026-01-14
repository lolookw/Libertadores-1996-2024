from pathlib import Path
import pandas as pd


RUTA_ENTRADA = Path("datos/crudos/partidos_rsssf_raw.csv")
RUTA_SALIDA = Path("datos/intermedios/partidos_rsssf.csv")


def resultado_desde_goles(gl: int, gv: int) -> str:
    if gl > gv:
        return "L"
    if gl < gv:
        return "V"
    return "E"


def fase_desde_etapa(etapa: str | None) -> str | None:
    if etapa is None:
        return None
    e = etapa.strip().lower()

    if e == "grupos":
        return "Grupos"
    if "second round" in e:
        return "Octavos"
    if "quarter" in e:
        return "Cuartos"
    if "semi" in e:
        return "Semifinal"
    if "final" == e or e.startswith("final"):
        return "Final"

    # fallback: guardamos el texto original
    return etapa


def main():
    df = pd.read_csv(RUTA_ENTRADA)

    # columnas base v1
    df_v1 = pd.DataFrame()
    df_v1["temporada"] = df["temporada"].astype("int64")
    df_v1["competicion"] = "Copa Libertadores"
    df_v1["fase"] = df["etapa"].apply(fase_desde_etapa)

    # instancia: grupos -> Group X ; series -> Ida/Vuelta
    df_v1["instancia"] = df["instancia"]
    df_v1.loc[df["etapa"] == "Grupos", "instancia"] = df["grupo"]

    df_v1["fecha"] = df["fecha"]

    # sede (no disponible en RSSSF de forma consistente)
    df_v1["pais_sede"] = ""
    df_v1["ciudad_sede"] = ""
    df_v1["estadio"] = ""

    # equipos
    df_v1["equipo_local"] = df["equipo_local"]
    df_v1["equipo_visitante"] = df["equipo_visitante"]

    # países de equipos (no disponible en grupos; en series podríamos extraer país_3 si lo agregamos luego)
    df_v1["pais_local"] = ""
    df_v1["pais_visitante"] = ""

    # goles y resultado
    df_v1["goles_local"] = df["goles_local"].astype("int64")
    df_v1["goles_visitante"] = df["goles_visitante"].astype("int64")
    df_v1["resultado"] = [
        resultado_desde_goles(gl, gv)
        for gl, gv in zip(df_v1["goles_local"], df_v1["goles_visitante"])
    ]

    # metadata
    df_v1["fuente"] = df["fuente"]
    df_v1["url_fuente"] = ""  # opcional: luego lo llenamos
    df_v1["id_partido_fuente"] = ""
    df_v1["observaciones"] = ""
    # opcional: guardamos agregado en observaciones para no perderlo
    df_v1.loc[df["agregado_texto"].notna(), "observaciones"] = "agregado=" + df["agregado_texto"].astype(str)

    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df_v1.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")
    print(f"OK -> {RUTA_SALIDA} | filas={len(df_v1)}")


if __name__ == "__main__":
    main()
