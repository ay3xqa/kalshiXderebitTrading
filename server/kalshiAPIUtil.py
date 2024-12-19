from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
import json
from StrikeMarkAnalyzer import StrikeMarkAnalyzer
import os



def sign_pss_text(private_key: rsa.RSAPrivateKey, text: str) -> str:
    # Before signing, we need to hash our message.
    # The hash is what we actually sign.
    # Convert the text to bytes
    message = text.encode('utf-8')

    try:
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    except InvalidSignature as e:
        raise ValueError("RSA sign PSS failed") from e
def load_private_key_from_file(file_path):
    with open(file_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # or provide a password if your key is encrypted
            backend=default_backend()
        )
    return private_key

import requests
import datetime

def retrieve_auth_header(path, method_type):
    # Get the current time
    current_time = datetime.datetime.now()

    # Convert the time to a timestamp (seconds since the epoch)
    timestamp = current_time.timestamp()

    # Convert the timestamp to milliseconds
    current_time_milliseconds = int(timestamp * 1000)
    timestampt_str = str(current_time_milliseconds)

    # Load the RSA private key
    private_key = load_private_key_from_file('kalshi_key.key')

    msg_string = timestampt_str + method + path

    sig = sign_pss_text(private_key, msg_string)
    headers = {
            'KALSHI-ACCESS-KEY': os.environ.get('KALSHI_ACCESS_KEY'),
            'KALSHI-ACCESS-SIGNATURE': sig,
            'KALSHI-ACCESS-TIMESTAMP': timestampt_str
        }
    
    legacy_headers = {
            'KALSHI-ACCESS-KEY': os.environ.get('KALSHI_ACCESS_KEY'),
            'KALSHI-ACCESS-SIGNATURE': sig,
            'KALSHI-ACCESS-TIMESTAMP': timestampt_str
        }
    return headers
method = "GET"
base_url = 'https://api.elections.kalshi.com'
path = '/trade-api/v2/markets'
headers = retrieve_auth_header(path=path, method_type=method)

def get_kalshi_max_year_json(currency, SMA):
    market_params = {'series_ticker':"KX"+currency+"MAXY"}
    response = requests.get(base_url+path, headers=headers, params=market_params)
    valid_currency = {"BTC", "ETH"}
    if currency not in valid_currency:
        print("Not valid currency type. Request not made")
        return {}
    if response.status_code == 200:
        markets_response = response.json()
        data = {}
        if markets_response['markets'][0]:
            data["market_title"] = markets_response['markets'][0]["title"]
            market_data = []
        for market in markets_response['markets']:
            if market["status"] == "active":
                mkt = {}
                last_dash_index = market["ticker"].rfind('-')
                target_price = int(market["floor_strike"]+0.01)
                mkt["event_ticker"] = market["ticker"]
                mkt["target_price"] = int(target_price)
                mkt["yes_price"] = market["yes_ask"]
                mkt["yes_prob"] = SMA.get_pdf_probability_of_gte(mkt["target_price"])
                mkt["no_price"] = market["no_ask"]
                mkt["no_prob"] = SMA.get_pdf_probability_of_lte(mkt["target_price"])
                market_data.append(mkt)
        sorted_market_data = sorted(market_data, key=lambda x: x['target_price'])
        data["market_data"] = sorted_market_data
        return data
    else:
        print("Error: ", response.status_code, response.text)
        return {}

def get_kalshi_max_day_json(currency, SMA):
    today = datetime.datetime.now()
    
    # Extract components for the format
    year_last_two = today.strftime('%y')  # Last two digits of the year (e.g., '24')
    month_abbr = today.strftime('%b').upper()  # Month abbreviation (e.g., 'DEC')
    day = today.strftime('%d')  # Day of the month (e.g., '13')
    
    # Combine components into the desired format
    formatted_date = f"{year_last_two}{month_abbr}{day}"  # e.g., '24DEC13'


    print(f"KX{currency}D-{formatted_date}17")
    market_params = {'event_ticker':f"KX{currency}D-{formatted_date}17"}
    response = requests.get(base_url+path, headers=headers, params=market_params)
    valid_currency = {"BTC", "ETH"}
    if currency not in valid_currency:
        print("Not valid currency type. Request not made")
        return {}
    if response.status_code == 200:
        markets_response = response.json()
        data = {}
        if markets_response['markets'][0]:
            data["market_title"] = markets_response['markets'][0]["title"]
            market_data = []
        for market in markets_response['markets']:
            if market["yes_ask"] > 90 or market["no_ask"] > 90:
                continue
            if market["status"] == "active":
                mkt = {}
                mkt["event_ticker"] = market["ticker"]
                mkt["target_price"] = int(market["floor_strike"]+0.01)
                mkt["yes_price"] = market["yes_ask"]
                mkt["yes_prob"] = SMA.get_pdf_probability_of_gte(mkt["target_price"])
                mkt["no_price"] = market["no_ask"]
                mkt["no_prob"] = SMA.get_pdf_probability_of_lte(mkt["target_price"])
                market_data.append(mkt)
        sorted_market_data = sorted(market_data, key=lambda x: x['target_price'])
        data["market_data"] = sorted_market_data
        return data
    else:
        print("Error: ", response.status_code, response.text)
        return {}

