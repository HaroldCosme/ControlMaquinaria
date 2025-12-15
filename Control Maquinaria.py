import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión de Maquinaria", layout="wide", page_icon="🏗️")

st.title("🚜 Control de Flota - Tiempo Real")

# --- 1. DATOS SIMULADOS (Lo que llenarán los operadores) ---
# Agregamos: Operador, Petróleo (%), Horómetros
data = [
    {"ID": "GR-01", "Equipo": "Grúa Terex 90T", "Ubicación": "Mina Chinalco", "Estado": "Operativo", "Operador": "Juan Pérez", "Combustible_%": 75, "H_Inicio": 5420, "H_Actual": 5428},
    {"ID": "GR-02", "Equipo": "Grúa Terex 90T", "Ubicación": "Piura", "Estado": "Mantenimiento", "Operador": "Carlos Diaz", "Combustible_%": 10, "H_Inicio": 3100, "H_Actual": 3100},
    {"ID": "GR-03", "Equipo": "Grúa Zoomlion 110T", "Ubicación": "Minera Deysi", "Estado": "Operativo", "Operador": "Luis Quispe", "Combustible_%": 45, "H_Inicio": 1200, "H_Actual": 1210},
    {"ID": "DP-01", "Equipo": "Dumper Volvo", "Ubicación": "Minera Deysi", "Estado": "Operativo", "Operador": "Mario T.", "Combustible_%": 88, "H_Inicio": 8500, "H_Actual": 8509},
    {"ID": "EX-01", "Equipo": "Excavadora Volvo", "Ubicación": "Piura", "Estado": "Stand-by", "Operador": "Sin Asignar", "Combustible_%": 30, "H_Inicio": 4400, "H_Actual": 4400},
]

df = pd.DataFrame(data)

# --- 2. CÁLCULOS AUTOMÁTICOS (Ingeniería) ---
# Calculamos cuánto trabajó hoy (Actual - Inicio)
df["Horas_Hoy"] = df["H_Actual"] - df["H_Inicio"]

# --- 3. FILTROS ---
st.sidebar.header("Filtros")
filtro_obra = st.sidebar.multiselect("Filtrar por Obra:", df["Ubicación"].unique(), default=df["Ubicación"].unique())
df_filtrado = df[df["Ubicación"].isin(filtro_obra)]

# --- 4. KPIs RÁPIDOS ---
# Mostramos alertas de máquinas que necesitan combustible urgente (< 20%)
bajos_combustible = df_filtrado[df_filtrado["Combustible_%"] < 20]

if not bajos_combustible.empty:
    st.error(f"⚠️ ¡ALERTA! {len(bajos_combustible)} equipos con combustible CRÍTICO.")

# --- 5. LA TABLA PRINCIPAL (Lo que pediste) ---
st.subheader("📋 Estado Actual de la Flota")

# Usamos un dataframe con formato de colores
# Pintamos la barra de progreso del combustible y coloreamos el estado
st.data_editor(
    df_filtrado,
    column_config={
        "Combustible_%": st.column_config.ProgressColumn(
            "Nivel Diesel",
            help="Nivel actual del tanque",
            format="%d%%",
            min_value=0,
            max_value=100,
        ),
        "H_Actual": st.column_config.NumberColumn(
            "Horómetro Total",
            help="Lectura actual del horómetro (Para Mantenimiento)",
            format="%d h"
        ),
        "Horas_Hoy": st.column_config.NumberColumn(
            "Prod. Diario",
            help="Horas trabajadas en el turno (Para Cobrar)",
            format="%d hrs"
        ),
        "Estado": st.column_config.SelectboxColumn(
            "Estado",
            options=["Operativo", "Mantenimiento", "Stand-by"],
            required=True,
        )
    },
    hide_index=True,
    use_container_width=True
)

# --- 6. GRÁFICO DE PRODUCCIÓN ---
st.subheader("💰 Producción del Día (Horas Trabajadas)")
fig = px.bar(df_filtrado, x="Equipo", y="Horas_Hoy", color="Ubicación", text_auto=True, title="¿Quién trabajó más hoy?")
st.plotly_chart(fig, use_container_width=True)
