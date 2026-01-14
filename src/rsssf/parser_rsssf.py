from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd


MESES = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

# ====== REGEX ======

# Partidos de grupos:
# "Mar 13: Minervén - Caracas F.C.                4-2"
RE_PARTIDO_GRUPOS = re.compile(
    r"^(?P<mes>[A-Za-z]{3})\s+(?P<dia>\d{1,2})\:\s+"
    r"(?P<local>.+?)\s+\-\s+(?P<visitante>.+?)\s+"
    r"(?P<goles_local>\d+)\-(?P<goles_visitante>\d+)\s*$"
)

# "Group 5" o "Group 5 [Argentina, Venezuela]"
RE_GRUPO = re.compile(r"^Group\s+(?P<grupo>\d+).*$")

# Tabla de posiciones: " 1.River Plate ... 14- 3 14"
RE_TABLA = re.compile(r"^\s*\d+\.\s*.+\s+\d+\s+\d+\s+\d+\s+\d+\s+.+$")

# Header de eliminatorias en una línea:
# "Second Round (May 1 & 8)"
RE_FASE_CON_FECHAS = re.compile(
    r"^(?P<fase>.+?)\s*\((?P<mes>[A-Za-z]{3})\s+(?P<dia_ida>\d{1,2})\s*&\s*(?P<dia_vuelta>\d{1,2})\)\s*$"
)

# Header de fase sola (para el caso "Second Round" + línea siguiente "(Apr 16 & 22)")
RE_FASE_SOLA = re.compile(r"^(Second Round|Quarter-Finals|Semifinals|Final|First Round)\s*$", re.IGNORECASE)

# Línea que SOLO trae fechas:
# "(Apr 16 & 22)" o "(May 8 & 15)"
RE_SOLO_FECHAS = re.compile(
    r"^\((?P<mes>[A-Za-z]{3})\s+(?P<dia_ida>\d{1,2})\s*&\s*(?P<dia_vuelta>\d{1,2})\)\s*$"
)

# Token de país tipo RSSSF: Arg, Bra, Ecu, Uru, etc.
RE_PAIS_3 = re.compile(r"^[A-Z][a-z]{2}$")

# Marcador: "1-0" o "2-4p"
RE_MARCADOR = re.compile(r"^\d+\-\d+(p)?$")


# ====== DATA ======

@dataclass
class PartidoCrudo:
    temporada: int
    etapa: str | None           # ej: "Second Round"
    grupo: str | None           # ej: "Group 5" (solo para grupos)
    instancia: str | None       # ej: "Ida"/"Vuelta" (solo para series)
    fecha: str | None           # YYYY-MM-DD
    equipo_local: str
    equipo_visitante: str
    goles_local: int
    goles_visitante: int
    agregado_texto: str | None  # ej: "2-2"
    fuente: str
    archivo_fuente: str
    linea_partido: str


def _fecha_iso(temporada: int, mes_3: str, dia: int) -> str | None:
    mes_3 = mes_3.strip()
    if mes_3 not in MESES:
        return None
    mes = MESES[mes_3]
    return f"{temporada:04d}-{mes:02d}-{dia:02d}"


def _extraer_tokens_serie(linea: str):
    """
    Parsea una línea tipo:
    "San José Bol Barcelona Ecu 1-0 1-2 2-2 2-4p"
    o
    "San Lorenzo de Almagro Arg Cruzeiro (Belo Horizonte) Bra 1-0 1-1 2-1"
    Devuelve: equipoA, paisA, equipoB, paisB, ida, vuelta, agregado (penales ignorado).
    """
    tokens = linea.strip().split()
    if len(tokens) < 8:
        return None

    # identificar el tramo final de marcadores: buscamos desde el final tokens tipo marcador
    marcadores = []
    k = len(tokens) - 1
    while k >= 0 and RE_MARCADOR.match(tokens[k]):
        marcadores.append(tokens[k])
        k -= 1
    marcadores = list(reversed(marcadores))

    # necesitamos al menos 3: ida, vuelta, agregado (penales puede estar como 4to)
    if len(marcadores) < 3:
        return None

    ida = marcadores[0]
    vuelta = marcadores[1]
    agregado = marcadores[2]  # lo guardamos
    # si hay marcadores[3] con "p", lo ignoramos

    # parte "texto" antes de los marcadores
    texto_tokens = tokens[: len(tokens) - len(marcadores)]

    # encontrar 2 códigos de país (3 letras) dentro de texto_tokens
    idx_paises = [i for i, t in enumerate(texto_tokens) if RE_PAIS_3.match(t)]
    if len(idx_paises) < 2:
        return None

    idx_pais_a = idx_paises[0]
    idx_pais_b = idx_paises[1]

    equipo_a = " ".join(texto_tokens[:idx_pais_a]).strip()
    pais_a = texto_tokens[idx_pais_a].strip()
    equipo_b = " ".join(texto_tokens[idx_pais_a + 1: idx_pais_b]).strip()
    pais_b = texto_tokens[idx_pais_b].strip()

    if not equipo_a or not equipo_b:
        return None

    return equipo_a, pais_a, equipo_b, pais_b, ida, vuelta, agregado


def parsear_archivo_rsssf(ruta_txt: Path, temporada: int, fuente: str = "RSSSF") -> list[PartidoCrudo]:
    partidos: list[PartidoCrudo] = []

    grupo_actual: str | None = None

    # estado de eliminatorias
    fase_actual: str | None = None
    mes_ida: str | None = None
    dia_ida: int | None = None
    dia_vuelta: int | None = None

    lineas = ruta_txt.read_text(encoding="utf-8", errors="replace").splitlines()

    i = 0
    while i < len(lineas):
        linea = lineas[i].rstrip()

        if not linea.strip():
            i += 1
            continue

        # ignorar tabla
        if RE_TABLA.match(linea):
            i += 1
            continue

        # grupo
        m_grupo = RE_GRUPO.match(linea.strip())
        if m_grupo:
            grupo_actual = f"Group {m_grupo.group('grupo')}"
            i += 1
            continue

        # header eliminatorias en una línea: "Second Round (May 1 & 8)"
        m_fase_fechas = RE_FASE_CON_FECHAS.match(linea.strip())
        if m_fase_fechas:
            fase_actual = m_fase_fechas.group("fase").strip()
            mes_ida = m_fase_fechas.group("mes").strip()
            dia_ida = int(m_fase_fechas.group("dia_ida"))
            dia_vuelta = int(m_fase_fechas.group("dia_vuelta"))
            grupo_actual = None  # salimos de grupos
            i += 1
            continue

        # header fase sola (dos líneas)
        m_fase_sola = RE_FASE_SOLA.match(linea.strip())
        if m_fase_sola:
            fase_actual = linea.strip()
            # si la siguiente línea es "(Apr 16 & 22)", la consumimos
            if i + 1 < len(lineas):
                prox = lineas[i + 1].strip()
                m_solo_fechas = RE_SOLO_FECHAS.match(prox)
                if m_solo_fechas:
                    mes_ida = m_solo_fechas.group("mes").strip()
                    dia_ida = int(m_solo_fechas.group("dia_ida"))
                    dia_vuelta = int(m_solo_fechas.group("dia_vuelta"))
                    grupo_actual = None
                    i += 2
                    continue
            i += 1
            continue

        # línea solo-fechas dentro de una fase: "(May 8 & 15)"
        m_solo_fechas = RE_SOLO_FECHAS.match(linea.strip())
        if m_solo_fechas and fase_actual:
            mes_ida = m_solo_fechas.group("mes").strip()
            dia_ida = int(m_solo_fechas.group("dia_ida"))
            dia_vuelta = int(m_solo_fechas.group("dia_vuelta"))
            i += 1
            continue

        # partido de grupos
        m_pg = RE_PARTIDO_GRUPOS.match(linea.strip())
        if m_pg:
            mes = m_pg.group("mes")
            dia = int(m_pg.group("dia"))
            local = m_pg.group("local").strip()
            visitante = m_pg.group("visitante").strip()
            gl = int(m_pg.group("goles_local"))
            gv = int(m_pg.group("goles_visitante"))

            fecha = _fecha_iso(temporada, mes, dia)

            partidos.append(
                PartidoCrudo(
                    temporada=temporada,
                    etapa="Grupos",
                    grupo=grupo_actual,
                    instancia=None,
                    fecha=fecha,
                    equipo_local=local,
                    equipo_visitante=visitante,
                    goles_local=gl,
                    goles_visitante=gv,
                    agregado_texto=None,
                    fuente=fuente,
                    archivo_fuente=ruta_txt.name,
                    linea_partido=linea.strip(),
                )
            )
            i += 1
            continue

        # línea de serie (eliminatorias)
        # Solo intentamos parsearla si tenemos fase + fechas cargadas
        if fase_actual and mes_ida and dia_ida and dia_vuelta:
            serie = _extraer_tokens_serie(linea)
            if serie:
                equipo_a, pais_a, equipo_b, pais_b, ida, vuelta, agregado = serie

                # ida y vuelta están expresadas desde el punto de vista del primer equipo (equipo_a)
                gl_ida, gv_ida = [int(x) for x in ida.replace("p", "").split("-")]
                gl_vta, gv_vta = [int(x) for x in vuelta.replace("p", "").split("-")]

                fecha_ida_iso = _fecha_iso(temporada, mes_ida, dia_ida)
                fecha_vta_iso = _fecha_iso(temporada, mes_ida, dia_vuelta)

                partidos.append(
                    PartidoCrudo(
                        temporada=temporada,
                        etapa=fase_actual,
                        grupo=None,
                        instancia="Ida",
                        fecha=fecha_ida_iso,
                        equipo_local=equipo_a,
                        equipo_visitante=equipo_b,
                        goles_local=gl_ida,
                        goles_visitante=gv_ida,
                        agregado_texto=agregado,
                        fuente=fuente,
                        archivo_fuente=ruta_txt.name,
                        linea_partido=linea.strip(),
                    )
                )
                partidos.append(
                    PartidoCrudo(
                        temporada=temporada,
                        etapa=fase_actual,
                        grupo=None,
                        instancia="Vuelta",
                        fecha=fecha_vta_iso,
                        equipo_local=equipo_b,
                        equipo_visitante=equipo_a,
                        goles_local=gv_vta,   # ojo: invertimos porque ahora local=equipo_b
                        goles_visitante=gl_vta,
                        agregado_texto=agregado,
                        fuente=fuente,
                        archivo_fuente=ruta_txt.name,
                        linea_partido=linea.strip(),
                    )
                )

                i += 1
                continue

        # si no matchea nada, seguimos
        i += 1

    return partidos


def exportar_csv_crudo(partidos: list[PartidoCrudo], ruta_salida: Path) -> None:
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([asdict(p) for p in partidos])
    df.to_csv(ruta_salida, index=False, encoding="utf-8")


def main():
    carpeta = Path("datos/rsssf")
    salida = Path("datos/crudos/partidos_rsssf_raw.csv")

    partidos_total: list[PartidoCrudo] = []

    for ruta in sorted(carpeta.glob("*.txt")):
        try:
            temporada = int(ruta.stem)
        except ValueError:
            raise ValueError(f"El archivo {ruta.name} debe llamarse como el año, ej: 1996.txt")

        partidos = parsear_archivo_rsssf(ruta, temporada=temporada)
        partidos_total.extend(partidos)

    exportar_csv_crudo(partidos_total, salida)
    print(f"OK -> {salida} | partidos={len(partidos_total)} | archivos={len(list(carpeta.glob('*.txt')))}")


if __name__ == "__main__":
    main()
