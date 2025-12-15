import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión de Maquinaria", layout="wide", page_icon="🏗️")

# --- 1. DATOS SIMULADOS (Lo que luego vendrá de Supabase) ---
# Aquí creamos un Excel imaginario con tus máquinas reales
data = [
    {"ID": "GR-01", "Tipo": "Grúa Telescópica", "Modelo": "Terex 90T", "Ubicación": "Mina Chinalco", "Estado": "Operativo", "Horas_Mes": 180, "Ingreso": 180*150},
    {"ID": "GR-02", "Tipo": "Grúa Telescópica", "Modelo": "Terex 90T", "Ubicación": "Piura", "Estado": "Mantenimiento", "Horas_Mes": 20, "Ingreso": 20*150},
    {"ID": "GR-03", "Tipo": "Grúa Telescópica", "Modelo": "Zoomlion 110T", "Ubicación": "Minera Deysi", "Estado": "Operativo", "Horas_Mes": 210, "Ingreso": 210*180},
    {"ID": "GR-04", "Tipo": "Grúa Telescópica", "Modelo": "Zoomlion 130T", "Ubicación": "Mina Chinalco", "Estado": "Operativo", "Horas_Mes": 195, "Ingreso": 195*200},
    {"ID": "DP-01", "Tipo": "Dumper", "Modelo": "Volvo A40", "Ubicación": "Minera Deysi", "Estado": "Operativo", "Horas_Mes": 250, "Ingreso": 250*120},
    {"ID": "DP-02", "Tipo": "Dumper", "Modelo": "Volvo A40", "Ubicación": "Minera Deysi", "Estado": "Stand-by", "Horas_Mes": 50, "Ingreso": 50*120},
    {"ID": "EX-01", "Tipo": "Excavadora", "Modelo": "Volvo EC300", "Ubicación": "Piura", "Estado": "Operativo", "Horas_Mes": 160, "Ingreso": 160*110},
    {"ID": "RT-01", "Tipo": "Retroexcavadora", "Modelo": "CAT 420", "Ubicación": "Piura", "Estado": "Operativo", "Horas_Mes": 140, "Ingreso": 140*90},
    {"ID": "TR-01", "Tipo": "Tractor", "Modelo": "D8T", "Ubicación": "Mina Chinalco", "Estado": "Mantenimiento", "Horas_Mes": 10, "Ingreso": 10*250},
]

df = pd.DataFrame(data)

# --- 2. SIDEBAR (Filtros) ---
st.sidebar.header("🔍 Filtros de Gerencia")
filtro_obra = st.sidebar.multiselect(
    "Filtrar por Obra:",
    options=df["Ubicación"].unique(),
    default=df["Ubicación"].unique()
)

# Aplicar filtro
df_filtrado = df[df["Ubicación"].isin(filtro_obra)]

# --- 3. KPI's PRINCIPALES (Lo que el jefe ve primero) ---
st.title("🏗️ Dashboard Gerencial de Activos")
st.markdown(f"**Vista general de flota en:** {', '.join(filtro_obra)}")

col1, col2, col3, col4 = st.columns(4)

total_maquinas = len(df_filtrado)
operativas = len(df_filtrado[df_filtrado["Estado"] == "Operativo"])
mantenimiento = len(df_filtrado[df_filtrado["Estado"] == "Mantenimiento"])
ingreso_total = df_filtrado["Ingreso"].sum()

col1.metric("🚜 Total Máquinas", total_maquinas)
col2.metric("✅ Operativas", f"{operativas} unid.")
col3.metric("🔧 En Mantenimiento", f"{mantenimiento} unid.", delta_color="inverse") # Rojo si hay muchas
col4.metric("💰 Estimado Mes (S/)", f"S/ {ingreso_total:,.2f}")

st.divider()

# --- 4. GRÁFICOS INTERACTIVOS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📍 ¿Dónde están mis máquinas?")
    # Gráfico de barras por ubicación
    fig_ubicacion = px.bar(
        df_filtrado, 
        x="Ubicación", 
        y="Ingreso", 
        color="Tipo", 
        title="Ingresos Generados por Obra y Tipo",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.G10
    )
    st.plotly_chart(fig_ubicacion, use_container_width=True)

with c2:
    st.subheader("📊 Estado de la Flota")
    # Gráfico de pastel (Donut)
    fig_estado = px.pie(
        df_filtrado, 
        names="Estado", 
        values="ID", # Cuenta por ID
        hole=0.4,
        title="Disponibilidad Actual",
        color="Estado",
        color_discrete_map={"Operativo":"green", "Mantenimiento":"red", "Stand-by":"orange"}
    )
    st.plotly_chart(fig_estado, use_container_width=True)

# --- 5. DETALLE (Tabla) ---
st.subheader("📋 Detalle de Equipos")
st.dataframe(
    df_filtrado.style.applymap(
        lambda x: 'background-color: #ffcdd2' if x == 'Mantenimiento' else ('background-color: #c8e6c9' if x == 'Operativo' else ''),
        subset=['Estado']
    ),
    use_container_width=True
)