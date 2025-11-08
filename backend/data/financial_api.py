import requests
import certifi
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
import yfinance as yf

load_dotenv()
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": COINGECKO_API_KEY
}

def obtener_tasas_plazofijo():
    url = "https://api.argentinadatos.com/v1/finanzas/tasas/plazoFijo"

    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        print(f"📄 Contenido recibido: {response.text}")
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            print("⚠️ La respuesta no es una lista. Estructura inesperada.")
            return [], []

        # Filtrar y ordenar tasas de clientes
        clientes = [item for item in data if isinstance(item.get("tnaClientes"), (int, float))]
        clientes = sorted(clientes, key=lambda x: x["tnaClientes"], reverse=True)

        no_clientes = [item for item in data if isinstance(item.get("tnaNoClientes"), (int, float))]
        no_clientes = sorted(no_clientes, key=lambda x: x["tnaNoClientes"], reverse=True)

        top_clientes = [
            {"banco": item["entidad"], "tasa": item["tnaClientes"]}
            for item in clientes[:5]
            if item.get("tnaClientes") is not None
        ]
        top_no_clientes = [
            {"banco": item["entidad"], "tasa": item["tnaNoClientes"]}
            for item in no_clientes[:5]
            if item.get("tnaNoClientes") is not None
        ]

        return top_clientes, top_no_clientes

    except Exception as e:
        print(f"⚠️ Error al obtener tasas de ArgentinaDatos: {e}")
        return [], []

def obtener_top5_acciones():
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    resultados = []
    for t in tickers:
        import yfinance as yf
        precio = yf.Ticker(t).history(period="1d")["Close"].iloc[-1]
        resultados.append(f"{t}: USD ${precio:.2f}")
    return resultados

def obtener_listado_acciones():
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "FB", "JNJ"]  # etc.
    tickers_sorted = sorted(tickers)
    resultados = []
    import yfinance as yf
    for t in tickers_sorted:
        precio = yf.Ticker(t).history(period="1d")["Close"].iloc[-1]
        resultados.append(f"{t}: USD ${precio:.2f}")
    return resultados

def obtener_top5_criptos():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 5,
        "page": 1,
        "sparkline": "false"
    }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        criptos = []
        for coin in data:
            criptos.append(f"{coin['name']} ({coin['symbol'].upper()}): USD ${coin['current_price']:.2f}")

        return criptos
    except Exception as e:
        return [f"Error al obtener datos de criptomonedas: {e}"]

def obtener_listado_criptos():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "sparkline": "false"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Ordenar alfabéticamente
        data_sorted = sorted(data, key=lambda x: x['name'].lower())

        criptos = []
        for coin in data_sorted:
            criptos.append(f"{coin['name']} ({coin['symbol'].upper()}): USD {coin['current_price']:.2f}")

        return criptos
    except Exception as e:
        return [f"Error al obtener listado de criptomonedas: {e}"]
    
def obtener_cuentas_remuneradas():
    url = "https://api.argentinadatos.com/v1/finanzas/fci/otros/ultimo"

    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or len(data) == 0:
            return []

        cuentas = []
        for item in data[:5]:  # top 5
            entidad = item.get("fondo", "Entidad desconocida")
            tna = item.get("tna", 0)
            tope = item.get("tope", "Sin tope")

            cuentas.append({
                "entidad": entidad,
                "tna": tna,
                "tope": tope
            })

        return cuentas

    except Exception as e:
        print(f"⚠️ Error al obtener cuentas remuneradas: {e}")
        return []

def obtener_cotizaciones_dolar():
    url = "https://dolarapi.com/v1/ambito/dolares"
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        cotizaciones = []
        for d in data:
            nombre = d.get("nombre", "Desconocido")
            compra = d.get("compra")
            venta = d.get("venta")
            fecha = d.get("fechaActualizacion", "")

            # Formateo de fecha
            try:
                fecha_dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
                fecha_formateada = fecha_dt.strftime("%Y-%m-%d, %H:%M:%S")
            except Exception:
                fecha_formateada = fecha

            # Si es Dólar Tarjeta, no mostrar valor compra
            if "tarjeta" in nombre.lower():
                compra = " ---"

            cotizaciones.append({
                "nombre": nombre,
                "compra": compra,
                "venta": venta,
                "fechaActualizacion": fecha_formateada
            })

        return cotizaciones

    except Exception as e:
        print(f"⚠️ Error al obtener cotizaciones del dólar: {e}")
        return []

def obtener_riesgo_pais():
    url = "https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo"
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
        data = response.json()

        # Esperado: {"fecha": "2025-11-04", "valor": 2475.0}
        fecha = data.get("fecha", "")
        valor = data.get("valor", "N/D")

        #  Formateo de fecha
        try:
            fecha_dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
            fecha_formateada = fecha_dt.strftime("%Y-%m-%d, %H:%M:%S")
        except Exception:
            fecha_formateada = fecha

        return {
            "valor": valor,
            "fecha": fecha_formateada
        }

    except Exception as e:
        print(f"⚠️ Error al obtener Riesgo País: {e}")
        return None
