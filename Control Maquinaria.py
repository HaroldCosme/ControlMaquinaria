import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Parte Diario de Maquinaria", layout="wide", page_icon="⛽")

# Cambiamos el logo a una excavadora
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2318/2318464.png", width=120)

st.title("⛽ Control de Combustible y Horómetros - Diario")

# --- 1. DATOS SIMULADOS (Parte Diario) ---
# Agregamos: Fecha, Niveles de Inicio/Fin tanto de Diesel como de Horómetro
data = [
    {
        "ID": "GR-01", "Equipo": "Grúa Terex 90T", "Ubicación": "Mina Chinalco", "Estado": "Operativo",
        "Fecha": "2023-12-15",
        "Diesel_Inicio_Gal": 50,  "Diesel_Fin_Gal": 42, # Consumió 8 galones
        "Horometro_Inicio": 5420, "Horometro_Fin": 5428, # Trabajó 8 horas
        "Operador": "Juan Pérez"
    },
    {
        "ID": "GR-03", "Equipo": "Grúa Zoomlion 110T", "Ubicación": "Minera Deysi", "Estado": "Operativo",
        "Fecha": "2023-12-15",
        "Diesel_Inicio_Gal": 80,  "Diesel_Fin_Gal": 65, # Consumió 15 galones
        "Horometro_Inicio": 1200, "Horometro_Fin": 1210, # Trabajó 10 horas
        "Operador": "Luis Quispe"
    },
    {
        "ID": "DP-01", "Equipo": "Dumper Volvo A40", "Ubicación": "Minera Deysi", "Estado": "Operativo",
        "Fecha": "2023-12-15",
        "Diesel_Inicio_Gal": 100, "Diesel_Fin_Gal": 80, # Consumió 20 galones
        "Horometro_Inicio": 8500, "Horometro_Fin": 8510, # Trabajó 10 horas
        "Operador": "Mario T."
    },
    {
        "ID": "EX-01", "Equipo": "Excavadora Volvo", "Ubicación": "Piura", "Estado": "Stand-by",
        "Fecha": "2023-12-15",
        "Diesel_Inicio_Gal": 40,  "Diesel_Fin_Gal": 40, # No consumió
        "Horometro_Inicio": 4400, "Horometro_Fin": 4400, # No trabajó
        "Operador": "Sin Asignar"
    },
    {
        "ID": "ZM-02", "Equipo": "Grúa Zoomlion 130T", "Ubicación": "Mina Chinalco", "Estado": "Operativo",
        "Fecha": "2023-12-15",
        "Diesel_Inicio_Gal": 120, "Diesel_Fin_Gal": 105, # Consumió 15 galones
        "Horometro_Inicio": 2100, "Horometro_Fin": 2108, # Trabajó 8 horas
        "Operador": "Pedro A."
    },
]

df = pd.DataFrame(data)

# --- 2. CÁLCULOS DE INGENIERÍA (Rendimiento) ---
# Calculamos la diferencia del día
df["Horas_Trabajadas"] = df["Horometro_Fin"] - df["Horometro_Inicio"]
df["Consumo_Galones"] = df["Diesel_Inicio_Gal"] - df["Diesel_Fin_Gal"]

# Calculamos el Ratio (Galones por Hora) - Vital para ver si están robando combustible
# Si Horas es 0, ponemos 0 para evitar error de división
df["Galones_por_Hora"] = df.apply(lambda row: row["Consumo_Galones"] / row["Horas_Trabajadas"] if row["Horas_Trabajadas"] > 0 else 0, axis=1)

# --- 3. BARRA LATERAL ---
st.sidebar.header("Filtros")
filtro_obra = st.sidebar.multiselect("Obra:", df["Ubicación"].unique(), default=df["Ubicación"].unique())
df_filtrado = df[df["Ubicación"].isin(filtro_obra)]

# --- 4. KPI'S DE CONSUMO ---
total_galones = df_filtrado["Consumo_Galones"].sum()
total_horas = df_filtrado["Horas_Trabajadas"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Total Horas Hoy", f"{total_horas} hrs")
c2.metric("Total Combustible Consumido", f"{total_galones} gal")
# Ratio Promedio de la flota seleccionada
ratio_promedio = total_galones / total_horas if total_horas > 0 else 0
c3.metric("Rendimiento Promedio", f"{ratio_promedio:.1f} gal/hora", delta="Eficiencia Flota")

st.divider()

# --- 5. TABLA DE CONTROL DIARIO (Lo que pediste) ---
st.subheader("📋 Parte Diario Detallado")

st.dataframe(
    df_filtrado[[
        "Fecha", "Equipo", "Ubicación", 
        "Diesel_Inicio_Gal", "Diesel_Fin_Gal", "Consumo_Galones",
        "Horometro_Inicio", "Horometro_Fin", "Horas_Trabajadas", 
        "Galones_por_Hora"
    ]].style.format({
        "Diesel_Inicio_Gal": "{:.1f} gl",
        "Diesel_Fin_Gal": "{:.1f} gl",
        "Consumo_Galones": "{:.1f} gl",
        "Horometro_Inicio": "{:,.1f}",
        "Horometro_Fin": "{:,.1f}",
        "Horas_Trabajadas": "{:.1f} hrs",
        "Galones_por_Hora": "{:.2f} gl/h"
    }).background_gradient(subset=["Consumo_Galones"], cmap="Reds"), # Pinta rojo si consumió mucho
    use_container_width=True
)

# --- 6. GRÁFICO DE RENDIMIENTO ---
st.subheader("📊 Análisis de Consumo (¿Quién gasta más?)")
# Muestra quién consumió más combustible vs horas trabajadas
fig = px.scatter(
    df_filtrado, 
    x="Horas_Trabajadas", 
    y="Consumo_Galones", 
    size="Galones_por_Hora", 
    color="Equipo",
    hover_name="Equipo",
    title="Eficiencia: Arriba a la izquierda = Alto Consumo (¡Ojo!)"
)
st.plotly_chart(fig, use_container_width=True)
