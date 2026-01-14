from pathlib import Path
import pandas as pd

RUTA_DATOS = Path("datos/procesados/partidos_rsssf1_validos.csv")
RUTA_SALIDA = Path("datos/referencias/equipos_referencia.csv")

def main():
    df = pd.read_csv(RUTA_DATOS)

    equipos = pd.concat([df["equipo_local"], df["equipo_visitante"]]).dropna().unique()
    equipos = sorted(set(e.strip() for e in equipos if str(e).strip()))

    # si ya existe, no pisamos lo que completaste
    if RUTA_SALIDA.exists():
        ref = pd.read_csv(RUTA_SALIDA)
        ya = set(ref["equipo"].astype(str))
    else:
        ref = pd.DataFrame(columns=["equipo","pais","ciudad","estadio_principal","fuente_referencia","notas"])
        ya = set()

    faltantes = [e for e in equipos if e not in ya]

    nuevos = pd.DataFrame({
        "equipo": faltantes,
        "pais": "",
        "ciudad": "",
        "estadio_principal": "",
        "fuente_referencia": "",
        "notas": ""
    })

    ref_final = pd.concat([ref, nuevos], ignore_index=True)
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    ref_final.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")

    print(f"OK -> {RUTA_SALIDA} | equipos_total={len(equipos)} | agregados={len(faltantes)}")

if __name__ == "__main__":
    main()
