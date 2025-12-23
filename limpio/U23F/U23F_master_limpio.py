import pandas as pd

# ============================
# CONFIG
# ============================
input_file = "/home/truji/Desktop/streamlit_app/limpio/U23F/U23F.xlsx"
output_file = "/home/truji/Desktop/streamlit_app/limpio/U23F_master_limpio.csv"

# ============================
# 1) Cargar archivo
# ============================
df = pd.read_excel(input_file)

# ============================
# 2) Eliminar columna "Posición" si existe
# ============================
if "Posición" in df.columns:
    df = df.drop(columns=["Posición"])

# ============================
# 3) Eliminar columnas que contienen "Puntos"
#    excepto "Puntos Totales"
# ============================
cols_puntos = [
    c for c in df.columns
    if isinstance(c, str) and "Puntos" in c and c != "Puntos Totales"
]

df = df.drop(columns=cols_puntos, errors="ignore")

print("Columnas eliminadas:", cols_puntos + ["Posición"])

# ============================
# 4) Convertir puntos totales a número
# ============================
df["Puntos Totales"] = pd.to_numeric(df["Puntos Totales"], errors="coerce").fillna(0)

# ============================
# 5) Formatear FECHA → dd/mm/yyyy
# ============================
if "Fecha" in df.columns:
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce").dt.strftime("%d/%m/%Y")

# ============================
# 6) Formatear marcas con 2 decimales
# ============================
pruebas = ["60", "Longitud", "Peso", "Altura", "60mv"]

for col in pruebas:
    if col in df.columns:
        df[col] = (
            pd.to_numeric(df[col], errors="coerce")
            .map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
        )

# ============================
# 7) Ordenar por puntos totales DESC
# ============================
df = df.sort_values(by="Puntos Totales", ascending=False)

# ============================
# 8) Quedarse con los 24 mejores
# ============================
df_top24 = df.head(24).copy()

# ============================
# 9) Crear columna Ranking
# ============================
df_top24.insert(0, "Ranking", range(1, len(df_top24) + 1))

# ============================
# 10) Guardar archivo final
# ============================
df_top24.to_csv(output_file, index=False, encoding="utf-8-sig")

print("✔ Archivo final guardado en:", output_file)
print("✔ Atletas guardados:", len(df_top24))
print("✔ Columnas finales:", df_top24.columns.tolist())
