import streamlit as st
import pandas as pd
import json
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Gestión de Tiempos", layout="wide")

@st.cache_data
def cargar_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = cargar_config()

# Establecer la conexión con Google Sheets
# Nota: Streamlit buscará automáticamente los datos en st.secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Nombre exacto de la pestaña en tu archivo de Google Sheets
NOMBRE_HOJA = "Hoja 1" 

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
        # 1. Leer los datos actuales de la planilla
        try:
            df_actual = conn.read(worksheet=NOMBRE_HOJA, usecols=list(range(5)), ttl=0)
        except Exception as e:
            st.error(f"Error al leer la planilla. Verifica que exista y esté compartida. Detalle: {e}")
            df_actual = pd.DataFrame(columns=["fecha", "hora", "sector", "tiempo_minutos", "tarea"])

        # 2. Crear el nuevo registro
        ahora = datetime.now()
        nuevo_registro = pd.DataFrame([{
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M:%S"),
            "sector": sector_sel,
            "tiempo_minutos": tiempo_sel,
            "tarea": tarea_sel
        }])

        # 3. Concatenar y actualizar
        # Si la hoja estaba vacía, usamos el nuevo registro como base
        if df_actual.empty or df_actual.columns[0] != "fecha":
            df_actualizado = nuevo_registro
        else:
            df_actualizado = pd.concat([df_actual, nuevo_registro], ignore_index=True)
            
        conn.update(worksheet=NOMBRE_HOJA, data=df_actualizado)
        
        st.success(f"✅ Registrado: {tiempo_sel} min en {tarea_sel} para {sector_sel}")

with tab_tablero:
    st.subheader("Métricas Generales")
    
    # Cargar datos desde Google Sheets (ttl=5 actualiza la caché cada 5 segundos)
    try:
        df = conn.read(worksheet=NOMBRE_HOJA, usecols=list(range(5)), ttl=5)
    except Exception:
        df = pd.DataFrame() # DataFrame vacío si hay error
    
    # Validar que existan datos y tengan la estructura correcta
    if not df.empty and "fecha" in df.columns:
        # Limpiar datos (por si hay filas vacías leídas del Sheets)
        df = df.dropna(subset=['fecha'])
        
        # Convertir tipos de datos
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['tiempo_minutos'] = pd.to_numeric(df['tiempo_minutos'])
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
        st.info("Aún no hay registros en la base de datos o la hoja no tiene el formato esperado.")