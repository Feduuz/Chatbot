def procesar_texto(mensaje):
    mensaje = mensaje.lower()

    if any(palabra in mensaje for palabra in ["bitcoin", "btc", "cripto"]):
        return "criptomoneda"
    elif any(palabra in mensaje for palabra in ["acción", "acciones", "cedear", "bolsa"]):
        return "acciones"
    elif any(palabra in mensaje for palabra in ["plazo fijo", "plazofijo", "plazo", "plazos fijos"]):
        return "plazo_fijo"
    elif "hola" in mensaje or "buenas" in mensaje:
        return "saludo"
    elif any(palabra in mensaje for palabra in ["cuenta remunerada", "cuentas remuneradas", "cuentas"]):
        return "cuenta_remunerada"
    elif any(palabra in mensaje for palabra in ["dolar", "dólar", "usd"]):
        return "dolar"
    elif any(palabra in mensaje for palabra in ["riesgo país", "riesgo pais", "riesgo"]):
        return "riesgo_pais"
    else:
        return "desconocido"
