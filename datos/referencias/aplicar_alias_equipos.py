from pathlib import Path
import pandas as pd

RUTA_ENTRADA = Path("datos/procesados/partidos_rsssf1_validos.csv")
RUTA_ALIAS = Path("datos/referencias/equipos_alias.csv")
RUTA_SALIDA = Path("datos/procesados/partidos_rsssf1_validos_normalizado.csv")

def main():
    df = pd.read_csv(RUTA_ENTRADA)

    if not RUTA_ALIAS.exists():
        raise FileNotFoundError(f"No existe {RUTA_ALIAS}. Crealo primero.")

    alias = pd.read_csv(RUTA_ALIAS).dropna()
    mapa = dict(zip(alias["equipo_alias"].astype(str).str.strip(),
                    alias["equipo_canonico"].astype(str).str.strip()))

    df["equipo_local"] = df["equipo_local"].astype(str).str.strip().replace(mapa)
    df["equipo_visitante"] = df["equipo_visitante"].astype(str).str.strip().replace(mapa)

    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")
    print(f"OK -> {RUTA_SALIDA} | filas={len(df)} | alias={len(mapa)}")

if __name__ == "__main__":
    main()
