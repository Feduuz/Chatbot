import requests
import certifi
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": COINGECKO_API_KEY
}

def obtener_tasas_bcra():
    url = "https://www.bcra.gob.ar/BCRAyVos/Plazos_fijos_online.asp"
    try:
        response = requests.get(url, verify=certifi.where(), timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la página del BCRA: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    tabla = soup.find('table')
    if not tabla:
        print("No se encontró la tabla de tasas.")
        return []

    tasas = []
    for fila in tabla.find_all('tr')[1:]:
        columnas = fila.find_all('td')
        if len(columnas) >= 3:
            banco = columnas[0].get_text(strip=True)
            tasa_raw = columnas[2].get_text(strip=True).replace('%', '').replace(',', '.')
            try:
                tasa_float = float(tasa_raw)
                tasas.append({'banco': banco, 'tasa': tasa_float})
            except ValueError:
                continue

    tasas_ordenadas = sorted(tasas, key=lambda x: x['tasa'], reverse=True)
    return tasas_ordenadas

def obtener_top5_acciones():
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    resultados = []
    for t in tickers:
        import yfinance as yf
        precio = yf.Ticker(t).history(period="1d")["Close"].iloc[-1]
        resultados.append(f"{t}: USD {precio:.2f}")
    return resultados

def obtener_listado_acciones():
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "FB", "JNJ"]  # etc.
    tickers_sorted = sorted(tickers)
    resultados = []
    import yfinance as yf
    for t in tickers_sorted:
        precio = yf.Ticker(t).history(period="1d")["Close"].iloc[-1]
        resultados.append(f"{t}: USD {precio:.2f}")
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
            criptos.append(f"{coin['name']} ({coin['symbol'].upper()}): USD {coin['current_price']:.2f}")

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