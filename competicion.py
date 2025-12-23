import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# ============================================================
# CONFIGURACIÓN PRINCIPAL
# ============================================================

schedule_url = "https://rfealive.me/Results/Schedule?chid=2025CVA66334&session=23%2F11%20Ma%C3%B1ana"

lugar = "VLC - Turia"
fecha = "23/11/25"
tipo = "AL"  # AL = aire libre, PC = pista cubierta

# === Carpeta LOCAL donde guardar el Excel ===
base_path = "/home/truji/Desktop/streamlit_app"
os.makedirs(base_path, exist_ok=True)

# Convertir fecha dd/mm/aa → YYYY-MM-DD
d, m, y = fecha.split("/")
y = "20" + y
fecha_ing = f"{y}-{m}-{d}"


# ============================================================
# EXTRAER TÍTULO OFICIAL DEL EVENTO
# ============================================================

resp_title = requests.get(schedule_url)
soup_title = BeautifulSoup(resp_title.text, "html.parser")

titulo_evento = "Sin_Titulo"

h2 = soup_title.find("h2")
h1 = soup_title.find("h1")

if h2:
    titulo_evento = h2.get_text(strip=True)
elif h1:
    titulo_evento = h1.get_text(strip=True)

print("Título oficial detectado:", titulo_evento)

titulo_limpio = titulo_evento.replace(" ", "_")[:40]


# ============================================================
# FUNCIÓN SCRAPER DE UNA CATEGORÍA
# ============================================================

def scrape_event(url, titulo_corto, categoria, lugar, fecha_ing, tipo, titulo_evento):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = soup.select("table tr")
    athletes = []
    i = 0

    while i < len(rows):
        row = rows[i]
        cols = row.find_all("td")

        if len(cols) >= 9 and "tb-date" in cols[0].get("class", []):
            try:
                posicion = cols[0].get_text(strip=True)
                nombre = cols[2].select_one("h5").get_text(strip=True)
                licencia = cols[2].select_one("p").get_text(strip=True)
                cat_html = cols[3].get_text(strip=True)
                nacimiento = cols[4].get_text(strip=True)
                club = cols[5].get_text(strip=True)
                puntos_totales = cols[7].get_text(strip=True)
            except:
                i += 1
                continue

            athlete_data = {
                "Posición": posicion,
                "Nombre": nombre,
                "Licencia": licencia,
                "Categoría HTML": cat_html,
                "Nacimiento": nacimiento,
                "Club": club,
                "Puntos Totales": puntos_totales,
            }

            if i + 1 < len(rows):
                detail_row = rows[i + 1]
                prueba_blocks = detail_row.select('div[style*="inline-grid"]')

                for block in prueba_blocks:
                    prueba = block.find("small").get_text(strip=True)
                    marcas = block.find_all("a", class_="erd_best")

                    marca = marcas[0].get_text(strip=True) if len(marcas) > 0 else ""
                    puntos = marcas[1].get_text(strip=True) if len(marcas) > 1 else ""

                    col_marca = f"{prueba} - Marca"
                    col_puntos = f"{prueba} - Puntos"

                    athlete_data[col_marca] = marca
                    athlete_data[col_puntos] = puntos

            athletes.append(athlete_data)
            i += 2

        else:
            i += 1

    df = pd.DataFrame(athletes)

    # Añadir info fija
    df["Lugar"] = lugar
    df["Fecha"] = fecha_ing
    df["Tipo"] = tipo
    df["Viento Legal"] = ""
    df["Competición"] = titulo_evento

    return df


# ============================================================
# DETECTAR SOLO LAS COMBINADAS COMPLETAS
# ============================================================

resp = requests.get(schedule_url)
soup = BeautifulSoup(resp.text, "html.parser")

event_links = []

keys = [
    "hexatló", "heptatló", "pentatló", "decatló",
    "hexatlón", "heptatlón", "pentatlón", "decatlón",
    "pentathlon", "heptathlon"
]

for a in soup.find_all("a"):
    href = a.get("href", "")
    nombre = a.get_text(strip=True)
    nombre_l = nombre.lower()

    if "ResultsEvent" in href:
        es_combinada = any(k in nombre_l for k in keys)
        es_final = href.endswith("5%3A1")

        if es_combinada and es_final:
            url = "https://rfealive.me" + href
            event_links.append((nombre, url))

print("\n=== CATEGORÍAS DETECTADAS ===")
for n, u in event_links:
    print(n, "-->", u)


# ============================================================
# EXTRAER CATEGORÍA LIMPIA
# ============================================================

def extraer_categoria(nombre):
    tokens = nombre.upper().split()
    categorias_estandar = ["SUB14","SUB16","SUB18","SUB20","SUB23","ABSOLUTO"]

    for t in tokens:
        if t in categorias_estandar:
            return t

    return "DESCONOCIDA"


# ============================================================
# PROCESAR TODAS LAS CATEGORÍAS Y GUARDAR EN UN EXCEL
# ============================================================

dfs = {}

for nombre, url in event_links:
    categoria = extraer_categoria(nombre)
    print(f"\nProcesando categoría: {nombre}")

    df = scrape_event(url, nombre, categoria, lugar, fecha_ing, tipo, titulo_evento)
    dfs[nombre] = df


# ============================================================
# GUARDAR UN SOLO ARCHIVO EXCEL POR COMPETICIÓN
# ============================================================

categorias_detectadas = sorted(set([extraer_categoria(n) for n, _ in event_links]))
categorias_text = "-".join(categorias_detectadas)

excel_name = f"{fecha_ing}_{titulo_limpio}_{lugar.replace(' ', '_')}_{categorias_text}.xlsx"
excel_path = os.path.join(base_path, excel_name)

with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    for nombre, df in dfs.items():
        sheet = nombre.replace(" ", "_")[:31]
        df.to_excel(writer, sheet_name=sheet, index=False)

print(f"\n✔ Archivo generado: {excel_path}")
