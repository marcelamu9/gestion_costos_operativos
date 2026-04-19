# Gestión de Costos Operativos en Proyecto de Construcción

**Autor:** Lina Marcela Garzón — Prueba Técnica Dataknow  
**Fecha:** Abril 2026  
**Versión:** 1.0

---

## 1. Explicación del Caso

Una empresa del sector constructor enfrenta desviaciones presupuestales recurrentes debido a la incapacidad de anticipar el costo de adquisición de dos equipos críticos para sus operaciones en campo. La gerencia sospecha que estos precios tienen relación con los precios de ciertos insumos del mercado de materias primas, pero no cuenta con evidencia estadística formal ni con un modelo que lo respalde.

El objetivo del análisis es:

1. **Confirmar o refutar** la hipótesis de que los precios de los equipos están relacionados con los precios de las materias primas disponibles (X, Y, Z).
2. **Identificar** cuáles materias primas son estadísticamente determinantes para cada equipo, descartando las que constituyen ruido.
3. **Construir un modelo predictivo** reproducible que permita estimar el costo de los equipos a partir de los precios de mercado de las materias primas relevantes.
4. **Proyectar costos futuros** con horizonte temporal justificado e intervalos de confianza que cuantifiquen la incertidumbre de las estimaciones.
5. **Exponer los resultados** a través de un agente conversacional de IA que combine el análisis estadístico con contexto externo de mercado.

Los datos disponibles cubren el período **2010-01-04 a 2023-08-31** (3,530 registros diarios de días hábiles), sin valores nulos y con cobertura continua.

---

## 2. Supuestos

| # | Supuesto | Justificación |
|---|---|---|
| 1 | Los precios de las materias primas X, Y, Z están relacionados con los precios de los Equipos 1 y 2 | Hipótesis central del caso: se valida estadísticamente mediante correlación de Pearson, prueba de causalidad de Granger y regresión OLS con p-values formales |
| 2 | La relación entre materias primas y equipos es económicamente fundamentada, no solo estadística | Que dos variables se muevan juntas no implica que una cause a la otra. Se asume que las materias primas son insumos reales en la cadena de producción o adquisición de los equipos, por lo que un alza en su precio se traslada al precio final. Esta relación de negocio es lo que da validez operacional al modelo, más allá de la correlación observada |
| 3 | Las condiciones de mercado del período 2010–2023 seguirán siendo relevantes en el horizonte de proyección | El modelo aprende patrones históricos; si el mercado cambia estructuralmente (nuevo proveedor, sustituto tecnológico), la precisión se vería afectada |
| 4 | La relación entre materias primas y equipos es estable en el tiempo | Se valida con análisis de residuales; el período COVID-19 (2020–2021) genera mayor volatilidad pero no rompe la estructura de la relación de forma permanente |
| 5 | Los precios de las materias primas son conocidos antes de necesitar el precio del equipo | Condición operacional indispensable: el modelo solo es útil si se puede alimentar con los precios de X, Y, Z antes de tomar la decisión de compra del equipo |


---

## 3. Formas para Resolver el Caso y la Opción Tomada

Para responder la pregunta de negocio se evaluaron varios enfoques metodológicos antes de definir la estrategia final. El criterio de selección fue doble: precisión predictiva y capacidad de explicar los resultados a la gerencia sin requerir conocimiento técnico previo.

**Regresión lineal (OLS / Ridge / Lasso):** Es el enfoque para medir la relación entre materias primas y precio de equipos. Entrega coeficientes interpretables, se puede decir cuánto sube el precio del equipo por cada unidad que sube la materia prima y permite validar la significancia estadística con p-values formales. Se eligió como modelo principal por su transparencia y por ser el estándar en análisis de consultoría donde los resultados deben ser auditables.

**Modelos de series de tiempo (ARIMA/SARIMA):** Estos modelos no usan las materias primas como input; proyectan una serie a partir de su propio comportamiento histórico. No son adecuados para explicar la relación entre variables, pero sí para proyectar hacia adelante cada materia prima de forma individual. Se usaron en esa función específica: generar los valores futuros de X, Y, Z que luego alimentan el modelo de regresión.

**ARIMAX / SARIMAX:** Combina la estructura temporal de ARIMA con variables externas. Es conceptualmente atractivo pero añade complejidad en la selección de órdenes y dificulta la interpretación de los coeficientes. Se descartó en favor de mantener los dos modelos separados (OLS para la relación, ARIMA para la proyección), lo que hace el análisis más modular y explicable.

**VAR (Vector Autoregression):** Modelo multivariado que captura relaciones bidireccionales entre series, es decir, no solo si X afecta al Equipo1, sino también si el Equipo1 afecta a X. Aunque técnicamente riguroso, agrega una complejidad de interpretación que va más allá del objetivo del caso. Se descartó por no agregar valor en este contexto específico.

### Enfoque seleccionado

Vale la pena señalar que OLS no es el enfoque tradicional para series de tiempo, donde se suele preferir modelos que capturen autocorrelación explícitamente. Sin embargo, su uso queda justificado en este caso porque las series de precios, una vez verificada la cointegración, mantienen una relación estable y no espuria en el largo plazo. Esto se validó formalmente con la prueba de Johansen (cointegración) y la prueba ADF (raíz unitaria), confirmando que aplicar OLS sobre series I(1) es estadísticamente válido y produce estimadores consistentes.

La estrategia final combina tres componentes encadenados:

| Componente | Método | Rol |
|---|---|---|
| Selección de variables | Correlación + Granger + Lasso + OLS | Identificar qué materias primas son realmente determinantes para cada equipo |
| Modelo predictivo | Regresión OLS | Cuantificar la relación y estimar el precio del equipo dado el precio de las materias primas |
| Proyección con incertidumbre | ARIMA + Monte Carlo (1,000 simulaciones) | Proyectar materias primas a 6 meses y propagar esa incertidumbre al precio del equipo |

Esta combinación permite responder las tres preguntas del negocio: qué materias primas importan, cuánto impactan, y cuál será el costo estimado con su rango de incertidumbre.

---

## 4. Resultados del Análisis de los Datos y los Modelos

### 4.1 Características de los datos

El conjunto de datos cubre el período 2010–2023 con 3,530 registros diarios de días hábiles, con cobertura continua. Lo más relevante al explorar las series es la magnitud de la variabilidad: todas las variables tanto materias primas como equipos muestran rangos amplios que hacen imposible gestionar el presupuesto de adquisición sin un modelo de referencia.

El comportamiento de las series de tiempo es muy similar entre las materias primas y equipos, por lo cual se hizo necesario probar que las correlaciones fueran reales y no correlaciones espurias.

| Variable | Mínimo | Máximo | Observación |
|---|---|---|---|
| Price_X | 19.33 | 127.98 | Alta volatilidad; multiplicó su valor por 6 en el período completo |
| Price_Y | 257.50 | 1,062.37 | Volatilidad media; picos pronunciados en 2021–2022 |
| Price_Z | 1,421.50 | 3,984.00 | Alta volatilidad; prácticamente duplicó su valor |
| Price_Equipo1 | 208.34 | 855.32 | Variabilidad significativa, correlacionada con X e Y |
| Price_Equipo2 | 566.00 | 1,703.96 | Mayor rango absoluto entre las variables objetivo |

Esta variabilidad confirma la necesidad del análisis: sin un modelo, la empresa está expuesta a desviaciones presupuestales de hasta el 300% entre el precio mínimo y máximo histórico de los equipos.

![Series de tiempo — materias primas y equipos 2010–2023](../results/figures/01_series_tiempo.png)

Durante la exploración también se identificaron algunos días faltantes en el calendario. Al revisar su distribución, se encontró que correspondían a festivos de fin de año semana entre Navidad y Año Nuevo, en los que los mercados no operan. Al tratarse de un patrón esperado y completamente consistente con el comportamiento habitual de los mercados financieros, no se consideró un problema de calidad de datos ni requirió imputación.

### 4.2 Selección de variables

No todas las materias primas disponibles son igualmente relevantes para cada equipo. Usar variables irrelevantes en el modelo introduce ruido y reduce su capacidad predictiva. Por eso se aplicó una metodología, donde cada método aborda el problema desde un ángulo distinto:

| Método | Qué mide |
|---|---|
| Correlación Pearson/Spearman | Si las variables se mueven juntas de forma lineal o monótona |
| Causalidad de Granger | Si el precio de la materia prima predice temporalmente al equipo (rezago hasta 10 días) |
| Regresión Lasso (L1) | Cuáles variables sobreviven cuando se penaliza la complejidad del modelo |
| Regresión OLS con p-values | Cuáles tienen significancia estadística formal una vez controladas las demás |

Una variable se considera relevante para un equipo si aparece como significativa en **al menos dos de los tres métodos** (Granger, Lasso y OLS). Esto con el fin de reducir el riesgo de incluir variables que sean significativas por azar en un solo test.

Los resultados de esta selección se guardan en `results/selected_features.json` y son el input directo del modelo OLS.

### 4.3 Métricas del modelo

El modelo OLS se evaluó con validación cruzada temporal (5 folds con `TimeSeriesSplit`), que respeta el orden cronológico de los datos para evitar que el modelo "vea el futuro" durante el entrenamiento. Este tipo de validación es más exigente que un split aleatorio y refleja mejor el rendimiento real en producción.

| Métrica | Equipo 1 | Equipo 2 |
|---|---|---|
| MAE (CV promedio) | 6.73 | 12.98 |
| RMSE (CV promedio) | 7.88 | 15.12 |
| R² (CV promedio) | 0.9758 | 0.9649 |
| R² (muestra completa) | 0.995 | 0.992 |

Un MAE de 6.7 sobre un rango de precios de 208–855 (Equipo 1) representa un error relativo de aproximadamente 1.5%, lo que es aceptable para planificación financiera. El R² superior a 0.96 en validación cruzada indica que el modelo explica más del 96% de la variabilidad del precio, usando únicamente los precios de las materias primas como input.

Los coeficientes del modelo son todos estadísticamente significativos (p < 0.001) y tienen una interpretación directa de negocio:

| Variable | β Equipo1 | β Equipo2 |
|---|---|---|
| constante | -0.082 | 1.228 |
| Price_X | 0.199 | 0.333 |
| Price_Y | 0.800 | — |
| Price_Y | — | 0.336 |
| Price_Z | — | 0.332 |

Para el **Equipo 1**, Price_Y es el insumo dominante: por cada unidad que sube Y, el precio del equipo sube 0.80 unidades. Price_X tiene una influencia más moderada (0.20). Para el **Equipo 2**, los tres insumos contribuyen de forma casi equilibrada (~0.33 cada uno), lo que significa que ninguna materia prima domina sola y el precio del equipo responde de manera más distribuida al mercado.

![Valores ajustados vs. valores reales — Equipo 1 y Equipo 2](../results/figures/08_fitted_vs_actual.png)

### 4.4 Validaciones formales del modelo OLS

Se realizaron tres pruebas estadísticas para confirmar que el modelo es sólido y que sus resultados no son un artefacto de las series de tiempo.

**Test de Johansen (cointegración):** Esta prueba verifica que la relación entre las variables no es espuria ,es decir, que no se trata de dos series que suben juntas simplemente porque el tiempo avanza, sino que existe un equilibrio de largo plazo entre ellas. Los resultados superan el valor crítico por un factor de ~30×, lo que constituye evidencia estadística abrumadora a favor de la cointegración.

| Sistema | Estadístico (r≤0) | Val. crítico 5% | Resultado |
|---|---|---|---|
| Equipo1 ~ X, Y | 1,430.59 | 29.80 | Cointegración confirmada |
| Equipo2 ~ X, Y, Z | 1,575.30 | 47.85 | Cointegración confirmada |

**Test de Ljung-Box (autocorrelación en residuales):** Verifica que los errores del modelo son ruido blanco, sin patrones temporales que el modelo haya dejado sin capturar. Todos los p-valores superan 0.05 en los rezagos 10, 20 y 40, lo que confirma que el OLS capturó toda la señal disponible en los datos.

**Rolling OLS (estabilidad de coeficientes, ventana 252 días):** Verifica que la relación entre materias primas y equipos no cambia con el tiempo. Los coeficientes de Price_Y y Price_Z se mantienen estables a lo largo de todo el período, lo que confirma que la relación es estructural y no un efecto temporal. Price_X muestra algo más de variabilidad, pues en ventanas cortas tiende a moverse junto con Y, dificultando separar su efecto individual; el coeficiente global sobre toda la muestra sigue siendo el más robusto.

En conjunto, estas tres pruebas validan que el modelo OLS no solo ajusta bien los datos históricos, sino que captura una relación económica real, estable y estadísticamente sólida entre las materias primas y el precio de los equipos.

### 4.5 Selección del modelo de proyección para materias primas

Para proyectar cada materia prima hacia adelante se evaluaron dos enfoques: ARIMA y Suavizamiento Exponencial de Holt con tendencia aditiva. La selección se hizo con un esquema de entrenamiento/test usando los últimos 63 días hábiles (~3 meses) como período de validación, eligiendo el modelo con menor RMSE en ese período, es decir, el que mejor predijo datos que no vio durante el entrenamiento.

El resultado varió por materia prima:

- **Price_X y Price_Z:** Ganó Holt. Estas series tienen tendencias recientes más informativas que su historia larga; Holt, al darle más peso a los datos recientes, captura mejor su dirección actual.
- **Price_Y:** Ganó ARIMA. La estructura de autocorrelación de esta serie es más compleja y ARIMA la modela mejor seleccionando automáticamente los órdenes que minimizan el AIC.

Para Holt se configuró el modelo para que mantenga la tendencia constante hacia adelante, sin frenarla artificialmente. Esto se justifica porque las series históricas muestran que cuando una materia prima sube o baja, esa dirección tiende a sostenerse durante meses, no revertirse de inmediato.

---

## 5. Proyección de Costos y Horizonte de Predicción

### 5.1 Horizonte elegido: 6 meses

Se proyectó un horizonte de **6 meses** (septiembre 2023 – febrero 2024), por tres razones:

**La incertidumbre crece con el tiempo.** Todo modelo de proyección pierde precisión a medida que se aleja del último dato conocido. En la práctica, los intervalos de confianza de las materias primas proyectadas ya abarcan ±30–40% del valor nominal al mes 6. Extender la proyección a 12 meses duplicaría ese rango, al punto en que la información dejaría de ser útil para tomar decisiones de compra.

**Los ciclos de planificación del sector.** Los proyectos de construcción usualmente planifican adquisiciones trimestralmente. Un horizonte de 6 meses cubre dos ciclos completos y permite una revisión intermedia en diciembre 2023, ajustando el presupuesto si los precios reales divergen del pronóstico.

**La vigencia del modelo.** El modelo se entrena con datos hasta agosto 2023. Proyectar más allá de 6 meses significa extrapolar tendencias que el modelo aprendió hace más de un año, lo que reduce progresivamente la credibilidad de los resultados.

### 5.2 Metodología de proyección

**Etapa 1 — Proyección de materias primas**

Para cada materia prima se evaluaron dos modelos usando los últimos 3 meses como período de prueba, seleccionando el que cometió menor error en datos que no había visto:

- **ARIMA**: identifica automáticamente los patrones de autocorrelación de la serie y proyecta con base en ellos. Es el modelo de referencia para series con comportamiento complejo.
- **Holt (tendencia aditiva, ventana 1 año)**: proyecta siguiendo la dirección reciente de la serie, dando más peso a los últimos 12 meses. Es especialmente útil cuando la serie tiene una tendencia clara que no queremos que el comportamiento de años anteriores distorsione.

Un ajuste adicional fue necesario para ARIMA en algunos casos: cuando el modelo descartaba la tendencia por criterios estadísticos internos, el pronóstico resultaba plano aunque la serie claramente venía subiendo o bajando. En esos casos, se calculó manualmente la dirección promedio de los últimos 12 meses y se aplicó como corrección, preservando la tendencia observable sin forzar el modelo.

**Etapa 2 — Proyección del precio del equipo con incertidumbre**

Las proyecciones de materias primas no son un número único sino un rango de posibilidades. Trasladar esa incertidumbre al precio del equipo requiere simulación Monte Carlo: se generaron 1,000 escenarios posibles, en cada uno se muestrea un precio de materia prima dentro de su rango proyectado, se aplica el modelo OLS y se obtiene un precio de equipo. El resultado es una distribución de 1,000 precios posibles de la que se extraen los percentiles P10, P25, P50, P75 y P90.

**Validación post-hoc**

Los datos reales de algunas materias primas para el período proyectado estaban disponibles, lo que permitió verificar qué tan bien calibradas estaban las proyecciones:

| Serie | Período validado | MAPE | % dentro IC 80% |
|---|---|---|---|
| Price_X | sep-23 - feb-24 (124 obs) | 8.9% | 100% |
| Price_Y | sep-01 - sep-12, 2023 (8 obs) | 1.2% | 100% |

El 100% de los valores reales cayó dentro del intervalo de confianza al 80%, lo que confirma que los intervalos están bien calibrados: son suficientemente amplios para cubrir la variabilidad real del mercado sin ser tan anchos que pierdan utilidad práctica.

### 5.3 Resultados de la proyección

**Equipo 1** — sep 2023 a feb 2024:

| Mes | P10 | P25 | Mediana | P75 | P90 |
|---|---|---|---|---|---|
| 2023-09 | 423.31 | 436.84 | 451.86 | 466.81 | 480.10 |
| 2023-10 | 390.18 | 418.62 | 449.42 | 480.07 | 507.75 |
| 2023-11 | 366.66 | 404.94 | 449.18 | 492.63 | 530.86 |
| 2023-12 | 345.03 | 394.51 | 448.48 | 502.68 | 552.68 |
| 2024-01 | 327.01 | 384.75 | 448.75 | 511.00 | 568.11 |
| 2024-02 | 310.19 | 377.01 | 448.43 | 520.61 | 584.30 |

**Equipo 2** — sep 2023 a feb 2024:

| Mes | P10 | P25 | Mediana | P75 | P90 |
|---|---|---|---|---|---|
| 2023-09 | 852.87 | 887.30 | 925.86 | 963.83 | 998.01 |
| 2023-10 | 783.45 | 846.55 | 913.73 | 981.77 | 1044.53 |
| 2023-11 | 736.10 | 815.08 | 903.89 | 992.71 | 1072.38 |
| 2023-12 | 695.48 | 788.82 | 894.93 | 1000.97 | 1098.03 |
| 2024-01 | 653.88 | 763.05 | 883.33 | 1002.36 | 1110.80 |
| 2024-02 | 623.29 | 743.63 | 874.91 | 1008.77 | 1125.55 |

![Proyección de costos — Equipo 1 y Equipo 2 con intervalos de confianza](../results/figures/10_forecast_equipos.png)

El **Equipo 1** muestra una mediana prácticamente estable alrededor de 449 durante todo el horizonte. La incertidumbre sí crece con el tiempo el rango P10–P90 pasa de ±28 unidades en septiembre a ±137 en febrero, pero el valor central se mantiene, lo que facilita la planificación.

El **Equipo 2** presenta una leve tendencia bajista en la mediana (de 926 a 875, aproximadamente −5.5%), impulsada por la proyección descendente de Price_Z. La incertidumbre es mayor en términos absolutos, creciendo de ±72 a ±251 unidades al mes 6.

**Recomendación presupuestal:** usar el **P75 como presupuesto base** y el **P90 como contingencia**, lo que garantiza cobertura para el 90% de los escenarios de mercado posibles. Los resultados completos están disponibles en `results/forecasts.json`.

---

## 6. Futuros Ajustes o Mejoras

El modelo es funcional y estadísticamente sólido, pero tiene margen de mejora en varios aspectos:

**Reentrenamiento periódico.** Cada mes sin actualización, el modelo pierde vigencia. El pipeline descrito en la arquitectura AWS (EventBridge + Lambda) ya contempla este ciclo automático, y debe priorizarse antes de cualquier otra mejora.

**Enriquecimiento de variables.** Incorporar variables exogenas como: el índice de precios al productor, tasa de cambio USD/COP, entre otras, esta parte tiene cabida a una investigación de acuerdo a los equyipos. Eto puede ayudar a capturar contexto macroeconómico que las materias primas X, Y, Z no reflejan directamente, mejorando la precisión.

**Modelos no lineales como siguiente paso.** Una vez estabilizado el modelo base, explorar Random Forest o XGBoost para capturar interacciones entre variables que OLS no modela.

A largo plazo, la mejora más estratégica sería conectar el sistema a APIs de proveedores de datos de mercado para eliminar la dependencia de archivos CSV y hacer el flujo completamente autónomo.

---

## 7. Apreciaciones y Comentarios del Caso

Combinar un modelo estadístico con un agente conversacional responde a un problema frecuente: los modelos se construyen pero no se usan porque los tomadores de decisiones no saben cómo consultarlos. El agente cierra esa brecha, haciendo que el pronóstico sea accesible para quien toma las decisiones de compra, sin requerir conocimiento técnico.

**IA convencional vs. Agente de IA.** El modelo OLS es un ejemplo de IA convencional: recibe un input (precios de materias primas) y produce un output (precio del equipo). No decide nada, no elige qué hacer, no tiene memoria entre llamadas. Es una función matemática que transforma datos en una predicción.

El agente construido en este proyecto es diferente. Ante una pregunta como *¿cuánto costará el Equipo 1 en febrero y qué factores de mercado lo afectan?*, el agente decide autónomamente invocar `get_forecast` para obtener los números del modelo y `search_market_context` para complementar con contexto externo; ejecuta ambas herramientas, observa los resultados, y construye una respuesta integrando las dos fuentes. Esto ilustra los cuatro conceptos clave: **autonomía** (decide qué herramienta usar sin intervención humana), **uso de herramientas** (accede a datos, APIs y resultados del modelo), **memoria** (mantiene el hilo de la conversación dentro de la sesión) y **capacidad de acción** (ejecuta código real, lee archivos, llama servicios externos). La diferencia esencial es que el modelo predice; el agente decide qué hacer con esa predicción y cómo presentarla.

---

## 8. Arquitectura de Despliegue en AWS

El diagrama completo se encuentra en `architecture/aws_architecture.drawio` (abrir con Draw.io en VS Code o en [draw.io](https://app.diagrams.net/)).

La arquitectura está organizada en cinco capas:

**1. Ingesta:** Los CSV históricos se cargan en Amazon S3 (`raw/`). Una instancia EC2 ejecuta `data_loader.py`, limpia los datos, alinea fechas y deposita el resultado en S3 (`processed/`).

**2. Almacenamiento:** Amazon S3 organiza los datos en tres prefijos: `raw/` para archivos originales, `processed/` para datos limpios y `results/` para forecasts y resultados del modelo.

**3. Machine Learning:** SageMaker Studio consume S3/processed para el análisis y entrenamiento. Los modelos se registran en el Model Registry con versionado y se despliegan como Serverless Endpoint con API REST para inferencia.

**4. Exposición:** API Gateway recibe las consultas, autentica y enruta a una función Lambda que ejecuta el agente (`agent.py`). El agente combina Gemini API para el razonamiento con el SageMaker Endpoint para predicciones en tiempo real y S3/results para forecasts precalculados.

**5. Consumo:** Amazon QuickSight lee de S3/results para el dashboard de gerencia. La CLI o Web App es el canal para consultas en lenguaje natural al agente.

**Re-entrenamiento automático:** EventBridge dispara una Lambda el primer día de cada mes, que enciende el EC2, espera a que procese datos nuevos y lo apaga. El ciclo continúa desde S3/processed hacia SageMaker.
