import re
import spacy
from difflib import get_close_matches

nlp = spacy.load("es_core_news_md")

# Diccionario simple
INTENT_KEYWORDS = {
    "saludo": ["hola", "buenas", "buenos", "hey"],
    "criptomoneda": ["bitcoin", "btc", "cripto", "criptomonedas", "ethereum"],
    "acciones": ["acción", "acciones", "bolsa", "cedear", "mercado"],
    "plazo_fijo": ["plazo fijo", "plazofijo", "plazo", "plazos fijos"],
    "cuenta_remunerada": ["cuenta remunerada", "cuentas remuneradas"],
    "dolar": ["dolar", "dólar", "usd"],
    "dolar_historico": ["dólar histórico ", "dolar historico", "gráfico dólar", "usd histórico"],
    "riesgo_pais": ["riesgo país", "riesgo pais", "riesgo"],
    "riesgo_pais_historico": ["riesgo país histórico", "riesgo pais historico", "riesgo histórico", "historico", "histórico"],
    "inflacion": ["inflacion", "inflación", "ipc", "inflación mensual"],
    "inflacion_interanual": ["interanual", "inflación interanual", "inflacion interanual"],
    "uva": ["uva", "valor uva", "índice uva", "indice uva"],
    "inicio": ["inicio", "menu", "menú", "volver", "home"]
}

def limpiar_texto(texto):
    # Eliminar emojis y símbolos no alfabéticos
    texto = re.sub(r"[^\w\sáéíóúñü]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip().lower()

def _keyword_intent(mensaje):
    texto = mensaje.lower()
    for intent, keys in INTENT_KEYWORDS.items():
        for k in keys:
            if k in texto:
                return intent

    tokens = [t.lemma_.lower() for t in nlp(texto) if not t.is_stop and t.is_alpha]
    flat_keys = [k for keys in INTENT_KEYWORDS.values() for k in keys]
    for tok in tokens:
        close = get_close_matches(tok, flat_keys, n=1, cutoff=0.8)
        if close:
            for intent, keys in INTENT_KEYWORDS.items():
                if close[0] in keys:
                    return intent
    return None

def procesar_texto(mensaje, context=None):
    """
    Retorna (intent, entities)
    entities: dict por ejemplo {"FECHA": "2025-09-30", "PERIODO": "interanual"}
    """
    if not mensaje:
        return "desconocido", {}

    mensaje_limpio = limpiar_texto(mensaje)
    intent_kw = _keyword_intent(mensaje_limpio)
    if intent_kw:
        return intent_kw, {}

    # Fallback Semántico
    doc = nlp(mensaje_limpio)
    entities = {}

    for ent in doc.ents:
        entities.setdefault(ent.label_, []).append(ent.text)

    best_intent = None
    best_score = 0.0

    for intent, keys in INTENT_KEYWORDS.items():
        for k in keys:
            score = nlp(k).similarity(doc)
            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score < 0.65:
        best_intent = "desconocido"

    return best_intent, entities

def es_consulta_directa(mensaje):
    claves = [
        "ranking",
        "top",
        "mejores",
        "lista",
        "ver",
        "mostrar"
    ]
    return any(k in mensaje.lower() for k in claves)