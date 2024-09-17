import requests
from concurrent.futures import ThreadPoolExecutor

# Deribit API endpoints
base_url = "https://www.deribit.com/api/v2/"

# Example endpoint to get all instruments (options data)
instrument_endpoint = "public/get_instruments"
mark_endpoint = "public/ticker"

# @brief    Retrieve mark to market price of a ticker (i.e BTC-27DEC24-10000-C -> BTC Call Expiring Dec 27 2024 with strike price of 10000)
# @params   instrument_name: STRING -> i.e "BTC-27DEC24-10000-C"
# @return   FLOAT -> i.e 0.662
def fetch_ticker(instrument_name):
    params = {"instrument_name": instrument_name}
    ticker_response = requests.get(base_url+mark_endpoint, params=params)
    ticker_data = ticker_response.json()
    if ticker_response.status_code == 200:
        return ticker_data["result"]["mark_price"]
    else:
        print("Failed to retrieve ticker info for: ", instrument_name, ticker_response.status_code, ticker_response.text)
        return None

# @brief    Retrieve all the call options for an expiration date and currency
# @params   exp_date: STRING -> formatted i.e "BTC-27DEC24"
#           currency: STRING -> i.e "BTC"
# @return   LIST: list of tuples with each tuple being (instrument_name: STRING, strike_price: FLOAT)
def fetch_instruments(exp_date, currency):
    # Query parameters (for example, options on BTC)
    params = {
        "currency": currency,
        "kind": "option",
        "expired": "false"
    }
    response = requests.get(base_url + instrument_endpoint, params=params)
    options = []
    if response.status_code == 200:
        data = response.json()
        for res in data["result"]:
            if exp_date in res["instrument_name"] and res["option_type"] == "call":
                options.append((res["instrument_name"], res["strike"]))
        return options
    else:
        print("Failed to retrieve data:", response.status_code, response.text)
        return []

# @brief    Helper function to retrieve mark to market price of an instrument and format output
# @params   instrument: STRING -> i.e "BTC-27DEC24-10000-C"
# @return   TUPLE: (strike: FLOAT, mark_price: FLOAT)
def get_instrument_data(instrument):
    if instrument:
        instrument_name = instrument[0]
        strike = instrument[1]
        mark_price = fetch_ticker(instrument_name=instrument_name)
        return (strike, mark_price) if mark_price else None
    else:
        return
    
# @brief    Main engine function using util functions to fetch each strike price and its corresponding MTM price. Uses threads to speed up API calls
# @params   exp_date: STRING -> formatted i.e "BTC-27DEC24"
#           currency: STRING -> i.e "BTC"
# @return   LIST: list of tuples (strike: FLOAT, mark_price: FLOAT)
def main_get_strike_and_mark_price(exp_date, currency):
    instrument_list = fetch_instruments(exp_date=exp_date, currency=currency)

    with ThreadPoolExecutor(max_workers = 10) as executor:
        results = list(executor.map(get_instrument_data, instrument_list))
    results = [result for result in results if result]
    return results