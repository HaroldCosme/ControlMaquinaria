import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Sistema de Auditoría Maquinaria", layout="wide", page_icon="👮")

# Logo de seguridad/control
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2318/2318464.png", width=120)
st.sidebar.title("Auditoría y Control")

# --- 1. BASE DE DATOS MEJORADA (Con Estándares de Consumo) ---
data = [
    {
        "ID": "GR-01", "Equipo": "Grúa Terex 90T", "Ubicación": "Mina Chinalco", "Estado": "Operativo", "Operador": "Juan Pérez",
        # El estándar es lo que DEBERÍA gastar (según manual)
        "Consumo_Std_Gal_Hr": 4.5, 
        "Horas_Mes": 180, "Tarifa_Hora": 180.00, "Gasto_Combustible_Mes": 4500, "Gasto_Viaticos": 1200,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 50, "Diesel_Fin": 40, # Consumió 10 gl en 8 horas (1.25 gl/h) -> OK
        "H_Inicio": 5420, "H_Fin": 5428
    },
    {
        "ID": "GR-03", "Equipo": "Grúa Zoomlion 110T", "Ubicación": "Minera Deysi", "Estado": "Operativo", "Operador": "Luis Quispe",
        "Consumo_Std_Gal_Hr": 5.0, # Esta gasta más
        "Horas_Mes": 210, "Tarifa_Hora": 220.00, "Gasto_Combustible_Mes": 5800, "Gasto_Viaticos": 1500,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 80, "Diesel_Fin": 55, # Consumió 25 gl en 4 horas (6.25 gl/h) -> ROBO!! (Std es 5.0)
        "H_Inicio": 1200, "H_Fin": 1204
    },
    {
        "ID": "DP-01", "Equipo": "Dumper Volvo A40", "Ubicación": "Minera Deysi", "Estado": "Operativo", "Operador": "Mario T.",
        "Consumo_Std_Gal_Hr": 8.0,
        "Horas_Mes": 250, "Tarifa_Hora": 140.00, "Gasto_Combustible_Mes": 8000, "Gasto_Viaticos": 1200,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 100, "Diesel_Fin": 84, 
        "H_Inicio": 8500, "H_Fin": 8502 # Trabajó solo 2 horas -> ¿Por qué tan poco?
    },
    {
        "ID": "ZM-02", "Equipo": "Grúa Zoomlion 130T", "Ubicación": "Mina Chinalco", "Estado": "Operativo", "Operador": "Pedro A.",
        "Consumo_Std_Gal_Hr": 6.0,
        "Horas_Mes": 195, "Tarifa_Hora": 250.00, "Gasto_Combustible_Mes": 6200, "Gasto_Viaticos": 1500,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 120, "Diesel_Fin": 108, 
        "H_Inicio": 2100, "H_Fin": 2102
    },
    {
        "ID": "EX-01", "Equipo": "Excavadora Volvo", "Ubicación": "Piura", "Estado": "Stand-by", "Operador": "Sin Asignar",
        "Consumo_Std_Gal_Hr": 5.5,
        "Horas_Mes": 0, "Tarifa_Hora": 110.00, "Gasto_Combustible_Mes": 0, "Gasto_Viaticos": 0,
        "Fecha_Hoy": "2023-12-15", "Diesel_Inicio": 40, "Diesel_Fin": 40, 
        "H_Inicio": 4400, "H_Fin": 4400
    }
]

df = pd.DataFrame(data)

# --- 2. CÁLCULOS AUDITORÍA ---
# Financieros
df["Ingreso_Total"] = df["Horas_Mes"] * df["Tarifa_Hora"]
df["Gastos_Totales"] = df["Gasto_Combustible_Mes"] + df["Gasto_Viaticos"]
df["Utilidad"] = df["Ingreso_Total"] - df["Gastos_Totales"]

# Operativos
df["Consumo_Real_Gal"] = df["Diesel_Inicio"] - df["Diesel_Fin"]
df["Horas_Hoy"] = df["H_Fin"] - df["H_Inicio"]
df["Ratio_Real"] = df.apply(lambda x: x["Consumo_Real_Gal"] / x["Horas_Hoy"] if x["Horas_Hoy"] > 0 else 0, axis=1)

# DETECTOR DE ROBO: Diferencia entre Real vs Estándar
df["Desviacion_Galones"] = df["Consumo_Real_Gal"] - (df["Horas_Hoy"] * df["Consumo_Std_Gal_Hr"])
# Si la desviación es positiva, gastó de más.

# --- 3. BARRA LATERAL ---
filtro_obra = st.sidebar.multiselect("Filtrar por Obra:", df["Ubicación"].unique(), default=df["Ubicación"].unique())
df_filtrado = df[df["Ubicación"].isin(filtro_obra)]

st.sidebar.markdown("---")
st.sidebar.warning("⚠️ Módulo de Control Activo")

# --- 4. PESTAÑAS ESTRATÉGICAS ---
tab1, tab2, tab3 = st.tabs(["💰 Finanzas", "👮 Auditoría de Robo", "👷 Productividad Personal"])

# === PESTAÑA 1: FINANZAS (Rápido) ===
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Utilidad Neta Mes", f"S/ {df_filtrado['Utilidad'].sum():,.2f}")
    col2.metric("Facturación", f"S/ {df_filtrado['Ingreso_Total'].sum():,.2f}")
    col3.metric("Gastos Totales", f"S/ {df_filtrado['Gastos_Totales'].sum():,.2f}")
    
    st.dataframe(df_filtrado[["Equipo", "Utilidad"]].style.format({"Utilidad": "S/ {:,.2f}"}).background_gradient(cmap="Greens"), use_container_width=True)

# === PESTAÑA 2: AUDITORÍA DE COMBUSTIBLE (LO IMPORTANTE) ===
with tab2:
    st.header("⛽ Control de Combustible (Real vs Estándar)")
    
    # Alerta automática
    posibles_robos = df_filtrado[df_filtrado["Desviacion_Galones"] > 2] # Más de 2 galones de diferencia
    if not posibles_robos.empty:
        st.error(f"🚨 ALERTA: Se detectó consumo excesivo en {len(posibles_robos)} equipos hoy.")
        for index, row in posibles_robos.iterrows():
            st.markdown(f"🔴 **{row['Equipo']}** (Operador: {row['Operador']}): Gastó **{row['Desviacion_Galones']:.1f} galones EXTRA** injustificados.")
    
    st.divider()
    
    # Gráfico de Dispersión: Lo normal vs Lo Real
    c1, c2 = st.columns([2,1])
    with c1:
        # Preparamos datos para comparar
        st.subheader("Análisis de Eficiencia")
        # Graficamos el Ratio Real. Línea punteada sería el estándar (podemos simular visualmente con colores)
        fig_robo = px.bar(
            df_filtrado[df_filtrado["Horas_Hoy"]>0], 
            x="Equipo", 
            y=["Ratio_Real", "Consumo_Std_Gal_Hr"], 
            barmode="group",
            title="Consumo Real (Azul) vs Lo que debería gastar (Rojo)",
            color_discrete_map={"Ratio_Real": "#1f77b4", "Consumo_Std_Gal_Hr": "#d62728"}
        )
        st.plotly_chart(fig_robo, use_container_width=True)
        st.caption("Si la barra AZUL es más alta que la ROJA -> 🚩 Ojo al piojo (Posible Robo o Falla)")

    with c2:
        st.subheader("Detalle Diario")
        st.dataframe(
            df_filtrado[["Equipo", "Consumo_Real_Gal", "Desviacion_Galones"]].style.format("{:.1f} gl").background_gradient(subset=["Desviacion_Galones"], cmap="Reds"),
            use_container_width=True
        )

# === PESTAÑA 3: PRODUCTIVIDAD (QUIÉN TRABAJA Y QUIÉN NO) ===
with tab3:
    st.header("👷 Ranking de Operadores (Hoy)")
    
    # Métricas de pereza
    sin_trabajar = df_filtrado[df_filtrado["Horas_Hoy"] == 0]
    if not sin_trabajar.empty:
        st.warning(f"⚠️ Hay {len(sin_trabajar)} operadores que reportaron 0 horas hoy.")
    
    # Gráfico de Ranking
    df_sorted = df_filtrado.sort_values(by="Horas_Hoy", ascending=True) # De menos a más
    
    fig_prod = px.bar(
        df_sorted, 
        x="Horas_Hoy", 
        y="Operador", 
        orientation='h', 
        color="Horas_Hoy",
        title="¿Quién trabajó menos hoy?",
        text_auto=True,
        color_continuous_scale="RdYlGn" # Rojo el que trabajó poco, Verde el que trabajó mucho
    )
    st.plotly_chart(fig_prod, use_container_width=True)
    
    st.subheader("Bitácora de Operadores")
    st.dataframe(
        df_filtrado[["Operador", "Equipo", "Horas_Hoy", "Estado"]].style.applymap(
            lambda x: 'color: red; font-weight: bold' if x == 0 else 'color: green', subset=['Horas_Hoy']
        ),
        use_container_width=True
    )
