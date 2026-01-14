from pathlib import Path
import pandas as pd
import unicodedata
import re

RUTA_ENTRADA = Path("datos/procesados/partidos_rsssf1_validos_normalizado.csv")
RUTA_ALIAS = Path("datos/referencias/equipos_alias.csv")
RUTA_SALIDA = Path("datos/procesados/partidos_rsssf1_validos_normalizado.csv")  # pisa el mismo (o cambiá nombre)

def normalizar_nombre(s: str) -> str:
    s = "" if s is None else str(s)
    s = s.replace("\u00a0", " ")  # NBSP -> espacio normal
    s = unicodedata.normalize("NFKC", s)  # normaliza unicode
    s = s.strip()
    s = re.sub(r"\s+", " ", s)  # colapsa espacios
    return s

def main():
    df = pd.read_csv(RUTA_ENTRADA)

    alias = pd.read_csv(RUTA_ALIAS, dtype=str).fillna("")
    alias["equipo_alias"] = alias["equipo_alias"].apply(normalizar_nombre)
    alias["equipo_canonico"] = alias["equipo_canonico"].apply(normalizar_nombre)

    # Mapa alias -> canónico
    mapa = dict(zip(alias["equipo_alias"], alias["equipo_canonico"]))

    # Normalizar columnas equipos antes de reemplazar
    df["equipo_local"] = df["equipo_local"].apply(normalizar_nombre).replace(mapa)
    df["equipo_visitante"] = df["equipo_visitante"].apply(normalizar_nombre).replace(mapa)

    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")
    print(f"OK -> {RUTA_SALIDA} | filas={len(df)} | alias={len(mapa)}")

if __name__ == "__main__":
    main()
