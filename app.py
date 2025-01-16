import importlib
import json
import os

import numpy as np
from flask import Flask, render_template, session, jsonify, request, redirect, url_for
import globalvaluemanagement
from account_management import auth_bp
from chart import convertWatchlist
from order_management import order_management_pb
from order_placement import order_bp
from risk_control import risk_pb
from stock_matching import pair_bp
from stock_pair import allstock_bp
from stock_pair_alpaca import pairanalyze_bp
from minimum_distance_strategy import maxmindistance_strategy, maxmindistance_backtest, minimumdistance_bp
from test_strategy import test_bp

app = Flask(__name__)

dbconn = None
connection = None
app.secret_key = os.urandom(24)
# UploadDir = '/static/images/'
login_num = 0
globalvaluemanagement._init()
globalvaluemanagement.set_value('0', 0)

# Register the auth blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(pair_bp, url_prefix='/pair')
app.register_blueprint(order_bp, url_prefix='/order')
app.register_blueprint(pairanalyze_bp, url_prefix='/pairanalyze')
app.register_blueprint(allstock_bp, url_prefix='/allstock')
app.register_blueprint(test_bp, url_prefix='/')
app.register_blueprint(maxmindistance_strategy, url_prefix='/')
app.register_blueprint(maxmindistance_backtest, url_prefix='/')
app.register_blueprint(minimumdistance_bp, url_prefix='/')
app.register_blueprint(risk_pb, url_prefix='/')
app.register_blueprint(order_management_pb, url_prefix='/')


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard")
def dashboard():
    if session.get('user_name'):
        # return render_template("dashboard.html")
        return redirect(url_for('auth.login'))
    else:
        return render_template("registerlogin.html")


# @app.route("/chart")
# def chart():
#     data = convertWatchlist()
#     formatted_data = [{'symbol': item, 'formatted': f"{item}:{item}"} for item in data]
#     return render_template("chart.html", data=formatted_data)

@app.route("/chart")
def chart():
    data = convertWatchlist()
    if not data:
        data = ["NASDAQ:AAPL"]  # Provide a fallback

    try:
        formatted_data = [{"name": item.split(":")[1], "symbol": item} for item in data]
        print("Formatted watchlist:", formatted_data)
        print("Serialized watchlist:", json.dumps(formatted_data))  # Check JSON serialization
        return render_template("chart.html", watchlist=formatted_data)
    except Exception as e:
        print(f"Serialization error: {e}")
        return "Error in watchlist data", 500


@app.route("/all_stock")
def all_stock():
    return render_template("pairing_allstock.html")


@app.route('/grid_strategy')
def grid_strategy():
    return render_template('grid_strategy.html')


@app.route('/filename/<file_name>')
def filename(file_name):
    print('filename')
    return render_template('strategy_file.html', file_name=file_name)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=7000, debug=True)


