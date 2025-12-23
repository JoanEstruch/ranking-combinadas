import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://rfealive.me/Results/ResultsEvent?key=2025CAT66308%3AGF2%3AGF2%3A5%3A1&session=23%2F11%20Ma%C3%B1ana"

cat = "U16H"
lugar = "Cornellà"
tipo = "AL"
fecha = "23/11/25"

titulo_corto = f"Hexatló {cat} Hombres"


resp = requests.get(url)
soup = BeautifulSoup(resp.text, "html.parser")

rows = soup.select("table tr")

athletes = []   # lista final

i = 0
while i < len(rows):
    row = rows[i]
    cols = row.find_all("td")

    # --- Detectar fila de datos personales ---
    if len(cols) >= 9 and "tb-date" in cols[0].get("class", []):
        # Datos personales
        try:
            posicion = cols[0].get_text(strip=True)
            dorsal = cols[1].get_text(strip=True)
            nombre = cols[2].select_one("h5").get_text(strip=True)
            licencia = cols[2].select_one("p").get_text(strip=True)
            categoria = cols[3].get_text(strip=True)
            nacimiento = cols[4].get_text(strip=True)
            club = cols[5].get_text(strip=True)
            puntos_totales = cols[7].get_text(strip=True)
            puesto_final = cols[8].get_text(strip=True)
        except:
            i += 1
            continue

        # Crear plantilla del atleta
        athlete_data = {
            "Posición": posicion,
            "Dorsal": dorsal,
            "Nombre": nombre,
            "Licencia": licencia,
            "Categoría": categoria,
            "Nacimiento": nacimiento,
            "Club": club,
            "Puntos Totales": puntos_totales,
            "Puesto Final": puesto_final
        }

        # --- La siguiente fila contiene las pruebas ---
        if i + 1 < len(rows):
            detail_row = rows[i + 1]
            prueba_blocks = detail_row.select('div[style*="inline-grid"]')

            for block in prueba_blocks:
                prueba = block.find("small").get_text(strip=True)

                marcas = block.find_all("a", class_="erd_best")
                marca = marcas[0].get_text(strip=True) if len(marcas) > 0 else ""
                puntos = marcas[1].get_text(strip=True) if len(marcas) > 1 else ""

                # Crear nombres de columnas automáticos
                col_marca = f"{prueba} - Marca"
                col_puntos = f"{prueba} - Puntos"

                athlete_data[col_marca] = marca
                athlete_data[col_puntos] = puntos

        athletes.append(athlete_data)

        i += 2  # saltamos la fila de pruebas
    else:
        i += 1


# Convertir a DataFrame
df = pd.DataFrame(athletes)

# Añadir columnas fijas automáticas
df["Lugar"] = lugar
df["Fecha"] = fecha
df["Tipo"] = tipo   # AL = Aire libre, PC = Pista cubierta
df["Categoría"] = cat  # opcional: si quieres mantenerla

# Eliminar columnas no deseadas
df = df.drop(columns=["Dorsal", "Puesto Final"], errors="ignore")

# Renombrar columnas añadiendo título corto
new_columns = {}
for col in df.columns:
    if " - Marca" in col or " - Puntos" in col:
        new_columns[col] = f"{titulo_corto} - {col}"
    else:
        new_columns[col] = col

df = df.rename(columns=new_columns)

# Guardar CSV INCLUYENDO la categoría en el nombre del archivo
df.to_csv(f"atletas_completo_{cat}.csv", index=False, encoding="utf-8-sig")

print(df.head())
print(f"Archivo generado: atletas_completo_{cat}.csv")




