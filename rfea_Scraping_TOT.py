import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
url = "https://rfealive.me/Results/ResultsEvent?key=2025MUR66615%3ASG1%3ASG1%3A5%3A1&session=21%2F12%20Ma%C3%B1ana"

cat = "ABSF"              # <<< CATEGORÍA DE LA COMPETICIÓN
fecha = "21/12/25"       # <<< DD/MM/AA
competicion = "Alhama de Murcia" # <<< TÍTULO MANUAL SI NO LO DETECTA EL HTML
save_path = "/home/truji/Desktop/streamlit_app/bruto"

os.makedirs(save_path, exist_ok=True)

# Convertir fecha dd/mm/aa → YYYY-MM-DD
d, m, y = fecha.split("/")
y = "20" + y
fecha_ing = f"{y}-{m}-{d}"


# ------------------------------------------------------------
# OBTENER HTML
# ------------------------------------------------------------
resp = requests.get(url)
soup = BeautifulSoup(resp.text, "html.parser")

rows = soup.select("table tr")


# ------------------------------------------------------------
# USAR EL TÍTULO MANUAL DIRECTAMENTE
# ------------------------------------------------------------
titulo_evento = competicion
titulo_limpio = titulo_evento.replace(" ", "_").replace("/", "_")[:60]

print("➡️ Título asignado manualmente:", titulo_evento)


# ------------------------------------------------------------
# SCRAPER
# ------------------------------------------------------------
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
            categoria_html = cols[3].get_text(strip=True)
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
            "Categoría HTML": categoria_html,
            "Nacimiento": nacimiento,
            "Club": club,
            "Puntos Totales": puntos_totales,
            "cat": cat,               # ← NUESTRA CATEGORÍA
            "Competición": titulo_evento,
            "Fecha": fecha_ing
        }

        # Fila de pruebas
        if i + 1 < len(rows):
            detail_row = rows[i + 1]
            prueba_blocks = detail_row.select('div[style*="inline-grid"]')

            for block in prueba_blocks:
                prueba = block.find("small").get_text(strip=True)
                marcas = block.find_all("a", class_="erd_best")

                marca = marcas[0].get_text(strip=True) if len(marcas) > 0 else ""
                puntos = marcas[1].get_text(strip=True) if len(marcas) > 1 else ""

                athlete_data[f"{prueba} - Marca"] = marca
                athlete_data[f"{prueba} - Puntos"] = puntos

        athletes.append(athlete_data)
        i += 2

    else:
        i += 1


# ------------------------------------------------------------
# CREAR DATAFRAME Y GUARDAR
# ------------------------------------------------------------
df = pd.DataFrame(athletes)

# Nombre final del archivo
filename = f"{cat}_{fecha_ing}_{titulo_limpio}.csv"
filepath = os.path.join(save_path, filename)

df.to_csv(filepath, index=False, encoding="utf-8-sig")

print(df.head())
print("\n✔ Archivo generado:", filepath)
