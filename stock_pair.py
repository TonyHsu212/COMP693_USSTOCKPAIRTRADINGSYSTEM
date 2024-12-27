import logging
import time
from threading import Thread
from alpaca.trading import GetAssetsRequest, AssetStatus, AssetClass
from flask import jsonify, Blueprint
from sqlalchemy import create_engine
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from account_management import getCursor
import pandas as pd
from scipy.stats import pearsonr

# Define the blueprint
allstock_bp = Blueprint('allstock', __name__, template_folder='templates')

# 配置 Alpaca API
# ALPACA_API_KEY = 'your_api_key'
# ALPACA_SECRET_KEY = 'your_secret_key'
APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'
APCA_API_KEY_ID = 'PK30X482MH0Y5RX80FPR'
APCA_API_SECRET_KEY = 'LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano'

# Alpaca 客户端
trading_client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)
data_client = StockHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)

# 配置 MySQL 数据库
########################### for local environment ########################################
# ---- PUT YOUR username HERE ----
dbuser = "root"
# ---- PUT YOUR PASSWORD HERE ----
dbpass = "801221789801"
dbhost = "localhost"
dbport = "3306"
dbname = "tradingsystem"

engine = create_engine(f'mysql+pymysql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}')


# Function to get US stock symbols
def get_us_stock_symbols():
    print("Getting ticker symbols...")
    try:
        assets_request = GetAssetsRequest(status=AssetStatus.ACTIVE, asset_class=AssetClass.US_EQUITY)
        assets = trading_client.get_all_assets(assets_request)
        symbols = [asset.symbol for asset in assets if asset.tradable]
        print(f"Retrieved {len(symbols)} symbols: ", symbols)
        return symbols
    except Exception as e:
        print(f"Error getting ticker symbols: {e}")
        return []


def download_stock_data(symbols, start_date='2021-01-01', end_date='2023-12-31'):
    """
    Downloads stock data for a list of symbols within a specified date range.

    Args:
        symbols (list): List of stock symbols to download.
        start_date (str): Start date for the historical data in 'YYYY-MM-DD' format.
        end_date (str): End date for the historical data in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: A DataFrame containing stock data for all symbols.
    """
    all_data = []
    # symbols = get_us_stock_symbols()
    for symbol in symbols[0:6]:
        try:
            print(f"Downloading data for {symbol}...")
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            bars = data_client.get_stock_bars(request_params).df
            # print('bars1:', bars)
            if bars.empty:
                print(f"No data found for {symbol}.")
                continue
            bars = bars.reset_index()
            # print('bars2:', bars)
            bars['Symbol'] = symbol
            # print('bars3:', bars)
            bars.rename(columns={'timestamp': 'Date', 'open': 'Open', 'high': 'High',
                                 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
            print('bars4:', bars)
            # all_data.append(bars[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Symbol']])
            all_data.append(bars[['Date', 'Symbol', 'Close']])
            print('all_data:', all_data)
            print(f"Data for {symbol} downloaded successfully.")
        except Exception as e:
            print(f"Error downloading data for {symbol}: {e}")

    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        print('combined_data', combined_data)
        print("All data downloaded successfully.")
        return combined_data
    else:
        print("No data downloaded.")
        return None


def analyze_stock_data_correlation(combined_data):
    """
    Analyzes the correlation between different stocks' closing prices and stores results in a database.

    Args:
        combined_data (pd.DataFrame): A DataFrame containing 'Date', 'Symbol', and 'Close' columns
                                      for multiple stocks.
        db_config (dict): A dictionary containing database connection parameters (e.g., host, database, user, password).

    Returns:
        list: A list of tuples containing stock pairs, their correlation, and p-value.
    """
    # Pivot the data to have dates as rows and symbols as columns
    print("Preparing data for correlation analysis...")
    pivot_data = combined_data.pivot(index='Date', columns='Symbol', values='Close')
    pivot_data.dropna(inplace=True)  # Drop rows with missing values

    print("Calculating correlations...")
    results = []
    symbols = pivot_data.columns

    # Connect to the database
    try:
        cursor, connection = getCursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        return results

    # Compute correlation and p-value for each pair of stocks
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            stock1 = symbols[i]
            stock2 = symbols[j]
            try:
                correlation, p_value = pearsonr(pivot_data[stock1], pivot_data[stock2])
                results.append((stock1, stock2, correlation, p_value))

                # Insert the result into the database
                insert_query = """
                    INSERT INTO TradingSystem.stock_analysis (Symbol_1, Symbol_2, Correlation, p_value)
                    VALUES (%s, %s, %s, %s)
                """

                cursor.execute(insert_query, (stock1, stock2, correlation, p_value))
                print(f"Analyzed pair: {stock1} & {stock2}, Correlation: {correlation}, P-value: {p_value}")
            except Exception as e:
                print(f"Error analyzing pair {stock1} & {stock2}: {e}")

    # Commit changes and close the connection
    try:
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error closing the database connection: {e}")

    return results


# Store the task status
tasks = {}


# Configure logging
logging.basicConfig(level=logging.DEBUG)


# Long task function
def long_task(task_id):
    logging.debug(f"Task {task_id} started.")
    start_time = time.time()
    try:
        for i in range(1, 10100):
            tasks[task_id] = {"status": "processing", "progress": i}
            logging.debug(f"Task {task_id} progress: {i}%")
            time.sleep(10)
        end_time = time.time()
        tasks[task_id] = {
            "status": "completed",
            "progress": 100,
            "time_spent": end_time - start_time,
        }
        logging.debug(f"Task {task_id} completed. Time spent: {end_time - start_time} seconds.")
    except Exception as e:
        tasks[task_id] = {"status": "error", "message": str(e)}
        logging.error(f"Task {task_id} failed: {e}")


@allstock_bp.route('/start-task', methods=['POST'])
def start_task():
    # Create a unique task ID
    print('start task.....')
    task_id = str(time.time())
    tasks[task_id] = {"status": "started", "progress": 0}
    thread = Thread(target=long_task, args=(task_id,))
    thread.start()
    symbols = get_us_stock_symbols()  # Retrieve stock symbols
    bars = download_stock_data(symbols, start_date='2021-01-01', end_date='2023-12-31')  # Download stock data

    if bars is not None:
        # Analyze correlations
        correlation_results = analyze_stock_data_correlation(bars)

        # Print correlation results
        print("\nCorrelation Results:")
        for stock1, stock2, correlation, p_value in correlation_results:
            print(f"Stocks: {stock1} & {stock2}, Correlation: {correlation:.2f}, P-value: {p_value:.4f}")
    else:
        print("No data to analyze.")
    return jsonify({"task_id": task_id})


@allstock_bp.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = tasks.get(task_id, {"status": "unknown"})
    return jsonify(task)


if __name__ == "__main__":
    # Mocking `get_us_stock_symbols` for this example.
    # def get_us_stock_symbols():
    #     return ["AAPL", "MSFT"]

    symbols = get_us_stock_symbols()  # Retrieve stock symbols
    bars = download_stock_data(symbols, start_date='2021-01-01', end_date='2023-12-31')  # Download stock data

    if bars is not None:
        # Analyze correlations
        correlation_results = analyze_stock_data_correlation(bars)

        # Print correlation results
        print("\nCorrelation Results:")
        for stock1, stock2, correlation, p_value in correlation_results:
            print(f"Stocks: {stock1} & {stock2}, Correlation: {correlation:.2f}, P-value: {p_value:.4f}")
    else:
        print("No data to analyze.")
