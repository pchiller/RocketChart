import requests

from datetime import datetime
import pandas as pd

def get_ohlc(coin_id,cg_key):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc/'
    print(url)
    params = {
             # 'ids': coin_id,
             'vs_currency': 'usd',
             'days': '1',
             # 'include_market_cap': 'true'
    }
    headers = { 'x-cg-demo-api-key': cg_key}
    response = requests.get(url, params = params)
    ohlc_data = response.json()
    converted_data = [convert_to_datetime_tuple(item) for item in ohlc_data]
    return converted_data[24:]

# Function to convert the timestamp (ms) to a datetime object
def convert_to_datetime_tuple(data):
    # The CoinGecko API returns [timestamp (ms), open, high, low, close]
    timestamp_ms = data[0]
    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000.0

    date_obj = datetime.fromtimestamp(timestamp_s)
    # The rest of the elements are the OHLC values
    ohlc_values = data[1:]
    # Return a tuple: (datetime, open, high, low, close)
    return (date_obj,) + tuple(ohlc_values)

def get_coin_data(coin_id,cg_key):
    url = f'https://api.coingecko.com/api/v3/simple/price/'
    print(url)
    params = {  
             'ids': coin_id,
             'vs_currencies': 'usd',
             # 'days': '1',
             'include_market_cap': 'true',
             'include_24hr_vol': 'true'
    }
    headers = { 'x-cg-demo-api-key': cg_key }
    response = requests.get(url, params = params)
    ohlc_data = response.json()
    data = ohlc_data.get(coin_id)
    usd = data.get('usd')
    usd_market_cap = format(int(data.get('usd_market_cap')),",")
    usd_24h_vol = format(round(data.get('usd_24h_vol'),2),",")

    text_content = """
💰 Price: <b>${usd}</b>
📊 Marketcap: <b>${usd_market_cap}</b>
📈 Volume: <b>${usd_24h_vol}</b>

    """
    return text_content.format(usd = usd,usd_market_cap=usd_market_cap,usd_24h_vol=usd_24h_vol)
# print(get_coin_data())
