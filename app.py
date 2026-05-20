import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Gestión de Tiempos", layout="wide")

@st.cache_data
def cargar_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = cargar_config()

def init_db():
    conn = sqlite3.connect('tiempos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            hora TIME,
            sector TEXT,
            tiempo_minutos INTEGER,
            tarea TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- INTERFAZ DE USUARIO ---
st.title("⏱️ Registro de Actividades")

# Pestañas para separar el ingreso del tablero
tab_ingreso, tab_tablero = st.tabs(["📝 Nuevo Registro", "📊 Tablero Dinámico"])

with tab_ingreso:
    st.subheader("Registrar nueva tarea")
    
    # Formularios de selección rápida
    col1, col2, col3 = st.columns(3)
    with col1:
        sector_sel = st.selectbox("Sector / Proyecto", config["sectores"])
    with col2:
        tiempo_sel = st.selectbox("Tiempo Demandado (min)", config["tiempos_minutos"])
    with col3:
        tarea_sel = st.selectbox("Tipo de Tarea", config["tareas"])
        
    if st.button("Guardar Registro", use_container_width=True, type="primary"):
        conn = sqlite3.connect('tiempos.db')
        c = conn.cursor()
        ahora = datetime.now()
        c.execute("INSERT INTO registros (fecha, hora, sector, tiempo_minutos, tarea) VALUES (?, ?, ?, ?, ?)",
                  (ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S"), sector_sel, tiempo_sel, tarea_sel))
        conn.commit()
        conn.close()
        st.success(f"✅ Registrado: {tiempo_sel} min en {tarea_sel} para {sector_sel}")

with tab_tablero:
    st.subheader("Métricas Generales")
    
    # Cargar datos
    conn = sqlite3.connect('tiempos.db')
    df = pd.read_sql_query("SELECT * FROM registros", conn)
    conn.close()
    
    if not df.empty:
        # Convertir fecha a datetime
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['horas'] = df['tiempo_minutos'] / 60.0
        
        # Filtros del tablero
        dias_filtro = st.slider("Días a analizar", 1, 30, 7)
        fecha_limite = pd.Timestamp.now().normalize() - pd.Timedelta(days=dias_filtro)
        df_filtrado = df[df['fecha'] >= fecha_limite]
        
        col_metric1, col_metric2 = st.columns(2)
        col_metric1.metric("Horas Totales (Período)", f"{df_filtrado['horas'].sum():.1f} hs")
        col_metric2.metric("Registros Totales", len(df_filtrado))
        
        # Gráficos
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.write("### Tiempo por Proyecto (hs)")
            df_proyecto = df_filtrado.groupby('sector')['horas'].sum().reset_index()
            st.bar_chart(df_proyecto, x='sector', y='horas')
            
        with col_graf2:
            st.write("### Tiempo por Tipo de Tarea (hs)")
            df_tarea = df_filtrado.groupby('tarea')['horas'].sum().reset_index()
            st.bar_chart(df_tarea, x='tarea', y='horas')
    else:
        st.info("Aún no hay registros en la base de datos.")