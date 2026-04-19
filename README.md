# Gestión de Costos Operativos — Proyecto de Construcción

Prueba técnica para Científico de Datos Senior — Dataknow  
Modelo predictivo de costos de equipos a partir de precios de materias primas,
con agente conversacional de IA para exposición de resultados.

---

## Estructura del proyecto

```
dataknow/
├── notebooks/
│   ├── 01_eda.ipynb                     # Análisis exploratorio de datos
│   ├── 02_feature_selection.ipynb       # Selección estadística de variables
│   └── 03_modeling_forecasting.ipynb    # Modelado OLS + ARIMA + Monte Carlo
├── src/
│   ├── __init__.py
│   ├── data_loader.py                   # Carga y limpieza de los CSVs
│   └── agent.py                         # Agente conversacional (Gemini API)
├── results/
│   ├── figures/                         # Gráficas generadas por los notebooks
│   ├── selected_features.json           # Variables seleccionadas
│   └── forecasts.json                   # Proyecciones de costos
├── reports/
│   └── informe.md                       # Informe completo
├── architecture/
│   └── aws_architecture.drawio          # Diagrama de arquitectura AWS
├── Prueba tecnica Senior/
│   └── data/                            # CSVs de datos históricos
├── pyproject.toml                       # Dependencias (uv)
├── .env.example                         # Template de variables de entorno
└── .gitignore
```

---

## Configuración del entorno

### Requisitos
- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) (gestor de paquetes moderno)

### Instalación

```bash
# Instalar uv si no lo tienes
pip install uv

# Crear entorno virtual e instalar dependencias
uv sync

# Activar el entorno
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows
```

### Configurar API key

```bash
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY (Google AI Studio)
```

---

## Ejecución — Orden recomendado

### 1. Verificar carga de datos

```bash
python -m src.data_loader
```

### 2. Ejecutar notebooks en orden

```
notebooks/01_eda.ipynb                # EDA — ~5 min
notebooks/02_feature_selection.ipynb  # Selección de variables — ~10 min
notebooks/03_modeling_forecasting.ipynb  # Modelado y proyección — ~15 min
```

> El notebook 03 requiere que el notebook 02 haya generado `results/selected_features.json`.

### 3. Lanzar el agente conversacional

```bash
uv run python -m src.agent
```

Preguntas de ejemplo para el agente:
- `¿Cuánto se espera que cueste el Equipo 1 en enero 2024?`
- `¿Cuál materia prima tiene mayor impacto en el Equipo 2?`
- `¿Qué tan preciso es el modelo?`
- `¿Hay alguna tendencia de mercado en el sector construcción?`



---

## Arquitectura Cloud (AWS)

Ver `architecture/aws_architecture.drawio` para el diagrama completo.

**Componentes principales:**
- **Amazon S3**: almacenamiento de CSVs históricos, resultados y Data Lake (Parquet)
- **AWS Glue**: pipeline ETL de ingesta, limpieza y transformación
- **Amazon Redshift**: almacén analítico para consultas históricas
- **Amazon SageMaker**: entrenamiento, registro y exposición del modelo (Studio + Training Jobs + Endpoint)
- **AWS Fargate / ECS**: despliegue del agente conversacional como contenedor
- **AWS Lambda**: trigger de re-entrenamiento mensual automático
- **Amazon API Gateway**: gateway para exposición segura de la API
- **Amazon QuickSight**: dashboard de proyecciones para gerencia

---

## Tecnologías utilizadas

| Categoría | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Gestión de dependencias | uv + pyproject.toml |
| Análisis de datos | pandas, numpy, statsmodels |
| Machine Learning | scikit-learn, pmdarima |
| Visualización | matplotlib, seaborn, plotly |
| Agente de IA | Google Gemini API (gemini-3.1-flash.preview) |
| Cloud (arquitectura) | Amazon Web Services (AWS) |
| Control de versiones | Git + GitHub |
