import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Sistema Integral Maquinaria", layout="wide", page_icon="🏗️")

# Logo
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2318/2318464.png", width=120)
st.sidebar.title("Panel de Control")

# --- 1. BASE DE DATOS UNIFICADA ---
data = [
    {
        "ID": "GR-01", "Equipo": "Grúa Terex 90T", "Ubicación": "Mina Chinalco", "Estado": "Operativo", "Operador": "Juan Pérez",
        "Horas_Mes": 180, "Tarifa_Hora": 180.00, "Gasto_Combustible_Mes": 4500, "Gasto_Viaticos": 1200,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 50, "Diesel_Fin": 42, "H_Inicio": 5420, "H_Fin": 5428
    },
    {
        "ID": "GR-02", "Equipo": "Grúa Terex 90T", "Ubicación": "Piura", "Estado": "Mantenimiento", "Operador": "Carlos Diaz",
        "Horas_Mes": 20, "Tarifa_Hora": 180.00, "Gasto_Combustible_Mes": 500, "Gasto_Viaticos": 800,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 20, "Diesel_Fin": 20, "H_Inicio": 3100, "H_Fin": 3100
    },
    {
        "ID": "GR-03", "Equipo": "Grúa Zoomlion 110T", "Ubicación": "Minera Deysi", "Estado": "Operativo", "Operador": "Luis Quispe",
        "Horas_Mes": 210, "Tarifa_Hora": 220.00, "Gasto_Combustible_Mes": 5800, "Gasto_Viaticos": 1500,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 80, "Diesel_Fin": 65, "H_Inicio": 1200, "H_Fin": 1210
    },
    {
        "ID": "DP-01", "Equipo": "Dumper Volvo A40", "Ubicación": "Minera Deysi", "Estado": "Operativo", "Operador": "Mario T.",
        "Horas_Mes": 250, "Tarifa_Hora": 140.00, "Gasto_Combustible_Mes": 8000, "Gasto_Viaticos": 1200,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 100, "Diesel_Fin": 80, "H_Inicio": 8500, "H_Fin": 8510
    },
    {
        "ID": "ZM-02", "Equipo": "Grúa Zoomlion 130T", "Ubicación": "Mina Chinalco", "Estado": "Operativo", "Operador": "Pedro A.",
        "Horas_Mes": 195, "Tarifa_Hora": 250.00, "Gasto_Combustible_Mes": 6200, "Gasto_Viaticos": 1500,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 120, "Diesel_Fin": 105, "H_Inicio": 2100, "H_Fin": 2108
    }
]

df = pd.DataFrame(data)

# --- 2. CÁLCULOS ---
df["Ingreso_Total"] = df["Horas_Mes"] * df["Tarifa_Hora"]
df["Gastos_Totales"] = df["Gasto_Combustible_Mes"] + df["Gasto_Viaticos"]
df["Utilidad"] = df["Ingreso_Total"] - df["Gastos_Totales"]

df["Consumo_Galones"] = df["Diesel_Inicio"] - df["Diesel_Fin"]
df["Horas_Trabajadas_Hoy"] = df["H_Fin"] - df["H_Inicio"]
df["Ratio_Gal_Hr"] = df.apply(lambda x: x["Consumo_Galones"] / x["Horas_Trabajadas_Hoy"] if x["Horas_Trabajadas_Hoy"] > 0 else 0, axis=1)

# --- 3. BARRA LATERAL ---
filtro_obra = st.sidebar.multiselect("Filtrar por Obra:", df["Ubicación"].unique(), default=df["Ubicación"].unique())
df_filtrado = df[df["Ubicación"].isin(filtro_obra)]

st.sidebar.markdown("---")
st.sidebar.info("Sistema v1.2 - Modo Demo")

# --- 4. PESTAÑAS ---
tab1, tab2 = st.tabs(["💰 Gerencia y Finanzas", "⛽ Parte Diario y Combustible"])

# === PESTAÑA 1 ===
with tab1:
    st.header("📊 Rentabilidad Mensual")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Facturación Total", f"S/ {df_filtrado['Ingreso_Total'].sum():,.2f}")
    col2.metric("Gastos Operativos", f"S/ {df_filtrado['Gastos_Totales'].sum():,.2f}", delta="- Costos", delta_color="inverse")
    col3.metric("Utilidad Neta", f"S/ {df_filtrado['Utilidad'].sum():,.2f}", delta="Ganancia")
    col4.metric("Máquinas Activas", len(df_filtrado[df_filtrado['Estado']=='Operativo']))
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        df_melt = df_filtrado.melt(id_vars=["Equipo"], value_vars=["Ingreso_Total", "Gastos_Totales"], var_name="Tipo", value_name="Monto")
        fig = px.bar(df_melt, x="Equipo", y="Monto", color="Tipo", barmode="group", title="Ingresos vs Gastos", color_discrete_map={"Ingreso_Total": "#2ecc71", "Gastos_Totales": "#e74c3c"})
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("Detalle de Utilidad")
        # CORRECCIÓN AQUÍ: Usamos un diccionario para formatear solo las columnas numéricas
        st.dataframe(
            df_filtrado[["Equipo", "Ingreso_Total", "Gastos_Totales", "Utilidad"]].style.format({
                "Ingreso_Total": "S/ {:,.2f}",
                "Gastos_Totales": "S/ {:,.2f}",
                "Utilidad": "S/ {:,.2f}"
            }).background_gradient(subset=["Utilidad"], cmap="RdYlGn"),
            use_container_width=True
        )

# === PESTAÑA 2 ===
with tab2:
    st.header("🚜 Control Diario de Operaciones")
    st.markdown("**Registro de Horómetros y Combustible - Turno Día**")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Horas Hoy", f"{df_filtrado['Horas_Trabajadas_Hoy'].sum()} hrs")
    k2.metric("Consumo Diesel Hoy", f"{df_filtrado['Consumo_Galones'].sum()} gal")
    promedio_fleet = df_filtrado['Consumo_Galones'].sum() / df_filtrado['Horas_Trabajadas_Hoy'].sum() if df_filtrado['Horas_Trabajadas_Hoy'].sum() > 0 else 0
    k3.metric("Rendimiento Flota", f"{promedio_fleet:.1f} gal/hr", delta="Consumo Promedio")
    
    st.divider()
    
    st.subheader("📋 Planilla de Control Diario")
    st.dataframe(
        df_filtrado[[
            "Fecha_Hoy", "Equipo", "Operador", 
            "Diesel_Inicio", "Diesel_Fin", "Consumo_Galones",
            "H_Inicio", "H_Fin", "Horas_Trabajadas_Hoy", "Ratio_Gal_Hr"
        ]].style.format({
            "Diesel_Inicio": "{:.1f} gl", "Diesel_Fin": "{:.1f} gl", "Consumo_Galones": "{:.1f} gl",
            "H_Inicio": "{:,.1f}", "H_Fin": "{:,.1f}", 
            "Horas_Trabajadas_Hoy": "{:.1f} hrs", "Ratio_Gal_Hr": "{:.2f} gl/h"
        }).background_gradient(subset=["Ratio_Gal_Hr"], cmap="Reds"),
        use_container_width=True
    )
    
    st.caption("Nota: Si la columna de Ratio (gl/h) se pone roja, la máquina está consumiendo más de lo normal.")
