from flask import render_template, Blueprint, session, redirect, url_for
from minimum_distance_strategy import risk_metrics, find_pairs_min_distance, pairs_info, get_data

risk_pb = Blueprint('risk_control', __name__, template_folder='templates')

from alpaca.trading.client import TradingClient
# from alpaca.trading.models import Account
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import numpy as np
from minimum_distance_strategy import pairs_list
from datetime import datetime

# Alpaca API Key 和 Secret Key
API_KEY = 'PK30X482MH0Y5RX80FPR'
API_SECRET = 'LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano'
# Initialize the trading client and data client
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)


# Get account information
def get_account_info():
    account = trading_client.get_account()
    equity = float(account.equity)  # Total funding
    buying_power = float(account.buying_power)  # Available funds
    utilization_rate = ((equity - buying_power) / equity) * 100  # Usage percentage
    return equity, buying_power, utilization_rate

# Get stock volatility
def get_stock_volatility(symbol, start_date, end_date):
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start_date,
        end=end_date
    )
    bars = data_client.get_stock_bars(request_params)
    print('bars', bars)
    close_prices = [bar.close for bar in bars[symbol]]
    volatility = np.std(close_prices)  # Standard deviation as volatility
    return volatility

# Get the volatility of two stocks traded in pairs
def get_pair_volatility(stock1, stock2, start_date, end_date):
    vol1 = get_stock_volatility(stock1, start_date, end_date)
    vol2 = get_stock_volatility(stock2, start_date, end_date)
    return vol1, vol2



@risk_pb.route('/risk_control')
def risk_control():
    from accountinfo import accountinfo
    global risk_metrics
    print('11')

    # Check if risk_metrics is empty
    if not risk_metrics:
        print('22')
        # Check if the user is logged in by checking the session
        if session.get('user_name'):
            print('33')
            # Render the dashboard if the user is logged in
            # return render_template("dashboard.html", accountinfo=accountinfo)
            return '', 204
        else:
            print('44')
            # Redirect to the login page if the user is not logged in
            return redirect(url_for('auth.login'))
    print('55')
    equity, buying_power, utilization_rate = get_account_info()
    print('utilization_rate', utilization_rate)
    start_date1 = datetime.strptime(pairs_info['start_date'], "%Y-%m-%d")
    end_date1 = datetime.strptime(pairs_info['end_date'], "%Y-%m-%d")
    start_date = pairs_info['start_date']
    end_date = pairs_info['end_date']
    print('start_date', start_date, 'end_date', end_date)
    formation_period = (end_date1 - start_date1).days
    print('formation_period', formation_period)
    stock_data = get_data(pairs_list, start_date, end_date)
    print('stock_data', stock_data)
    best_pair, min_distance = find_pairs_min_distance(stock_data, formation_period)
    print('best_pair', best_pair, 'min_distance', min_distance)
    stock1 = best_pair[0]
    stock2 = best_pair[1]
    print('stock1', stock1, 'stock2', stock2)
    # vol1, vol2 = get_pair_volatility(stock1, stock2, start_date1, end_date1)
    # print('vol1', vol1, 'vol2', vol2)
    vol1 = get_stock_volatility(stock1, start_date, end_date)
    vol2 = get_stock_volatility(stock2, start_date, end_date)
    vol1 = round(vol1, 2)
    vol2 = round(vol2, 2)
    risk_metrics[stock1 + 'volatility'] = vol1
    risk_metrics[stock2 + 'volatility'] = vol2
    risk_metrics['utilization_rate'] = round(utilization_rate, 2)

    print('vol1', vol1, 'vol2', vol2, 'utilization_rate', utilization_rate)
    return render_template('risk_control.html', risk_metrics=risk_metrics)


# main
if __name__ == "__main__":
    # account info
    equity, buying_power, utilization_rate = get_account_info()
    print(f"account total fund: ${equity:.2f}")
    print(f"available fund: ${buying_power:.2f}")
    print(f"usage: {utilization_rate:.2f}%")

    # Market volatility (using S&P 500 ETF: SPY)
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    market_volatility = get_stock_volatility("SPY", start_date, end_date)
    print(f"Market volatility (SPY): {market_volatility:.2f}")

    # 配对交易股票波动率
    stock1 = "AAPL"  # apple
    stock2 = "MSFT"  # microsoft
    vol1, vol2 = get_pair_volatility(stock1, stock2, start_date, end_date)
    print(f"{stock1} volatility: {vol1:.2f}")
    print(f"{stock2} volatility: {vol2:.2f}")
