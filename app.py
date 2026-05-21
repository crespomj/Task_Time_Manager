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

conn = st.connection("gsheets", type=GSheetsConnection)
NOMBRE_HOJA = "Hoja 1" 

# --- INTERFAZ DE USUARIO ---
st.title("⏱️ Registro de Actividades")

tab_ingreso, tab_tablero = st.tabs(["📝 Nuevo Registro", "📊 Tablero Dinámico"])

with tab_ingreso:
    
    # 1. Macro categoría (Un solo toque)
    st.write("### Ámbito de Acción")
    ambito_sel = st.radio("Selecciona el área general:", config["ambitos"], horizontal=True, label_visibility="collapsed")
    
    st.divider()
    
    # 2. Detalles principales
    col1, col2, col3 = st.columns(3)
    with col1:
        sector_sel = st.selectbox("Sector / Proyecto", config["sectores"])
    with col2:
        tiempo_sel = st.selectbox("Tiempo Demandado (min)", config["tiempos_minutos"])
    with col3:
        tarea_sel = st.selectbox("Tipo de Tarea", config["tareas"])
        
    # 3. Opciones avanzadas (Colapsables para no ensuciar la pantalla)
    with st.expander("Opciones adicionales (Imprevistos y Notas)"):
        imprevisto = st.toggle("🚨 Marcar como Urgencia / Interrupción no planificada")
        nota = st.text_input("Nota breve (Usa el micrófono del teclado para dictar)")
        
    if st.button("Guardar Registro", use_container_width=True, type="primary"):
        try:
            # Ahora leemos 8 columnas
            df_actual = conn.read(worksheet=NOMBRE_HOJA, usecols=list(range(8)), ttl=0)
        except Exception as e:
            st.error(f"Error al leer la planilla. Detalle: {e}")
            df_actual = pd.DataFrame(columns=["fecha", "hora", "sector", "tiempo_minutos", "tarea", "ambito", "imprevisto", "nota"])

        ahora = datetime.now()
        nuevo_registro = pd.DataFrame([{
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M:%S"),
            "sector": sector_sel,
            "tiempo_minutos": tiempo_sel,
            "tarea": tarea_sel,
            "ambito": ambito_sel,
            "imprevisto": "Sí" if imprevisto else "No",
            "nota": nota
        }])

        if df_actual.empty or df_actual.columns[0] != "fecha":
            df_actualizado = nuevo_registro
        else:
            df_actualizado = pd.concat([df_actual, nuevo_registro], ignore_index=True)
            
        conn.update(worksheet=NOMBRE_HOJA, data=df_actualizado)
        st.success(f"✅ Registrado: {tiempo_sel} min ({tarea_sel} - {ambito_sel})")

with tab_tablero:
    st.subheader("Métricas Generales")
    
    try:
        # Leemos las 8 columnas
        df = conn.read(worksheet=NOMBRE_HOJA, usecols=list(range(8)), ttl=5)
    except Exception:
        df = pd.DataFrame() 
    
    if not df.empty and "fecha" in df.columns:
        df = df.dropna(subset=['fecha'])
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['tiempo_minutos'] = pd.to_numeric(df['tiempo_minutos'])
        df['horas'] = df['tiempo_minutos'] / 60.0
        
        dias_filtro = st.slider("Días a analizar", 1, 30, 7)
        fecha_limite = pd.Timestamp.now().normalize() - pd.Timedelta(days=dias_filtro)
        df_filtrado = df[df['fecha'] >= fecha_limite]
        
        # --- MÉTRICAS SUPERIORES ---
        col_m1, col_m2, col_m3 = st.columns(3)
        total_horas = df_filtrado['horas'].sum()
        
        # Calcular horas de imprevistos
        df_imprevistos = df_filtrado[df_filtrado['imprevisto'] == 'Sí']
        horas_imprevistas = df_imprevistos['horas'].sum()
        porcentaje_imprevisto = (horas_imprevistas / total_horas * 100) if total_horas > 0 else 0
        
        col_m1.metric("Horas Totales", f"{total_horas:.1f} hs")
        col_m2.metric("Registros", len(df_filtrado))
        col_m3.metric("🚨 Tiempo en Imprevistos", f"{horas_imprevistas:.1f} hs", f"{porcentaje_imprevisto:.1f}% del tiempo", delta_color="inverse")
        
        st.divider()
        
        # --- GRÁFICOS ---
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.write("### Distribución por Ámbito (hs)")
            df_ambito = df_filtrado.groupby('ambito')['horas'].sum().reset_index()
            st.bar_chart(df_ambito, x='ambito', y='horas', color="#FF4B4B") # Un color distinto
            
            st.write("### Tiempo por Proyecto (hs)")
            df_proyecto = df_filtrado.groupby('sector')['horas'].sum().reset_index()
            st.bar_chart(df_proyecto, x='sector', y='horas')
            
        with col_g2:
            st.write("### Tiempo por Tarea (hs)")
            df_tarea = df_filtrado.groupby('tarea')['horas'].sum().reset_index()
            st.bar_chart(df_tarea, x='tarea', y='horas')
            
            # Tabla de registros recientes con notas
            st.write("### Últimos 5 registros (Detalle)")
            st.dataframe(df_filtrado.sort_values(by=['fecha', 'hora'], ascending=False)[['fecha', 'sector', 'tarea', 'imprevisto', 'nota']].head(5), use_container_width=True)

    else:
        st.info("Aún no hay registros o las columnas no están configuradas correctamente en Google Sheets.")