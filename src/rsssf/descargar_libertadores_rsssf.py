import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.rsssf.org/sacups/"

OUT_DIR = Path("libertadores_rsssf_txt")
OUT_DIR = Path("datos/rsssf")

def build_url_for_year(year: int) -> str:
    """
    Construye la URL del año usando la convención de nombres:
    - 1996–2009: copaXX.html, con XX = últimos 2 dígitos
    - 2010–2024: copa20XX.html
    """
    if 1996 <= year <= 2009:
        # últimos dos dígitos, con cero a la izquierda si hace falta
        suffix = f"{year % 100:02d}"
        filename = f"copa{suffix}.html"
    elif 2010 <= year <= 2024:
        filename = f"copa{year}.html"
    else:
        raise ValueError(f"Año fuera de rango: {year}")

    return BASE_URL + filename


def scrape_year(year: int):
    url = build_url_for_year(year)
    print(f"Descargando {year} desde {url} ...")

    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} para {year} ({url})")

    # RSSSF suele estar en latin-1
    if resp.encoding is None:
        resp.encoding = "latin-1"

    soup = BeautifulSoup(resp.text, "html.parser")

    parts = []

    # Título principal (Copa Libertadores de América XXXX), si está
    h2 = soup.find("h2")
    if h2:
        parts.append(h2.get_text(strip=True))
        parts.append("")

    # Uno o varios bloques <pre> (partidos, tablas, etc.)
    pres = soup.find_all("pre")
    if not pres:
        raise RuntimeError(f"No encontré ningún <pre> para {year} ({url})")

    for pre in pres:
        parts.append(pre.get_text("\n", strip=False))

    text = "\n".join(parts)

    out_path = OUT_DIR / f"{year}.txt"
    out_path.write_text(text, encoding="utf-8")
    print(f"OK -> {out_path} ({len(text)} caracteres)")


def main():
    for year in range(1996, 2025):
        try:
            scrape_year(year)
            # pequeña pausa para no matar al server
            time.sleep(1)
        except Exception as e:
            print(f"ERROR en {year}: {e}")


if __name__ == "__main__":
    main()
