import pandas as pd

df = pd.read_csv("datos/procesados/partidos_rsssf1_validos_normalizado.csv", dtype=str)
ref = pd.read_csv("datos/referencias/equipos_referencia.csv", dtype=str)

equipos = set(pd.concat([df["equipo_local"], df["equipo_visitante"]]).dropna())
canonicos = set(ref["equipo"].dropna())

sin_match = sorted(equipos - canonicos)
print("sin_match:", len(sin_match))
print("primeros:", sin_match[:20])

# si son 5, imprimimos detalle total
for e in sin_match:
    print("----")
    print("repr:", repr(e))
    print("codepoints:", [hex(ord(c)) for c in e])
