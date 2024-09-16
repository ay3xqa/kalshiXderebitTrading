from flask import Flask, request, jsonify
from deribitAPIUtil import main_get_strike_and_mark_price
import os

app = Flask(__name__)

# Deribit API endpoints
base_url = "https://www.deribit.com/api/v2/"

# Example endpoint to get all instruments (options data)
instrument_endpoint = "public/get_instruments"
mark_endpoint = "public/ticker"

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/strike_mark_data")
def get_strike_mark_data():
    exp_date = request.args.get("exp_date")
    currency = request.args.get("currency")
    try:
        results = main_get_strike_and_mark_price(exp_date, currency)
        return jsonify({"result": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)