import streamlit as st
import pandas as pd
import os

# ==============================================================
# CONFIG STREAMLIT
# ==============================================================
st.set_page_config(page_title="Combinadas Viewer", page_icon="🏅", layout="wide")

st.title("🏅 Visualizador de Competición – Archivos locales")

DATA_DIR = "/home/truji/Desktop/streamlit_app/limpio"

# ==============================================================
# SIDEBAR: Seleccionar archivo
# ==============================================================
st.sidebar.title("📁 Selección de archivo")

# Aceptar XLSX y CSV
files = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx") or f.endswith(".csv")]

if not files:
    st.sidebar.error("❌ No hay archivos .xlsx o .csv en la carpeta.")
    st.stop()

selected_file = st.sidebar.selectbox("Selecciona archivo:", files)

full_path = os.path.join(DATA_DIR, selected_file)

st.success(f"Archivo seleccionado: **{selected_file}**")

# ==============================================================
# Cargar el archivo seleccionado
# ==============================================================
try:
    if selected_file.endswith(".csv"):
        # ====================================
        #   CARGAR CSV
        # ====================================
        st.subheader(f"📄 Mostrando CSV: {selected_file}")
        df = pd.read_csv(full_path, encoding="utf-8", sep=",")
        st.dataframe(df, use_container_width=True)

    else:
        # ====================================
        #   CARGAR EXCEL
        # ====================================
        xls = pd.ExcelFile(full_path)

        # Selector de hoja (solo para Excel)
        sheet = st.sidebar.selectbox("Selecciona hoja:", xls.sheet_names)

        st.subheader(f"📄 Mostrando: {selected_file} → {sheet}")

        df = pd.read_excel(full_path, sheet_name=sheet)
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error al leer el archivo: {e}")
