import json
import requests
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

def normalizar_fecha(f):
    if not f:
        return None
    try:
        return datetime.strptime(f.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        return None

def consultar_ollama(
    mensaje: str,
    historial: list | None = None,
    contexto_datos: dict | list | None = None
):
    """
    - mensaje: texto del usuario
    - historial: mensajes previos (opcional)
    - contexto_datos: datos REALES obtenidos por API (opcional)
    """

    historial = historial or []

    # System prompt anti-alucinación
    system_prompt = (
        "Sos un asistente financiero argentino.\n"
        "Usá EXCLUSIVAMENTE los datos provistos por el sistema.\n"
        "No inventes valores, precios ni porcentajes.\n"
        "Si el dato no está disponible, decilo explícitamente.\n"
        "Respondé en español claro."
    )

    messages = [{"role": "system", "content": system_prompt}]

    # Inyectar datos reales si existen
    if contexto_datos is not None:
        messages.append({
            "role": "system",
            "content": (
                "Datos financieros reales (JSON):\n"
                f"{json.dumps(contexto_datos, ensure_ascii=False)}"
            )
        })

    # Historial previo
    messages.extend(historial[-10:])

    # Mensaje actual del usuario
    messages.append({"role": "user", "content": mensaje})

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    if contexto_datos is None:
        payload["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": "buscar_dato_financiero",
                    "description": "Devuelve datos financieros actuales o históricos.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "consulta": {"type": "string"},
                            "fecha": {"type": "string"}
                        },
                        "required": ["consulta"]
                    }
                }
            }
        ]

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"⚠️ Error al comunicarme con el modelo: {e}"

    message = data.get("message")
    if not message:
        return "⚠️ No pude generar una respuesta en este momento."

    # Respuesta directa (sin tools)
    if contexto_datos is not None:
        return message.get(
            "content",
            "No hay información disponible para esa consulta."
        )

    if "tool_calls" not in message:
        return message.get(
            "content",
            "No hay información disponible para esa consulta."
        )

    tool = message["tool_calls"][0]
    args_raw = tool["function"].get("arguments", {})

    try:
        args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
    except:
        args = {}

    consulta = args.get("consulta", "").lower()
    fecha = normalizar_fecha(args.get("fecha"))

    # Reutiliza APIs
    from data.financial_api import (
        obtener_top5_criptos,
        obtener_top5_acciones,
        obtener_cotizaciones_dolar,
        obtener_riesgo_pais,
        obtener_riesgo_pais_historico,
        obtener_indice_inflacion,
        obtener_indice_inflacion_interanual,
        obtener_indice_uva
    )

    resultado = []

    if "cripto" in consulta:
        resultado = obtener_top5_criptos()

    elif "acción" in consulta or "acciones" in consulta:
        resultado = obtener_top5_acciones()

    elif "dólar" in consulta or "dolar" in consulta:
        resultado = obtener_cotizaciones_dolar()

    elif "riesgo" in consulta:
        if fecha:
            fechas, valores = obtener_riesgo_pais_historico()
            if fecha in fechas:
                idx = fechas.index(fecha)
                resultado = [f"Riesgo País {fecha}: {valores[idx]} puntos"]
            else:
                resultado = ["No hay datos para esa fecha."]
        else:
            dato = obtener_riesgo_pais()
            resultado = [dato] if dato else ["No hay dato disponible."]

    elif "inflación" in consulta:
        fechas, valores, ultimo = obtener_indice_inflacion()
        resultado = [ultimo]

    elif "interanual" in consulta:
        fechas, valores, ultimo = obtener_indice_inflacion_interanual()
        resultado = [ultimo]

    elif "uva" in consulta:
        fechas, valores, ultimo = obtener_indice_uva()
        resultado = [ultimo]

    else:
        resultado = ["No entendí qué dato financiero consultar."]

    # Enviar resultado real al modelo para que redacte
    final_payload = {
        "model": MODEL,
        "messages": [
            *messages,
            {
                "role": "tool",
                "content": json.dumps(resultado, ensure_ascii=False),
                "tool_call_id": tool["id"]
            }
        ],
        "stream": False
    }

    try:
        final_response = requests.post(
            OLLAMA_URL,
            json=final_payload,
            timeout=60
        ).json()
    except:
        return "⚠️ Error al generar la respuesta final."

    return final_response.get("message", {}).get(
        "content",
        "No pude generar una respuesta final."
    )