from __future__ import annotations

import json
import os
import time
from pathlib import Path

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

RESULTS_DIR = Path(__file__).parent.parent / "results"
FORECASTS_FILE = RESULTS_DIR / "forecasts.json"

MODEL = "gemini-3-flash-preview"

SYSTEM_PROMPT = """Eres un agente especializado en analisis de costos de equipos de construccion.
Tienes acceso a:
1. Resultados de un modelo estadistico (OLS + Monte Carlo) que predice costos de Equipo1 y Equipo2
   basado en precios de materias primas (X, Y, Z).
2. Datos historicos de precios (2010-2023).
3. Capacidad de buscar contexto externo de mercado.

Tu rol es ayudar al evaluador a entender los resultados del analisis y responder preguntas
sobre proyecciones, metodologia, y contexto de mercado.

Cuando respondas:
- Se preciso con los numeros del modelo
- Distingue claramente entre resultados del modelo y contexto externo de mercado
- Si el usuario pregunta sobre metodologia, explica con claridad tecnica pero accesible
- Si preguntan sobre la diferencia entre IA convencional y agente de IA, explica el concepto
  usando este mismo sistema como ejemplo concreto

Usa las herramientas disponibles para obtener informacion actualizada antes de responder."""


def _load_forecasts() -> dict:
    if FORECASTS_FILE.exists():
        with open(FORECASTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_forecast(equipo: str, mes: str = "") -> str:
    """Retorna la proyeccion de costos de un equipo para los proximos 6 meses.
    Incluye percentiles P10, P25, mediana (P50), P75 y P90 por mes.
    Usalo cuando el usuario pregunte sobre costos futuros o proyecciones.

    Args:
        equipo: Nombre del equipo. Valores posibles: Equipo1, Equipo2.
        mes: Mes en formato YYYY-MM (ej: 2024-01). Dejar vacio para todos los meses.

    Returns:
        Tabla de proyeccion mensual con percentiles.
    """
    try:
        data = _load_forecasts()
        if not data:
            return (
                "Los resultados de proyeccion aun no estan disponibles. "
                "Ejecuta primero el notebook 03_modeling_forecasting.ipynb."
            )

        # Normalizar: "Equipo 1" → "Equipo1", "equipo1" → "Equipo1"
        equipo_norm = equipo.replace(" ", "").strip().capitalize()
        if not equipo_norm.startswith("Equipo"):
            equipo_norm = "Equipo" + equipo_norm

        monthly_data = data.get("proyeccion_mensual", {}).get(f"Price_{equipo_norm}", [])
        if not monthly_data:
            return f"No se encontro proyeccion para {equipo}."

        if mes:
            monthly_data = [m for m in monthly_data if m["mes"] == mes]
            if not monthly_data:
                return f"No hay proyeccion para {equipo} en el mes {mes}."

        metadata = data.get("metadata", {})
        lines = [
            f"Proyeccion de costos -- {equipo}",
            f"Horizonte: {metadata.get('forecast_horizon', 'N/A')}",
            f"Metodo: {metadata.get('metodo_equipos', 'N/A')}",
            "",
            f"{'Mes':<12} {'P10':>8} {'P25':>8} {'Mediana':>10} {'P75':>8} {'P90':>8}",
            "-" * 56,
        ]
        for row in monthly_data:
            lines.append(
                f"{row['mes']:<12} {row['p10']:>8.2f} {row['p25']:>8.2f} "
                f"{row['mediana']:>10.2f} {row['p75']:>8.2f} {row['p90']:>8.2f}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Error al obtener proyeccion: {e}"


def get_model_info(aspecto: str = "") -> str:
    """Retorna informacion sobre el modelo estadistico: variables, metricas, metodologia u horizonte.
    Usalo cuando el usuario pregunte sobre el modelo, su precision o metodologia.

    Args:
        aspecto: Aspecto a consultar. Valores posibles: variables, metricas, metodologia, horizonte.
                 Dejar vacio para toda la informacion.

    Returns:
        Descripcion del aspecto solicitado del modelo.
    """
    try:
        data = _load_forecasts()
        metricas = data.get("modelo_metricas", {})

        sections = {
            "variables": """Variables seleccionadas por el modelo:
El analisis combino correlacion de Pearson/Spearman, causalidad de Granger, Lasso y OLS con p-values.
Criterio: significativa en al menos 2 de los 3 metodos.

- Equipo1: Price_X (beta=0.199), Price_Y (beta=0.800)
- Equipo2: Price_X (beta=0.333), Price_Y (beta=0.336), Price_Z (beta=0.332)""",

            "metricas": (
                "Metricas de evaluacion (validacion cruzada temporal -- TimeSeriesSplit, 5 folds):\n\n"
                + (
                    "\n".join(
                        f"{target.replace('Price_', '')}:\n"
                        + "\n".join(f"  {k}: {v:.4f}" for k, v in m.items())
                        for target, m in metricas.items()
                    )
                    if metricas
                    else "Ejecuta el notebook 03 para obtener las metricas."
                )
            ),

            "metodologia": """Metodologia de modelado:

1. SELECCION DE VARIABLES (notebook 02):
   - Correlacion Pearson y Spearman: relaciones lineales y monotonicas
   - Prueba de Granger: causalidad temporal con rezago hasta 10 dias
   - Regresion Lasso (L1): regularizacion que elimina variables irrelevantes
   - Regresion OLS con p-values: significancia estadistica formal

2. MODELO PREDICTIVO (notebook 03):
   - Regresion Lineal OLS (statsmodels) -- interpretable y con IC formales
   - Evaluacion: TimeSeriesSplit 5 folds (respeta el orden temporal)
   - Validaciones: Johansen (cointegracion), Ljung-Box (residuos), Rolling OLS (estabilidad)

3. PROYECCION DE MATERIAS PRIMAS:
   - Competencia ARIMA vs Holt; ganador por RMSE minimo en test de 3 meses
   - Intervalos de confianza al 80% y 95%

4. PROYECCION DE EQUIPOS:
   - Simulacion Monte Carlo (1,000 realizaciones)
   - Resultado: P10, P25, P50, P75, P90 por mes""",

            "horizonte": """Justificacion del horizonte de proyeccion (6 meses = 126 dias habiles):

- Estadistica: los IC de ARIMA crecen con el tiempo; mas alla de 6 meses la incertidumbre
  supera el valor informacional de la proyeccion.
- Operacional: ciclos trimestrales de planificacion en construccion (2 ciclos de revision).
- Validacion: el 100% de los valores reales de Price_X (124 obs, sep-23 a feb-24)
  cayeron dentro del IC 80%, confirmando calibracion adecuada.""",
        }

        if aspecto and aspecto in sections:
            return sections[aspecto]
        return "\n\n---\n\n".join(f"[{k.upper()}]\n{v}" for k, v in sections.items())
    except Exception as e:
        return f"Error al obtener informacion del modelo: {e}"


def search_market_context(query: str) -> str:
    """Busca contexto externo de mercado sobre materias primas, sector constructor o macroeconomia.
    Usalo cuando el usuario quiera complementar el analisis con informacion de mercado.

    Args:
        query: Termino de busqueda. Ejemplos: petroleo 2024, construccion Colombia, inflacion.

    Returns:
        Contexto de mercado relevante para el query.
    """
    try:
        # Desactivar con MARKET_SEARCH=off en .env para no consumir tokens en pruebas
        if os.getenv("MARKET_SEARCH", "on").lower() == "off":
            return f"[Busqueda desactivada] Activa MARKET_SEARCH=on en .env para consultar: '{query}'"

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt = (
            f"Proporciona contexto de mercado relevante sobre: '{query}'. "
            f"Enfocate en el impacto sobre proyectos de construccion y equipos pesados en Colombia, "
            f"periodo 2023-2024. Maximo 5 puntos concisos."
        )
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=300),
        )
        return response.text
    except Exception as e:
        return f"Error en busqueda de mercado: {e}"


AGENT_TOOLS = [get_forecast, get_model_info, search_market_context]


class EquipmentCostAgent:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY no encontrada. "
                "Configura tu API key de Google AI Studio en el archivo .env."
            )
        self._client = genai.Client(api_key=api_key)
        self._tool_map = {t.__name__: t for t in AGENT_TOOLS}
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=AGENT_TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        self._session = self._client.chats.create(model=MODEL, config=self._config)

    def _send_with_retry(self, message, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                return self._session.send_message(message)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait = 40 * (attempt + 1)
                    print(f"\n  [Cuota excedida — reintentando en {wait}s...]", flush=True)
                    time.sleep(wait)
                else:
                    raise

    def chat(self, user_message: str) -> str:
        response = self._send_with_retry(user_message)

        # Loop agentico: invocar tools hasta obtener respuesta de texto final
        while True:
            fn_calls = [
                part.function_call
                for part in response.candidates[0].content.parts
                if part.function_call
            ]
            if not fn_calls:
                break

            fn_parts = []
            for fc in fn_calls:
                tool = self._tool_map.get(fc.name)
                result = tool(**fc.args) if tool else f"Herramienta no encontrada: {fc.name}"
                fn_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fc.name,
                            response={"result": result},
                        )
                    )
                )
            response = self._send_with_retry(fn_parts)

        return response.text

    def reset(self):
        self._session = self._client.chats.create(model=MODEL, config=self._config)
        print("Conversacion reiniciada.")

    def run(self):
        print("Agente de Costos de Equipos — Dataknow")
        print("Comandos: 'salir' para terminar, 'reset' para nueva sesion\n")

        while True:
            try:
                user_input = input("Tu: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nHasta luego.")
                break

            if not user_input:
                continue
            if user_input.lower() in ("salir", "exit", "quit"):
                print("Hasta luego.")
                break
            if user_input.lower() == "reset":
                self.reset()
                continue

            print("\nAgente: ", end="", flush=True)
            try:
                print(self.chat(user_input))
            except Exception as e:
                print(f"[Error: {e}]")
            print()


def main():
    EquipmentCostAgent().run()


if __name__ == "__main__":
    main()
