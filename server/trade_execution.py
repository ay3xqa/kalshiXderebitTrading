from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
import json
import uuid
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

    msg_string = timestampt_str + method_type + path

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
execute_trade_method = "POST"
base_url = 'https://api.elections.kalshi.com'
execute_trade_path = '/trade-api/v2/portfolio/orders'
execute_trade_headers = retrieve_auth_header(path=execute_trade_path, method_type=execute_trade_method)

def find_best_trade_opportunity():
    with open("kalshi_all_btc_markets_data.json", 'r') as f:
        all_market_data = json.load(f)
    #for now this is hardcoded to daily eth
    market = all_market_data["data"][1]["market_data"]
    print(market)
    best_trade = {
        "event_ticker": None,
        "trade_type": None,  # "yes" or "no"
        "price": None,
        "probability": None,
        "difference": float('-inf')
    }
    for event in market:
        # Calculate differences for both yes and no trades
        yes_difference = event['yes_prob'] - event['yes_price']
        no_difference = event['no_prob'] - event['no_price']

        # Check if this 'yes' trade has the maximum difference
        if yes_difference > best_trade["difference"]:
            best_trade.update({
                "event_ticker": event["event_ticker"],
                "trade_type": "yes",
                "price": event["yes_price"],
                "probability": event["yes_prob"],
                "difference": yes_difference
            })

        # Check if this 'no' trade has the maximum difference
        if no_difference > best_trade["difference"]:
            best_trade.update({
                "event_ticker": event["event_ticker"],
                "trade_type": "no",
                "price": event["no_price"],
                "probability": event["no_prob"],
                "difference": no_difference
            })

    # Remove 'difference' key before returning (if not needed in the output)
    return best_trade

#Function to actually execute the trade
def execute_trade(action, side, count, order_type, ticker, yes_price=None, no_price=None):
    order_id = str(uuid.uuid4())
    payload = {
        "action": action,
        "side": side,
        "count": count,
        "type": order_type,
        "ticker": ticker,
        "client_order_id": order_id
    }
    response = requests.post(base_url+execute_trade_path, headers=execute_trade_headers, json=payload)
    print(response.text)

def create_and_execute_trade():
    best_trade = find_best_trade_opportunity()
    if not isSufficientAlpha:
        return
    max_allocation = getMaxAllocation(best_trade)
    if max_allocation > 0:
        execute_trade("buy", best_trade["trade_type"], max_allocation, "market", best_trade["event_ticker"])

def isSufficientAlpha(trade):
    return trade["difference"] >= 10

portfolio_method = "GET"
base_url = 'https://api.elections.kalshi.com'
portfolio_path = '/trade-api/v2/portfolio/balance'
portfolio_headers = retrieve_auth_header(path=portfolio_path, method_type=portfolio_method)

def getMaxAllocation(trade):
    response = requests.get(base_url+portfolio_path, headers=portfolio_headers)
    max_allocation = response.json()["balance"]*0.2
    return int(max_allocation//trade["price"])

#local testing for best trade and max allocation
best_trade = find_best_trade_opportunity()
max_allocation = getMaxAllocation(best_trade)
print(best_trade)
print(max_allocation)