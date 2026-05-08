import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from zoneinfo import ZoneInfo
from datetime import datetime
import subprocess

TZ_AR = ZoneInfo("America/Argentina/Buenos_Aires")

def now_ar():
    return datetime.now(TZ_AR).replace(tzinfo=None)

def obtener_fecha_commit():
    try:
        return subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=format:%d/%m/%Y'],
            text=True
        ).strip()
    except:
        return now_ar().strftime("%d/%m/%Y")

fecha_commit = obtener_fecha_commit()

# Configuración de la página
st.set_page_config(
    page_title="Calculadora Nacionalidad Española - Córdoba",
    page_icon="🇪🇸",
    layout="wide"
)

def inject_ga(measurement_id: str):
    st.components.v1.html(
        f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{measurement_id}', {{ 'anonymize_ip': true }});
        </script>
        """,
        height=0,
    )

inject_ga("G-4QDSBC0514")


# Función para cargar y limpiar los datos
@st.cache_data(ttl=600)  # 10 minutos
def cargar_datos():
    # Leer el CSV (skiprows=1 para saltar la fila de título)
    df = pd.read_csv('resoluciones.csv', skiprows=1)
    
    # Limpiar columnas innecesarias
    df = df[['Anexo ', 'Número de expediente ', 'Fecha Presentación', 
             'Fecha Notificación Mail', 'Fecha Resolución', 'Observaciones']]
    
    # Renombrar columnas
    df.columns = ['Anexo', 'Num_Expediente', 'Fecha_Presentacion', 
                  'Fecha_Notificacion', 'Fecha_Resolucion', 'Observaciones']
    
    # Convertir fechas
    df['Fecha_Presentacion'] = pd.to_datetime(df['Fecha_Presentacion'], format='%d/%m/%Y', errors='coerce')
    df['Fecha_Resolucion'] = pd.to_datetime(df['Fecha_Resolucion'], format='%d/%m/%Y', errors='coerce')
    df['Fecha_Notificacion'] = pd.to_datetime(df['Fecha_Notificacion'], format='%d/%m/%Y', errors='coerce')
    
    # Filtrar solo casos resueltos
    df_resueltos = df[df['Fecha_Resolucion'].notna()].copy()
    
    # Calcular días de espera
    df_resueltos['Dias_Espera'] = (df_resueltos['Fecha_Resolucion'] - df_resueltos['Fecha_Presentacion']).dt.days
    
    # Calcular meses de espera
    df_resueltos['Meses_Espera'] = df_resueltos['Dias_Espera'] / 30.44  # Promedio de días por mes
    
    return df, df_resueltos

# Cargar datos
df_completo, df_resueltos = cargar_datos()

st.sidebar.write("Total presentados", len(df_completo))
st.sidebar.write("No incluidos en el cálculo", len(df_completo) - len(df_resueltos))
st.sidebar.write("Casos usados:", len(df_resueltos))
st.sidebar.write("Mediana meses:", round(df_resueltos['Meses_Espera'].median(), 1))


# Título principal
st.title("Calculadora de Nacionalidad Española")
st.subheader("Trámites presentados en Córdoba, Argentina")

# Sidebar para navegación
st.sidebar.title("Navegación")
opcion = st.sidebar.radio(
    "Selecciona una opción:",
    ["📅 Calcular mi fecha estimada", "📊 Estadísticas generales"]
)

# ===== OPCIÓN 1: CALCULAR FECHA ESTIMADA =====
if opcion == "📅 Calcular mi fecha estimada":
    st.header("Calculá tu fecha estimada de resolución")

    # Input de fecha (ancho completo)
    fecha_presentacion = st.date_input(
        "¿Cuándo presentaste tu trámite?",
        value=now_ar().date(),
        min_value=datetime(2022, 1, 1).date(),
        max_value=now_ar().date()
    )


    # Botón (UNA sola vez)
    if st.button(
        "🔮 Calcular fecha estimada",
        type="primary",
        key="btn_calcular_fecha"
    ):
            
            # Estadísticas de tiempos
            dias_promedio = df_resueltos['Dias_Espera'].mean()
            dias_mediana = df_resueltos['Dias_Espera'].median()
            meses_promedio = df_resueltos['Meses_Espera'].mean()
            meses_mediana = df_resueltos['Meses_Espera'].median()
            
            # Percentiles
            #p25 = df_resueltos['Dias_Espera'].quantile(0.25)
            #p75 = df_resueltos['Dias_Espera'].quantile(0.75)

            p45 = df_resueltos['Dias_Espera'].quantile(0.45)
            p95 = df_resueltos['Dias_Espera'].quantile(0.95)
            
            # Calcular fecha estimada (usando mediana)
            fecha_estimada_mediana = fecha_presentacion + timedelta(days=int(dias_mediana))
            #fecha_estimada_p25 = fecha_presentacion + timedelta(days=int(p25))
            #fecha_estimada_p75 = fecha_presentacion + timedelta(days=int(p75))
            fecha_estimada_p45 = fecha_presentacion + timedelta(days=int(p45))
            fecha_estimada_p95 = fecha_presentacion + timedelta(days=int(p95))
            
            # Mostrar resultados
            st.success("✅ Cálculo completado")
            
            # Métricas principales
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric(
                    "📊 Estimación basada en casos completos (mediana)",
                    fecha_estimada_mediana.strftime("%d/%m/%Y"),
                    f"{int(meses_mediana)} meses aprox.",
                    help="Calculada solo con trámites que tienen fechas completas. No contempla expedientes con datos faltantes."
                )

                        
                with col_b:
                    st.metric(
                        "⚡ Escenario optimista (P45)",
                        fecha_estimada_p45.strftime("%d/%m/%Y"),
                        f"{int(p45/30.44)} meses",
                        help="El 45% de los trámites históricos se resolvió antes de esta fecha. Representa un escenario favorable."
                    )

                    with col_c:
                        st.metric(
                            "🛡️ Escenario más probable hoy (P95)",
                            fecha_estimada_p95.strftime("%d/%m/%Y"),
                            f"{int(p95/30.44)} meses",
                            help="El 95% de los trámites históricos se resolvió en este plazo o antes. Es el escenario más confiable cuando hay datos incompletos."
                        )

            # Información adicional
            st.info(f"""
            📌 **Información importante:**
            
            - **Tiempo promedio:** {int(meses_promedio)} meses ({int(dias_promedio)} días)
            - **Tiempo mediano:** {int(meses_mediana)} meses ({int(dias_mediana)} días)
            - **Rango más común:** Entre {int(p45/30.44)} y {int(p95/30.44)} meses
            
            💡 La fecha estimada está basada en {len(df_resueltos)} casos resueltos del grupo de WhatsApp.
            """)
            
            # Distribución de tiempos
            st.subheader("📈 Distribución de tiempos de resolución")
            
            fig_hist = px.histogram(
                df_resueltos,
                x='Meses_Espera',
                nbins=30,
                title='¿Cuánto tiempo tardan los trámites?',
                labels={'Meses_Espera': 'Meses de espera', 'count': 'Cantidad de casos'},
                color_discrete_sequence=['#1f77b4']
            )
            
            # Agregar líneas de referencia
            fig_hist.add_vline(x=meses_mediana, line_dash="dash", line_color="red", 
                              annotation_text=f"Mediana: {int(meses_mediana)} meses")
            fig_hist.add_vline(x=meses_promedio, line_dash="dash", line_color="green",
                              annotation_text=f"Promedio: {int(meses_promedio)} meses")
            
            st.plotly_chart(fig_hist, width='stretch')
    
# ⬅️ ESTO VA FUERA DEL IF DEL BOTÓN
    with st.expander("ℹ️ Cómo funciona esta calculadora", expanded=False):
        st.markdown(f"""
        Calculadora basada en **{len(df_resueltos)} casos resueltos** reales del grupo de WhatsApp.

        La fecha estimada usa la **mediana** de tiempos históricos (más confiable que el promedio).

        💡 *Esto es solo una estimación. Los tiempos pueden variar.*
        """)

# ===== OPCIÓN 2: ESTADÍSTICAS GENERALES =====
else:
    st.header("Estadísticas Generales del Proceso")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total presentados", len(df_completo))
    
    with col2:
        st.metric("✅ Resueltos", len(df_resueltos))
    
    with col3:
        st.metric("⏳ No incluidos en el cálculo", len(df_completo) - len(df_resueltos))
    
    with col4:
        porcentaje_resueltos = (len(df_resueltos) / len(df_completo)) * 100
        st.metric("% Resueltos", f"{porcentaje_resueltos:.1f}%")
    
    st.divider()
    
    # Últimas resoluciones
    st.subheader("🔔 Últimas 10 resoluciones")
    
    ultimas = df_resueltos.nlargest(10, 'Fecha_Resolucion')[
        ['Fecha_Presentacion', 'Fecha_Resolucion', 'Meses_Espera', 'Anexo', 'Observaciones']
    ].copy()
    
    ultimas['Fecha_Presentacion'] = ultimas['Fecha_Presentacion'].dt.strftime('%d/%m/%Y')
    ultimas['Fecha_Resolucion'] = ultimas['Fecha_Resolucion'].dt.strftime('%d/%m/%Y')
    ultimas['Meses_Espera'] = ultimas['Meses_Espera'].round(1)
    ultimas.columns = ['Fecha Presentación', 'Fecha Resolución', 'Meses', 'Anexo', 'Observaciones']
    
    st.dataframe(ultimas, width='stretch', hide_index=True)
    
    st.divider()
    
    # Gráficos
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Tendencia temporal
        st.subheader("📈 Tendencia de resoluciones por mes")
        
        df_temporal = df_resueltos.copy()
        df_temporal['Mes_Resolucion'] = df_temporal['Fecha_Resolucion'].dt.to_period('M').astype(str)
        
        resueltos_por_mes = df_temporal.groupby('Mes_Resolucion').size().reset_index(name='Cantidad')
        
        fig_tendencia = px.bar(
            resueltos_por_mes,
            x='Mes_Resolucion',
            y='Cantidad',
            title='Resoluciones por mes',
            labels={'Mes_Resolucion': 'Mes', 'Cantidad': 'Casos resueltos'},
            color_discrete_sequence=['#2ecc71']
        )
        
        st.plotly_chart(fig_tendencia, width='stretch')
    
    with col_b:
        # Distribución por anexo
        st.subheader("📋 Distribución por tipo de Anexo")
        
        anexos = df_resueltos['Anexo'].value_counts().reset_index()
        anexos.columns = ['Anexo', 'Cantidad']
        
        fig_anexos = px.pie(
            anexos,
            values='Cantidad',
            names='Anexo',
            title='Casos por tipo de Anexo',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        st.plotly_chart(fig_anexos, width='stretch')
    
    st.divider()
    
    # Estadísticas de tiempo por anexo
    st.subheader("⏱️ Tiempos promedio por tipo de Anexo")
    
    tiempos_anexo = df_resueltos.groupby('Anexo').agg({
        'Meses_Espera': ['mean', 'median', 'count']
    }).round(1)
    
    tiempos_anexo.columns = ['Promedio (meses)', 'Mediana (meses)', 'Cantidad de casos']
    tiempos_anexo = tiempos_anexo.reset_index()
    
    st.dataframe(tiempos_anexo, width='stretch', hide_index=True)
    
    # Box plot de tiempos
    #st.subheader("📊 Distribución de tiempos de espera")
    
    #fig_box = px.box(
    #    df_resueltos,
    #    x='Anexo',
    #    y='Meses_Espera',
    #    title='Distribución de tiempos por Anexo',
    #    labels={'Meses_Espera': 'Meses de espera', 'Anexo': 'Tipo de Anexo'},
    #    color='Anexo',
    #    color_discrete_sequence=px.colors.qualitative.Pastel
    #)
    
    #st.plotly_chart(fig_box, width='stretch') 

st.divider()
st.caption(f"""
💡 **Nota**  
Esta aplicación usa datos reales del grupo de WhatsApp de solicitantes en Córdoba.  
Las estimaciones son aproximadas y pueden variar según múltiples factores.

📊 **Última actualización:** {fecha_commit}
""")

st.divider()

st.caption("""
🤍 **Proyecto independiente**  
Si esta herramienta te fue útil y querés colaborar (opcional):  
**Alias:** alanmonti.mp
""")

st.divider()

st.caption("""
👤 **Alan Montis**  
📧 alanmonti92@gmail.com  
🔗 https://www.linkedin.com/in/alanmontis/  
💻 https://github.com/AlanMonti92
""")
