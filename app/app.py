import streamlit as st
import pandas as pd
import os

# ==============================================================
# CONFIG STREAMLIT
# ==============================================================
st.set_page_config(
    page_title="Ranking Combinadas",
    page_icon="🏅",
    layout="wide"
)

# Ruta local (tu ordenador)
LOCAL_DIR = "/home/truji/Desktop/streamlit_app/limpio"

# Ruta servidor (GitHub / Streamlit Cloud)
CLOUD_DIR = "limpio"

# Elegir según dónde exista
if os.path.exists(LOCAL_DIR):
    DATA_DIR = LOCAL_DIR
else:
    DATA_DIR = CLOUD_DIR


# DATA_DIR = "limpio"
# DATA_DIR = "/home/truji/Desktop/streamlit_app/limpio" 

# ==============================================================
# MÍNIMAS POR CATEGORÍA (EDITA LIBREMENTE)
# ==============================================================
MINIMAS = {
    "U16M": {"mínima": 3550, "repesca": 3200},
    "U16F": {"mínima": 3100, "repesca": 2850},
    "U18M": {"mínima": 4350, "repesca": 4200},
    "U18F": {"mínima": 3275, "repesca": 3050},
    "U20M": {"mínima": 4500, "repesca": 4200},
    "U20F": {"mínima": 3200, "repesca": 2850},
    "U23M": {"mínima": 4800, "repesca": 4300},
    "U23F": {"mínima": 3200, "repesca": 3100},
    "ABSM": {"mínima": 5300, "repesca": 4700},
    "ABSF": {"mínima": 3800, "repesca": 3400},
}

# ==============================================================
# MENSAJES POR CATEGORÍA
# ==============================================================
MENSAJES = {
    "U16M": "5 atletas ya tienen la mínima directa realizada.",
    "U16F": "3 atletas están en zona de repesca.",
    "U18M": "",
    "U18F": "",
    "U20M": "",
    "U20F": "",
    "U23M": "",
    "U23F": "",
    "ABSM": "",
    "ABSF": ""
}

# ==============================================================
# SIDEBAR – NAVEGACIÓN
# ==============================================================
st.sidebar.title("📌 Navegación")

page = st.sidebar.radio(
    "Ir a:",
    ["🏠 Inicio", "📊 Ranking", "🏟️ Competiciones realizadas"]
)

# ==============================================================
# PÁGINA: INICIO
# ==============================================================
if page == "🏠 Inicio":

    st.title("🏅 Ranking Nacional – Pruebas Combinadas")

    st.markdown("""
    Bienvenido/a al **Ranking NO oficial de Pruebas Combinadas**.

    - 📊 Ranking actualizado según resultados oficiales
    - 🏟️ Competiciones válidas
    - 📈 Análisis por categoría

    Usa el menú lateral para navegar.
    """)

# ==============================================================
# PÁGINA: COMPETICIONES
# ==============================================================
elif page == "🏟️ Competiciones realizadas":

    st.header("🏟️ Competiciones válidas para el ranking")

    st.markdown("""
    ### 🏆 Temporada 2024–2025

    **Campeonato España U16 – Albacete**  
    **Control FACV – Valencia**  
    **Interterritorial – Madrid**
    """)

# ==============================================================
# PÁGINA: RANKING
# ==============================================================
elif page == "📊 Ranking":

    st.title("🏅 Ranking Nacional – Pruebas Combinadas")

    # ----------------------------------------------------------
    # DETECTAR ARCHIVOS
    # ----------------------------------------------------------
    all_files = [f for f in os.listdir(DATA_DIR) if f.endswith("_master_limpio.csv")]
    categorias = [f.replace("_master_limpio.csv", "") for f in all_files]

    ORDER = [
        "U16F", "U16M",
        "U18F", "U18M",
        "U20F", "U20M",
        "U23F", "U23M",
        "ABSF", "ABSM"
    ]
    categorias_ordenadas = [c for c in ORDER if c in categorias]

    st.sidebar.title("📁 Categoría")
    selected_cat = st.sidebar.radio("Elige categoría:", categorias_ordenadas)

    selected_file = f"{selected_cat}_master_limpio.csv"
    full_path = os.path.join(DATA_DIR, selected_file)

    # ----------------------------------------------------------
    # MOSTRAR MÍNIMAS
    # ----------------------------------------------------------
    if selected_cat in MINIMAS:
        mini = MINIMAS[selected_cat]["mínima"]
        repesca = MINIMAS[selected_cat]["repesca"]

        st.info(
            f"### 📌 Mínimas {selected_cat}\n"
            f"- **Directa:** {mini} puntos\n"
            f"- **Repesca:** {repesca} puntos"
        )

        mensaje = MENSAJES.get(selected_cat, "")
        if mensaje.strip():
            st.success(f"🔔 {mensaje}")

    # ----------------------------------------------------------
    # CARGAR ARCHIVO
    # ----------------------------------------------------------
    try:
        df = pd.read_csv(full_path, encoding="utf-8")

        st.subheader(f"📊 Ranking {selected_cat}")

        # Convertir puntos totales SOLO a enteros
        df["Puntos Totales"] = pd.to_numeric(df["Puntos Totales"], errors="coerce").fillna(0).astype(int)

        # --------------------------------------------
        # FORMATO: DECIMALES SOLO EN PRUEBAS TÉCNICAS
        # --------------------------------------------
        columnas_pruebas = [
            col for col in df.columns
            if col not in ["Ranking", "Puntos Totales", "Nombre", "Licencia",
                           "cat", "Nacimiento", "Club", "Competición", "Fecha Competición"]
        ]

        def format_decimal(valor):
            try:
                # Si es formato tiempo "m:ss.xx" → NO tocar
                if ":" in str(valor):
                    return valor
                return f"{float(valor):.2f}"
            except:
                return valor

        # Diccionario de formato para st.dataframe()
        format_dict = {"Puntos Totales": "{:.0f}"}
        format_dict.update({col: format_decimal for col in columnas_pruebas})

        # --------------------------------------------
        # COLOR SOLO EN EL TEXTO  (NO fondo)
        # --------------------------------------------
        def color_text(row):
            puntos = row["Puntos Totales"]
            if puntos >= mini:
                color = "color: green; font-weight: bold;"
            elif puntos >= repesca:
                color = "color: orange; font-weight: bold;"
            else:
                color = ""
            return [color] * len(row)

        df = df.reset_index(drop=True)
        df.index = df.index + 1  # si quieres empezar en 1 en lugar de 0

        
        styled = (
            df.style
            .apply(color_text, axis=1)
            .format(format_dict)
        )

        st.dataframe(styled, use_container_width=True, height=900, hide_index=True)

    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {e}")
