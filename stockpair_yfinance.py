import base64
import io
from flask import request, jsonify, Blueprint, render_template, get_flashed_messages
import alpaca_trade_api as tradeapi
from matplotlib.figure import Figure
from scipy.stats import pearsonr
from flask import flash

# Initialize Alpaca API client
API_KEY = "your_api_key_here"
API_SECRET = "your_api_secret_here"
BASE_URL = "https://paper-api.alpaca.markets"  # Use live URL for live trading

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Define the blueprint
pairanalyze_bp = Blueprint('pairanalyze', __name__, template_folder='templates')


@pairanalyze_bp.route('/analyze_stock_pair', methods=['POST'])
def analyze_stock_pair():
    print('---analyze_stock_pair---')
    if request.method == 'POST':
        try:
            # Get parameters from the form (POST data)
            stock1 = request.form.get('stock1')
            stock1 = stock1.upper()  # Capitalize the stock symbol to uppercase
            stock2 = request.form.get('stock2')
            stock2 = stock2.upper()  # Capitalize the stock symbol to uppercase
            period = request.form.get('period')  # Retrieve the period from the form
            interval = request.form.get('interval')  # Retrieve the interval from the form

            # Debugging: Print the data to ensure it's correctly received
            print(f"Stock1: {stock1}, Stock2: {stock2}, Period: {period}, Interval: {interval}")

            if not stock1 or not stock2 or not period or not interval:
                return jsonify({"error": "All parameters (stock1, stock2, period, interval) are required."}), 400

            # Fetch stock data using Alpaca
            # Alpaca API supports historical data fetching via the get_barset method
            barset1 = api.get_barset(stock1, interval, limit=1000)
            barset2 = api.get_barset(stock2, interval, limit=1000)

            # Check if data is available
            if not barset1 or not barset2:
                return jsonify({"error": "Unable to fetch stock data. Check stock symbols or parameters."}), 400

            data1 = barset1[stock1]
            data2 = barset2[stock2]

            # Convert the data to pandas DataFrame for easier manipulation
            import pandas as pd
            df1 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in data1])
            df2 = pd.DataFrame([{'timestamp': bar.t.timestamp(), 'close': bar.c} for bar in data2])

            # Merge the dataframes on timestamp
            df1['timestamp'] = pd.to_datetime(df1['timestamp'], unit='s')
            df2['timestamp'] = pd.to_datetime(df2['timestamp'], unit='s')
            df1.set_index('timestamp', inplace=True)
            df2.set_index('timestamp', inplace=True)

            combined_data = df1[['close']].join(df2[['close']], lsuffix=f'_{stock1}', rsuffix=f'_{stock2}', how='inner')

            # Calculate correlation and p-value
            corr, p_value = pearsonr(combined_data[f'close_{stock1}'], combined_data[f'close_{stock2}'])
            corr, p_value = round(float(corr), 3), round(float(p_value), 3)

            # Calculate spread
            spread = combined_data[f'close_{stock1}'] - combined_data[f'close_{stock2}']

            # Prepare data for frontend
            result = {
                "correlation": corr,
                "pValue": p_value,
                "dates": combined_data.index.strftime('%Y-%m-%d').tolist(),
                "spread": spread.tolist(),
            }

            # Create a Matplotlib figure
            new_height = 4 * 0.98  # Reduce height by 20%
            fig = Figure(figsize=(8, new_height))  # Adjusted the size for shrinking
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(combined_data.index, spread, label='Spread', color='blue')
            ax.set_title(f"Spread ({stock1} - {stock2})")
            ax.set_xlabel('Date')
            ax.set_ylabel('Spread')
            ax.legend()

            # Convert the plot to a PNG image
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)

            # Shrink the image by half
            img_data = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

            flash(result)
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
