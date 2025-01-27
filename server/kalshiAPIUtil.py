from kalshiAuth import retrieve_auth_header
from s3_update_util import update_local_csv
import requests
import datetime

method = "GET"
base_url = 'https://api.elections.kalshi.com'
path = '/trade-api/v2/markets'

def get_kalshi_max_year_json(currency, SMA):
    market_params = {'series_ticker':"KX"+currency+"MAXY"}
    headers = retrieve_auth_header(path=path, method_type=method)
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
                mkt["no_price"] = market["no_ask"]
                mkt["no_prob"] = SMA.integrate_pdf(mkt["target_price"])
                mkt["yes_price"] = market["yes_ask"]
                mkt["yes_prob"] = 100-mkt["no_prob"]
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
    headers = retrieve_auth_header(path=path, method_type=method)
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
                mkt["no_price"] = market["no_ask"]
                mkt["no_prob"] = SMA.integrate_pdf(mkt["target_price"])
                mkt["yes_price"] = market["yes_ask"]
                mkt["yes_prob"] = 100-mkt["no_prob"]

                if currency == "BTC":
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_local_csv(timestamp, "BTC", "Daily", "No", mkt["target_price"], mkt["no_prob"], mkt["no_price"])
                    update_local_csv(timestamp, "BTC", "Daily", "Yes", mkt["target_price"], mkt["yes_prob"], mkt["yes_price"])

                market_data.append(mkt)
        sorted_market_data = sorted(market_data, key=lambda x: x['target_price'])
        data["market_data"] = sorted_market_data
        return data
    else:
        print("Error: ", response.status_code, response.text)
        return {}

