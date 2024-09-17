from flask import Flask, request, jsonify
from deribitAPIUtil import main_get_strike_and_mark_price
from pdf import get_pdf_probability_of_lte, get_pdf_probability_of_gte, get_graph_data
import os
import json

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/strike_mark_data")
def get_strike_mark_data():
    exp_date = request.args.get("exp_date")
    currency = request.args.get("currency")
    try:
        results = main_get_strike_and_mark_price(exp_date, currency)
        with open('strike_mark_data.json', 'w') as f:
            json.dump({"data": results}, f, indent=4)
        return jsonify({"data": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/function_and_derivatives_data")
def get_function_and_derivatives_data():
    try:
        data = get_graph_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error" : str(e)}), 500

@app.route("/get_probability")
def get_probability():
    contract_type = request.args.get("contract_type")
    target_price = request.args.get("target_price")
    if not contract_type or not target_price:
        missing_params = []
        if not contract_type:
            missing_params.append("contract_type")
        if not target_price:
            missing_params.append("target_price")
        return jsonify({"error": f"Missing parameter(s): {', '.join(missing_params)}"}), 400
    try:
        target_price = float(target_price)
    except ValueError:
        return jsonify({"error": "Invalid parameter: target_price must be a number"}), 400
    contract_functions = {
        "yes": get_pdf_probability_of_gte,
        "no": get_pdf_probability_of_lte
    }
    probability_function = contract_functions.get(contract_type)
    if probability_function:
        probability = probability_function(target_price)
        return jsonify({"data": probability})
    else:
        return jsonify({"error": "Invalid parameter: contract_type must be 'yes' or 'no'"}), 400

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)