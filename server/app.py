from flask import Flask, request, jsonify
from deribitAPIUtil import main_get_strike_and_mark_price, get_all_strike_mark_data_threading
from kalshiAPIUtil import get_kalshi_max_year_json, get_kalshi_max_day_json
from apscheduler.schedulers.background import BackgroundScheduler
from StrikeMarkAnalyzer import StrikeMarkAnalyzer
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)


def fetch_and_save_kalshi_data():
    try:
        btc_max_year = get_kalshi_max_year_json("BTC", btc_year_analyzer)
        btc_max_day = get_kalshi_max_day_json("BTC", btc_day_analyzer)
        eth_max_year = get_kalshi_max_year_json("ETH", eth_year_analyzer)
        eth_max_day = get_kalshi_max_day_json("ETH", eth_day_analyzer)
        results = [btc_max_day, eth_max_day, btc_max_year, eth_max_year]
        
        if results:
            with open('kalshi_all_btc_markets_data.json', 'w') as f:
                json.dump({"data": results}, f, indent=4)
            
            # Refresh the analyzer data after fetching and saving
            btc_day_analyzer.refresh_data()
            eth_day_analyzer.refresh_data()
            btc_year_analyzer.refresh_data()
            eth_year_analyzer.refresh_data()
        else:
            print("No results found.")
        print("Updated kalshi fetch")
    except Exception as e:
        print(f"Error fetching data: {e}")


scheduler = BackgroundScheduler()
scheduler.add_job(get_all_strike_mark_data_threading, 'interval', minutes=2) 
scheduler.add_job(fetch_and_save_kalshi_data, 'interval', minutes=2) 
scheduler.start()

def initialize_data():
    # First, get the strike mark data needed for analyzers
    get_all_strike_mark_data_threading()  # Initial fetch for strike mark data
    global btc_day_analyzer, eth_day_analyzer, btc_year_analyzer, eth_year_analyzer
    btc_day_analyzer = StrikeMarkAnalyzer("BTC", "day")
    eth_day_analyzer = StrikeMarkAnalyzer("ETH", "day")
    btc_year_analyzer = StrikeMarkAnalyzer("BTC", "year")
    eth_year_analyzer = StrikeMarkAnalyzer("ETH", "year")
    fetch_and_save_kalshi_data()  # Initial data fetch for Kalshi

initialize_data()

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/get_all_kalshi_markets_json")
def get_all_kalshi_markets_json():
    try:
        with open('kalshi_all_btc_markets_data.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=True)