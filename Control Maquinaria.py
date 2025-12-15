import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gerencia de Maquinaria", layout="wide", page_icon="💰")

# --- 1. DATOS SIMULADOS (Inteligencia de Negocios) ---
# Hemos agregado: Tarifa (cuánto cobras), Gasto en Comida/Viáticos y Gasto en Petróleo
data = [
    {
        "ID": "GR-01", "Equipo": "Grúa Terex 90T", "Ubicación": "Mina Chinalco", "Estado": "Operativo", 
        "Operador": "Juan Pérez", "Horas_Mes": 180, 
        "Tarifa_Hora": 180.00,  # Soles o Dólares
        "Gasto_Combustible": 4500, 
        "Gasto_Comida_Viaticos": 1200 # Comida del personal
    },
    {
        "ID": "GR-02", "Equipo": "Grúa Terex 90T", "Ubicación": "Piura", "Estado": "Mantenimiento", 
        "Operador": "Carlos Diaz", "Horas_Mes": 20, 
        "Tarifa_Hora": 180.00, 
        "Gasto_Combustible": 500, 
        "Gasto_Comida_Viaticos": 800 # Se paga comida aunque esté parada
    },
    {
        "ID": "GR-03", "Equipo": "Grúa Zoomlion 110T", "Ubicación": "Minera Deysi", "Estado": "Operativo", 
        "Operador": "Luis Quispe", "Horas_Mes": 210, 
        "Tarifa_Hora": 220.00, 
        "Gasto_Combustible": 5800, 
        "Gasto_Comida_Viaticos": 1500
    },
    {
        "ID": "DP-01", "Equipo": "Dumper Volvo A40", "Ubicación": "Minera Deysi", "Estado": "Operativo", 
        "Operador": "Mario T.", "Horas_Mes": 250, 
        "Tarifa_Hora": 140.00, 
        "Gasto_Combustible": 8000, 
        "Gasto_Comida_Viaticos": 1200
    },
    {
        "ID": "EX-01", "Equipo": "Excavadora Volvo", "Ubicación": "Piura", "Estado": "Stand-by", 
        "Operador": "Sin Asignar", "Horas_Mes": 10, 
        "Tarifa_Hora": 110.00, 
        "Gasto_Combustible": 0, 
        "Gasto_Comida_Viaticos": 0
    },
    {
        "ID": "ZM-02", "Equipo": "Grúa Zoomlion 130T", "Ubicación": "Mina Chinalco", "Estado": "Operativo", 
        "Operador": "Pedro A.", "Horas_Mes": 195, 
        "Tarifa_Hora": 250.00, 
        "Gasto_Combustible": 6200, 
        "Gasto_Comida_Viaticos": 1500
    },
]

df = pd.DataFrame(data)

# --- 2. CÁLCULOS FINANCIEROS (El Cerebro del Sistema) ---
df["Ingreso_Total"] = df["Horas_Mes"] * df["Tarifa_Hora"]
df["Gastos_Totales"] = df["Gasto_Combustible"] + df["Gasto_Comida_Viaticos"]
df["Utilidad"] = df["Ingreso_Total"] - df["Gastos_Totales"]
df["Margen_%"] = (df["Utilidad"] / df["Ingreso_Total"]) * 100

# --- 3. BARRA LATERAL (FILTROS) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2830/2830534.png", width=100) # Un logo genérico
st.sidebar.header("Filtrar Reporte")
filtro_obra = st.sidebar.multiselect(
    "Seleccionar Obra:",
    options=df["Ubicación"].unique(),
    default=df["Ubicación"].unique()
)

df_filtrado = df[df["Ubicación"].isin(filtro_obra)]

# --- 4. DASHBOARD FINANCIERO (Lo que le importa al jefe) ---
st.title("💰 Reporte de Rentabilidad - Mes Actual")
st.markdown(f"**Viendo datos de:** {', '.join(filtro_obra)}")

# Métricas grandes arriba
col1, col2, col3, col4 = st.columns(4)

total_facturacion = df_filtrado["Ingreso_Total"].sum()
total_gastos = df_filtrado["Gastos_Totales"].sum()
total_comida = df_filtrado["Gasto_Comida_Viaticos"].sum()
utilidad_neta = df_filtrado["Utilidad"].sum()

col1.metric("Ingresos Totales", f"S/ {total_facturacion:,.2f}")
col2.metric("Gastos Operativos", f"S/ {total_gastos:,.2f}", delta="- Costos", delta_color="inverse")
col3.metric("Gasto en Personal (Comida)", f"S/ {total_comida:,.2f}", help="Viáticos, alimentación y hospedaje")
# La utilidad se pone verde si ganamos, roja si perdemos
col4.metric("UTILIDAD NETA", f"S/ {utilidad_neta:,.2f}", delta="Ganancia Líquida")

st.divider()

# --- 5. GRÁFICOS DE ANÁLISIS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Rentabilidad por Máquina")
    # Gráfico de barras que muestra Ingreso vs Gasto por máquina
    # Preparamos datos para el gráfico
    df_melt = df_filtrado.melt(id_vars=["Equipo"], value_vars=["Ingreso_Total", "Gastos_Totales"], var_name="Tipo", value_name="Monto")
    fig_rentabilidad = px.bar(
        df_melt, 
        x="Equipo", 
        y="Monto", 
        color="Tipo", 
        barmode="group",
        title="Ingresos vs Gastos (¿Qué máquina rinde más?)",
        color_discrete_map={"Ingreso_Total": "#2ecc71", "Gastos_Totales": "#e74c3c"}
    )
    st.plotly_chart(fig_rentabilidad, use_container_width=True)

with c2:
    st.subheader("💸 ¿En qué se va la plata?")
    # Gráfico de pastel de gastos
    gastos_df = pd.DataFrame({
        "Concepto": ["Combustible", "Viáticos/Comida Personal"],
        "Monto": [df_filtrado["Gasto_Combustible"].sum(), df_filtrado["Gasto_Comida_Viaticos"].sum()]
    })
    fig_gastos = px.pie(gastos_df, values="Monto", names="Concepto", hole=0.4, title="Distribución de Gastos", color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_gastos, use_container_width=True)

# --- 6. TABLA DETALLADA CON ALERTA VISUAL ---
st.subheader("📋 Detalle Financiero por Equipo")

st.dataframe(
    df_filtrado[["Equipo", "Ubicación", "Estado", "Horas_Mes", "Ingreso_Total", "Gasto_Comida_Viaticos", "Utilidad"]].style.format({
        "Ingreso_Total": "S/ {:,.2f}",
        "Gasto_Comida_Viaticos": "S/ {:,.2f}",
        "Utilidad": "S/ {:,.2f}"
    }).background_gradient(subset=["Utilidad"], cmap="RdYlGn"), # Colorea verde lo alto, rojo lo bajo
    use_container_width=True
)
