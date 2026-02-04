# 🇪🇸 Calculadora de Nacionalidad Española - Córdoba

Aplicación web para estimar tiempos de resolución de trámites de nacionalidad española presentados en Córdoba, Argentina.

## 📋 Requisitos

- Python 3.8 o superior
- pip

## 🚀 Instalación y Uso Local

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Colocar el archivo CSV

Asegúrate de tener el archivo `resoluciones.csv` en la misma carpeta que `app.py`

### 3. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📊 Funcionalidades

### 📅 Calcular fecha estimada
- Ingresa tu fecha de presentación
- Obtén una estimación de cuándo se resolverá tu trámite
- Ve escenarios optimistas, probables y conservadores
- Basado en datos reales de casos resueltos

### 📈 Estadísticas generales
- Total de casos presentados y resueltos
- Últimas 10 resoluciones
- Tendencia de resoluciones por mes
- Distribución por tipo de Anexo
- Tiempos promedio por Anexo
- Gráficos interactivos

## 🚀 Deploy en Railway

### 1. Crear cuenta en Railway
Ve a [railway.app](https://railway.app) y crea una cuenta gratuita

### 2. Preparar el proyecto
Asegúrate de tener estos archivos:
- `app.py` (aplicación principal)
- `requirements.txt` (dependencias)
- `resoluciones.csv` (datos)

### 3. Deploy
1. Crea un nuevo proyecto en Railway
2. Conecta tu repositorio de GitHub o sube los archivos
3. Railway detectará automáticamente que es una app de Python
4. Agrega las siguientes variables de entorno en Railway:
   - No necesitas configurar nada especial

### 4. Configurar el comando de inicio
En Railway, ve a Settings > Deploy y asegúrate de que el comando de inicio sea:
```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## 📁 Estructura del proyecto

```
.
├── app.py              # Aplicación principal de Streamlit
├── requirements.txt    # Dependencias de Python
├── resoluciones.csv    # Datos de los trámites
└── README.md          # Este archivo
```

## 🔄 Actualizar datos

Para actualizar los datos:
1. Descarga el nuevo Google Sheets como CSV
2. Reemplaza el archivo `resoluciones.csv`
3. Si está en Railway, sube el nuevo archivo y redeploy

## 💡 Próximas mejoras (Fase 2)

- [ ] Conexión automática con Google Sheets API
- [ ] Actualización automática de datos
- [ ] Filtros por rango de fechas
- [ ] Comparación entre diferentes períodos
- [ ] Notificaciones cuando hay nuevas resoluciones

## 📝 Notas

- Los datos provienen del grupo de WhatsApp de solicitantes en Córdoba
- Las estimaciones son aproximadas basadas en datos históricos
- Los tiempos pueden variar según diversos factores

## 🤝 Contribuir

Si quieres mejorar la aplicación, siéntete libre de:
- Reportar bugs
- Sugerir nuevas funcionalidades
- Mejorar el código

---

Hecho con ❤️ para la comunidad de solicitantes de nacionalidad española en Córdoba By Alan Monti
