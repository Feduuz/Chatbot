from data.financial_api import (
    obtener_top5_criptos,
    obtener_listado_criptos,
    obtener_tasas_plazofijo,
    obtener_top5_acciones,
    obtener_listado_acciones,
    obtener_cuentas_remuneradas,
    obtener_cotizaciones_dolar,
    obtener_riesgo_pais
)

def obtener_datos_financieros(intencion, mensaje):
    mensaje = mensaje.lower()

    if intencion == "saludo":
        return "Un gusto. ¿Sobre qué tema te gustaría saber más?"

    elif intencion == "criptomoneda":
        top5 = obtener_top5_criptos()
        respuesta = "<b>💰 Las 5 criptomonedas con mayor capitalización son:</b><br><br>"
        for i, cripto in enumerate(top5, start=1):
            respuesta += f"{i}° {cripto}<br>"

        return respuesta


    elif intencion == "acciones":
        top5 = obtener_top5_acciones()
        respuesta = "<b>📈 Las 5 acciones con mayor capitalización son:</b><br><br>"
        for i, accion in enumerate(top5, start=1):
            respuesta += f"{i}° {accion}<br>"

        return respuesta


    elif intencion == "plazo_fijo":
        top_clientes, top_no_clientes = obtener_tasas_plazofijo()
        if not top_clientes and not top_no_clientes:
            return "⚠️ No pude obtener las tasas de plazo fijo en este momento. Probá más tarde."

        respuesta = "<b>🏦 Top 5 Tasas de Plazo Fijo más altas (según el BCRA):</b><br><br>"

        if top_clientes:
            respuesta += "<b>👤 **Para Clientes:**</b><br>"
            for i, t in enumerate(top_clientes, start=1):
                respuesta += f"{i}° {t['banco']}: TNA {t['tasa']:.2f}%<br>"

        respuesta += "<br><hr><br>"

        if top_no_clientes:
            respuesta += "<b>🚫 **Para No Clientes:**</b><br>"
            for i, t in enumerate(top_no_clientes, start=1):
                respuesta += f"{i}° {t['banco']}: TNA {t['tasa']:.2f}%<br>"

        return respuesta

    elif intencion == "cuenta_remunerada":
        cuentas = obtener_cuentas_remuneradas()
        if not cuentas:
            return "⚠️ No pude obtener los datos de cuentas remuneradas en este momento."

        respuesta = "<b>💵 Top 5 Cuentas Remuneradas (según ArgentinaDatos):</b><br><br>"
        for i, c in enumerate(cuentas, start=1):
            respuesta += f"{i}° <b>{c['entidad']}</b><br>"
            respuesta += f"🏦 TNA: {c['tna']}%<br>"
            tope = c['tope'] if c['tope'] not in [None, "None", "", 0] else " --- "
            respuesta += f"💰 Tope: ${tope}<br><br>"


        return respuesta

    elif intencion == "dolar":
        cotizaciones = obtener_cotizaciones_dolar()
        if not cotizaciones:
            return "⚠️ No pude obtener las cotizaciones del dólar en este momento."

        respuesta = "<b>💵 Cotizaciones del Dólar (Fuente Ámbito Financiero):</b><br><br>"

        for c in cotizaciones:
            respuesta += f"<b>Dólar {c['nombre']}</b><br>"
            respuesta += f"🟢 Compra: ${c['compra']}<br>"
            respuesta += f"🔴 Venta: ${c['venta']}<br>"
            respuesta += f"🕒 Última actualización: {c['fechaActualizacion']}<br><br>"

        return respuesta

    elif intencion == "riesgo_pais":
        datos = obtener_riesgo_pais()
        if not datos:
            return "⚠️ No pude obtener el valor del Riesgo País en este momento."

        respuesta = "<b>📊 Índice de Riesgo País (Argentina)</b><br><br>"
        respuesta += f"🇦🇷 Valor actual: <b>{datos['valor']}</b> puntos<br>"
        respuesta += f"🕒 Última actualización: {datos['fecha']}<br>"

        return respuesta


    elif intencion == "desconocido":
        return "No entendí muy bien 🤔. Probá preguntarme sobre criptomonedas, acciones, cuentas remuneradas o plazos fijos."

    else:
        return "Todavía no tengo información para esa consulta, pero pronto la agregaré 📊."
