from pathlib import Path
import pandas as pd
import unicodedata
import re

RUTA_ENTRADA = Path("datos/procesados/partidos_rsssf1_validos_normalizado.csv")
RUTA_ALIAS = Path("datos/referencias/equipos_alias.csv")
RUTA_SALIDA = Path("datos/procesados/partidos_rsssf1_validos_normalizado.csv")  # pisa, cambiá si querés
RUTA_REPORTE = Path("reportes/referencias/alias_no_aplicados.csv")

def norm(s: str) -> str:
    s = "" if s is None else str(s)
    s = s.replace("\u00a0", " ")
    s = unicodedata.normalize("NFKC", s)
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s

def main():
    df = pd.read_csv(RUTA_ENTRADA, dtype=str)
    alias = pd.read_csv(RUTA_ALIAS, dtype=str).fillna("")

    # normalizar
    df["equipo_local"] = df["equipo_local"].apply(norm)
    df["equipo_visitante"] = df["equipo_visitante"].apply(norm)

    alias["equipo_alias"] = alias["equipo_alias"].apply(norm)
    alias["equipo_canonico"] = alias["equipo_canonico"].apply(norm)

    # claves normalizadas para merge
    alias = alias.drop_duplicates(subset=["equipo_alias"])
    mapa = alias.set_index("equipo_alias")["equipo_canonico"]

    # aplicar: si está en mapa, reemplazamos; si no, dejamos igual
    antes_local = df["equipo_local"].copy()
    antes_vis = df["equipo_visitante"].copy()

    df["equipo_local"] = df["equipo_local"].map(lambda x: mapa.get(x, x))
    df["equipo_visitante"] = df["equipo_visitante"].map(lambda x: mapa.get(x, x))

    # reporte: cuáles NO se tocaron pero podrían estar “casi”
    # (simple: los que no estaban en mapa)
    no_aplicados = sorted(set(pd.concat([antes_local, antes_vis])) - set(mapa.index))
    RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"equipo_no_en_alias": no_aplicados}).to_csv(RUTA_REPORTE, index=False, encoding="utf-8")

    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")
    print(f"OK -> {RUTA_SALIDA} | filas={len(df)} | alias={len(mapa)}")
    print(f"Reporte -> {RUTA_REPORTE}")

if __name__ == "__main__":
    main()
