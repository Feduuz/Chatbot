from data.financial_api import (
    obtener_top5_criptos,
    obtener_listado_criptos,
    obtener_tasas_bcra,
    obtener_top5_acciones,
    obtener_listado_acciones
)

def obtener_datos_financieros(intencion, mensaje):
    mensaje = mensaje.lower()

    if intencion == "saludo":
        return "¡Hola! Soy tu asistente financiero 🤖. ¿Querés saber sobre criptomonedas, acciones o plazos fijos?"

    elif intencion == "criptomoneda":
        top5 = obtener_top5_criptos()
        respuesta = "💰 Las 5 criptomonedas con mayor capitalización son:\n\n"
        respuesta += "\n".join(top5)
        respuesta += "\n\n¿Te interesa saber sobre alguna criptomoneda diferente? (Sí/No)"
        return respuesta

    elif intencion == "acciones":
        top5 = obtener_top5_acciones()
        respuesta = "📈 Las 5 acciones con mayor capitalización son:\n\n"
        respuesta += "\n".join(top5)
        respuesta += "\n\n¿Querés saber sobre alguna acción diferente? (Sí/No)"
        return respuesta

    elif intencion == "plazo_fijo":
        tasas = obtener_tasas_bcra()
        if not tasas:
            return "⚠️ No pude obtener las tasas de plazo fijo en este momento. Probá más tarde."
        top5 = tasas[:5]
        respuesta = "🏦 Las 5 entidades con la tasa de plazo fijo más alta son:\n\n"
        for t in top5:
            respuesta += f"{t['banco']}: {t['tasa']:.2f}%\n"
        return respuesta

    elif intencion == "desconocido":
        return "No entendí muy bien 🤔. Probá preguntarme sobre criptomonedas, acciones o plazos fijos."

    else:
        return "Todavía no tengo información para esa consulta, pero pronto la agregaré 📊."
