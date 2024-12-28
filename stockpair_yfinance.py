import base64
import datetime
import io

import pandas as pd
from flask import request, jsonify, Blueprint, render_template, get_flashed_messages
import alpaca_trade_api as tradeapi
from matplotlib.figure import Figure
from scipy.stats import pearsonr
from flask import flash

# Initialize Alpaca API client
API_KEY = "PK30X482MH0Y5RX80FPR"
API_SECRET = "LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano"
# Use live URL for live trading
# Use paper URL for paper trading
BASE_URL = "https://paper-api.alpaca.markets"

# api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')
from alpaca_trade_api.rest import REST
# api = REST(API_KEY, API_SECRET, base_url='https://paper-api.alpaca.markets', log_level='DEBUG')
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL)

# Define the blueprint
pairanalyze_bp = Blueprint('pairanalyze', __name__, template_folder='templates')

#
# @pairanalyze_bp.route('/analyze_stock_pair', methods=['POST'])
# def analyze_stock_pair():
#     print('---analyze_stock_pair---')
#     if request.method == 'POST':
#         print('-0-')
#         try:
#             print('-1-')
#             # Get parameters from the form (POST data)
#             stock1 = request.form.get('stock1')
#             print('stock1', stock1)
#             # Capitalize the stock symbol to uppercase
#             stock1 = stock1.upper()
#             stock2 = request.form.get('stock2')
#             print('stock2', stock2)
#             # Capitalize the stock symbol to uppercase
#             stock2 = stock2.upper()
#             # Retrieve the period from the form
#             period = request.form.get('period')
#             print('period', period)
#             # Retrieve the interval from the form
#             interval = request.form.get('interval')
#             print('interval', interval)
#             period = int(period[0])
#             print('period', period)
#             print('-2-')
#             if period <= 0:
#                 print('-3-')
#                 return jsonify({"error": "Period must be a positive integer."}), 400
#
#             # Debugging: Print the data to ensure it's correctly received
#             print(f"Stock1: {stock1}, Stock2: {stock2}, Period: {period}, Interval: {interval}")
#
#             if not stock1 or not stock2 or not period or not interval:
#                 return jsonify({"error": "All parameters (stock1, stock2, period, interval) are required."}), 400
#
#             # obtain current time
#             now = datetime.datetime.now()
#             end_date = now
#             print('now', now)
#
#             # end_date = now.isoformat()
#             # print('end_date', end_date)
#             if not period:
#                 return jsonify({"error": "Period is required and cannot be empty."}), 400
#
#             # according to current time and period and calculate start date and end date
#             # try:
#             #     print('--')
#             #     days = int(period)
#             #     start_date = now - datetime.timedelta(days=days)
#             #     # start_date = start_date.isoformat()
#             # except Exception as e:
#             #     return jsonify({"error": f"An error occurred while processing the period: {str(e)}"}), 400
#
#             # Calculate start date and end date based on the period (in days)
#             # try:
#             #     days = int(period)
#             #     start_date = now - datetime.timedelta(days=days)
#             #     start_date = start_date.isoformat(timespec='seconds')  # Correct formatting here
#             #     end_date = now.isoformat(timespec='seconds')  # Same for end_date
#             # except Exception as e:
#             #     return jsonify({"error": f"An error occurred while processing the period: {str(e)}"}), 400
#
#             # Calculate start date and end date based on the period (in days)
#             try:
#                 days = int(period)
#                 start_date = now - datetime.timedelta(days=days)  # start_date is a datetime object
#                 # Format start_date and end_date as RFC3339 format (YYYY-MM-DDTHH:MM:SS)
#                 start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')  # Format as RFC3339
#                 end_date = now.strftime('%Y-%m-%d %H:%M:%S')  # Format as RFC3339
#             except Exception as e:
#                 return jsonify({"error": f"An error occurred while processing the period: {str(e)}"}), 400
#
#
#             # Fetch stock data using Alpaca
#             # Alpaca API supports historical data fetching via the get_barset method
#             # barset1 = api.get_bars(stock1, interval, limit=1000)
#             # barset2 = api.get_bars(stock2, interval, limit=1000)
#             barset1 = api.get_bars(
#                 stock1,
#                 interval,
#                 start=start_date,
#                 end=end_date,
#                 feed="iex"  # 指定 IEX 数据源
#             )
#             barset2 = api.get_bars(
#                 stock2,
#                 interval,
#                 start=start_date,
#                 end=end_date,
#                 feed="iex"  # 指定 IEX 数据源
#             )
#
#             # Check if data is available
#             if not barset1 or not barset2:
#                 return jsonify({"error": "Unable to fetch stock data. Check stock symbols or parameters."}), 400
#
#             data1 = barset1[stock1]
#             data2 = barset2[stock2]
#
#             # Convert the data to pandas DataFrame for easier manipulation
#             import pandas as pd
#             df1 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in data1])
#             df2 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in data2])
#
#             # Merge the dataframes on timestamp
#             df1['timestamp'] = pd.to_datetime(df1['timestamp'], unit='s')
#             df2['timestamp'] = pd.to_datetime(df2['timestamp'], unit='s')
#             df1.set_index('timestamp', inplace=True)
#             df2.set_index('timestamp', inplace=True)
#
#             combined_data = df1[['close']].join(df2[['close']], lsuffix=f'_{stock1}', rsuffix=f'_{stock2}', how='inner')
#
#             # Calculate correlation and p-value
#             corr, p_value = pearsonr(combined_data[f'close_{stock1}'], combined_data[f'close_{stock2}'])
#             corr, p_value = round(float(corr), 3), round(float(p_value), 3)
#
#             # Calculate spread
#             spread = combined_data[f'close_{stock1}'] - combined_data[f'close_{stock2}']
#
#             # Prepare data for frontend
#             result = {
#                 "correlation": corr,
#                 "pValue": p_value,
#                 "dates": combined_data.index.strftime('%Y-%m-%d').tolist(),
#                 "spread": spread.tolist(),
#             }
#
#             # Create a Matplotlib figure
#             new_height = 4 * 0.98  # Reduce height by 20%
#             fig = Figure(figsize=(8, new_height))  # Adjusted the size for shrinking
#             ax = fig.add_subplot(1, 1, 1)
#             ax.plot(combined_data.index, spread, label='Spread', color='blue')
#             ax.set_title(f"Spread ({stock1} - {stock2})")
#             ax.set_xlabel('Date')
#             ax.set_ylabel('Spread')
#             ax.legend()
#
#             # Convert the plot to a PNG image
#             buf = io.BytesIO()
#             fig.savefig(buf, format="png")
#             buf.seek(0)
#
#             # Shrink the image by half
#             img_data = base64.b64encode(buf.read()).decode('utf-8')
#             buf.close()
#
#             flash(result)
#             return render_template('stock_pair.html', result=result, plot_data=img_data)
#
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

#
# @pairanalyze_bp.route('/analyze_stock_pair', methods=['POST'])
# def analyze_stock_pair():
#     print('---analyze_stock_pair---')
#     try:
#         # Debugging raw form data
#         print("Raw Form Data:", request.form)
#
#         # Get parameters from the form
#         stock1 = request.form.get('stock1', '').strip().upper()
#         stock2 = request.form.get('stock2', '').strip().upper()
#         period = request.form.get('period', '')[0].strip()
#         print('period', period)
#         interval = request.form.get('interval')
#         print('interval', interval)
#
#         # Validate form inputs
#         if not stock1 or not stock2 or not period or not interval:
#             return jsonify({"error": "All parameters (stock1, stock2, period, interval) are required."}), 400
#
#         # Convert period to integer
#         try:
#             period = int(period)
#         except ValueError:
#             return jsonify({"error": "Period must be a valid integer."}), 400
#
#         if period <= 0:
#             return jsonify({"error": "Period must be a positive integer."}), 400
#
#         # Calculate start and end dates
#         now = datetime.datetime.now()
#         # start_date = (now - datetime.timedelta(days=period)).isoformat()
#         # end_date = now.isoformat()
#         start_date = (now - datetime.timedelta(days=period)).strftime("%Y-%m-%d")  # 转为 YYYY-MM-DD 格式
#         end_date = now.strftime("%Y-%m-%d")  # 转为 YYYY-MM-DD 格式
#
#         print(f"Stock1: {stock1}, Stock2: {stock2}, Period: {period}, Interval: {interval}")
#         print(f"Start Date: {start_date}, End Date: {end_date}")
#
#         # Fetch stock data from Alpaca
#         try:
#             barset1 = api.get_bars(stock1, interval, start=start_date, end=end_date, feed="iex")
#             barset2 = api.get_bars(stock2, interval, start=start_date, end=end_date, feed="iex")
#         except Exception as api_error:
#             return jsonify({"error": f"Alpaca API error: {api_error}"}), 500
#
#         # Check if data is available
#         if not barset1 or not barset2:
#             return jsonify({"error": "Unable to fetch stock data. Check stock symbols or parameters."}), 400
#
#         # Convert data to DataFrame
#         import pandas as pd
#         df1 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in barset1[stock1]])
#         df2 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in barset2[stock2]])
#
#         df1['timestamp'] = pd.to_datetime(df1['timestamp'], unit='s')
#         df2['timestamp'] = pd.to_datetime(df2['timestamp'], unit='s')
#         df1.set_index('timestamp', inplace=True)
#         df2.set_index('timestamp', inplace=True)
#
#         combined_data = df1[['close']].join(df2[['close']], lsuffix=f'_{stock1}', rsuffix=f'_{stock2}', how='inner')
#
#         # Calculate correlation and spread
#         from scipy.stats import pearsonr
#         corr, p_value = pearsonr(combined_data[f'close_{stock1}'], combined_data[f'close_{stock2}'])
#         spread = combined_data[f'close_{stock1}'] - combined_data[f'close_{stock2}']
#
#         # Prepare results
#         result = {
#             "correlation": round(corr, 3),
#             "pValue": round(p_value, 3),
#             "dates": combined_data.index.strftime('%Y-%m-%d').tolist(),
#             "spread": spread.tolist(),
#         }
#
#         # Create plot
#         from matplotlib.figure import Figure
#         fig = Figure(figsize=(8, 4))
#         ax = fig.add_subplot(1, 1, 1)
#         ax.plot(combined_data.index, spread, label='Spread', color='blue')
#         ax.set_title(f"Spread ({stock1} - {stock2})")
#         ax.set_xlabel('Date')
#         ax.set_ylabel('Spread')
#         ax.legend()
#
#         buf = io.BytesIO()
#         fig.savefig(buf, format="png")
#         buf.seek(0)
#         img_data = base64.b64encode(buf.read()).decode('utf-8')
#         buf.close()
#
#         # Render the result
#         return render_template('stock_pair.html', result=result, plot_data=img_data)
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#

@pairanalyze_bp.route('/analyze_stock_pair', methods=['POST'])
def analyze_stock_pair():
    try:
        # Parse form data
        stock1 = request.form.get('stock1', '').strip().upper()
        stock2 = request.form.get('stock2', '').strip().upper()
        period = request.form.get('period', '')
        interval = request.form.get('interval', '')
        print(f"Stock1: {stock1}, Stock2: {stock2}, Period: {period}, Interval: {interval}")

        # Validate inputs
        if not stock1 or not stock2 or not period or not interval:
            print('-0-')
            return jsonify({"error": "All parameters (stock1, stock2, period, interval) are required."}), 400

        period_mapping = {"1d": 1, "5d": 5, "1wk": 7, "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825}
        valid_intervals = ["1Min", "5Min", "15Min", "1Hour", "1Day"]

        if period not in period_mapping:
            print('-1-')
            return jsonify({"error": "Invalid period value."}), 400
        if interval not in valid_intervals:
            print('-2-')
            return jsonify({"error": "Invalid interval value."}), 400

        # Calculate date range
        now = datetime.datetime.now()
        days = period_mapping[period]
        start_date = (now - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        print(f"now: {now}, days: {days}, start_date: {start_date}, end_date: {end_date}")
        print('-3-')

        # Fetch data from Alpaca
        barset1 = api.get_bars(stock1, interval, start=start_date, end=end_date, feed="iex")
        barset2 = api.get_bars(stock2, interval, start=start_date, end=end_date, feed="iex")
        # barset1 = api.get_bars("AAPL", "1Min", start="2024-11-28", end="2024-12-29", feed="iex")
        # barset2 = api.get_bars("MSFT", "1Min", start="2024-11-28", end="2024-12-29", feed="iex")
        print('-4-')
        # print('barset1', barset1)

        if not barset1 or not barset2:
            print('-3-')
            return jsonify({"error": "Unable to fetch stock data. Check stock symbols or parameters."}), 400

        # Create DataFrame
        # df1 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in barset1[stock1]])
        # df2 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in barset2[stock2]])
        df1 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in barset1])
        df2 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in barset2])

        df1['timestamp'] = pd.to_datetime(df1['timestamp'], unit='s')
        df2['timestamp'] = pd.to_datetime(df2['timestamp'], unit='s')
        df1.set_index('timestamp', inplace=True)
        df2.set_index('timestamp', inplace=True)

        combined_data = df1[['close']].join(df2[['close']], lsuffix=f'_{stock1}', rsuffix=f'_{stock2}', how='inner')

        # Analyze correlation
        from scipy.stats import pearsonr
        corr, p_value = pearsonr(combined_data[f'close_{stock1}'], combined_data[f'close_{stock2}'])
        spread = combined_data[f'close_{stock1}'] - combined_data[f'close_{stock2}']

        # Plot data
        from matplotlib.figure import Figure
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(combined_data.index, spread, label='Spread', color='blue')
        ax.set_title(f"Spread ({stock1} - {stock2})")
        ax.set_xlabel('Date')
        ax.set_ylabel('Spread')
        ax.legend()

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        result = {"correlation": round(corr, 3), "pValue": round(p_value, 3)}

        return render_template('stock_pair.html', result=result, plot_data=img_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pairanalyze_bp.route('/analyze_pair_page')
def analyze_pair_page():
    # Get the flashed messages
    result = get_flashed_messages()
    if not result:
        return render_template('stock_pair.html', result=result)
    else:
        return render_template('stock_pair.html')
