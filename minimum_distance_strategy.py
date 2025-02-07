import os
import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, flash, redirect, url_for, session
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
import numpy as np
from flask import Blueprint, request, render_template
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame

from account_management import getCursor

# Alpaca API credentials
API_KEY = 'PK30X482MH0Y5RX80FPR'
API_SECRET = 'LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano'

# Define the blueprint
maxmindistance_strategy = Blueprint('strategy', __name__, template_folder='templates')
maxmindistance_backtest = Blueprint('backtest', __name__, template_folder='templates')

# Create a blueprint for minimumdistance
minimumdistance_bp = Blueprint('minimumdistance', __name__, template_folder='templates')
# Obtain the optimal pairs
pairs_info = {}  # including date
pairs_list = []  # including stock symbols
risk_metrics = {} # including risk metrics

# Initialize Alpaca client
client = TradingClient(API_KEY, API_SECRET)
def is_valid_ticker(ticker: str) -> bool:
    try:
        # obtain stock information
        asset = client.get_asset(ticker)
        # to check the stock is whether tradable
        return asset.tradable
    except Exception as e:
        print(f"Error checking ticker {ticker}: {e}")
        return False

# Step 1: Get stock data
# def get_data(tickers, start, end):
#     data = yf.download(tickers, start=start, end=end)['Adj Close']
#     return data


# Step 1: Get stock data
def get_data(tickers, start, end):
    print('get_data')
    # 初始化数据客户端
    data_client = StockHistoricalDataClient(API_KEY, API_SECRET)
    # Prepare request parameters
    request_params = StockBarsRequest(
        symbol_or_symbols=tickers,  # List of tickers
        timeframe=TimeFrame.Day,    # Daily data
        start=pd.Timestamp(start, tz="UTC"),  # Start date
        end=pd.Timestamp(end, tz="UTC"),      # End date
    )

    # Fetch data
    bars = data_client.get_stock_bars(request_params)
    # print('get_data-tickers', tickers, 'get_data-bars', bars)

    # Convert to DataFrame and filter only adjusted close prices
    df = bars.df  # Access the resulting DataFrame
    df = df.pivot_table(values="close", index="timestamp", columns="symbol")  # Pivot to get symbols as columns

    return df


# Step 2: Standardize stock prices
def normalize_prices(prices):
    return prices / prices.iloc[0]


# Step 3: Calculate the square distance
def squared_distance(series1, series2):
    return np.sum((series1 - series2) ** 2)


# Step 4: Find the stock pairs with the smallest distance
def find_pairs_min_distance(stock_data, formation_period):
    tickers = stock_data.columns
    n = len(tickers)
    min_distance = float('inf')
    best_pair = (None, None)

    for i in range(n):
        for j in range(i+1, n):
            stock1 = stock_data[tickers[i]].iloc[:formation_period]
            stock2 = stock_data[tickers[j]].iloc[:formation_period]
            norm_stock1 = normalize_prices(stock1)
            norm_stock2 = normalize_prices(stock2)
            distance = squared_distance(norm_stock1, norm_stock2)

            if distance < min_distance:
                min_distance = distance
                best_pair = (tickers[i], tickers[j])

    # # Insert query
    # query = """
    # INSERT INTO stock_analysis_2 (Symbol_1, Symbol_2, min_distance)
    # VALUES (%s, %s, %s, %s)
    # """
    # data = (best_pair[0], best_pair[1], min_distance)  # Use best_pair[0] for best_pair column
    #
    # cursor, connection = getCursor()
    #
    # # Execute and commit
    # cursor.execute(query, data)
    # connection.commit()

    return best_pair, min_distance

# Define a pandas Series
data = []
norm_stock1 = pd.Series(data)
norm_stock2 = pd.Series(data)
stock_pairs_info = {}

# Step 5: Pair trading strategies
def pairs_trading(stock1, stock2, window_size, threshold):
    global norm_stock1
    global norm_stock1
    global stock_pairs_info

    norm_stock1 = normalize_prices(stock1)
    norm_stock2 = normalize_prices(stock2)

    # The initial signal length is window size
    signals = [0] * window_size
    for i in range(window_size, len(norm_stock1)):
        spread = norm_stock1.iloc[i] - norm_stock2.iloc[i]
        # print('spread', spread, 'norm_stock1.iloc[i]', norm_stock1.iloc[i], 'norm_stock2.iloc[i]', norm_stock2.iloc[i])

        if spread > threshold:
            signals.append(-1)  # Short stock 1, long stock 2
        elif spread < -threshold:
            signals.append(1)   # Short stock 2, long stock 1
        else:
            signals.append(0)   # No trading
    print('----1----')
    print('pairs_list[0]', pairs_list[0])
    stock_pairs_info[pairs_list[0]] = norm_stock1
    stock_pairs_info[pairs_list[1]] = norm_stock2
    print('------2------', norm_stock1, '------3------',  norm_stock2)
    # print('stock1', stock1, 'norm_stock1', norm_stock1, 'stock2', stock2, 'norm_stock2', norm_stock2)

    return signals

# def pairs_trading(norm_stock1, norm_stock2, window_size, threshold):
#     try:
#         print('Validating inputs...')
#         if not hasattr(norm_stock1, 'iloc') or not hasattr(norm_stock2, 'iloc'):
#             raise ValueError("Inputs must be pandas Series.")
#
#         print('Inputs validated successfully.')
#         # Initialize signals
#         signals = [0] * window_size
#         for i in range(window_size, len(norm_stock1)):
#             spread = norm_stock1.iloc[i] - norm_stock2.iloc[i]
#             print('spread:', spread, 'norm_stock1.iloc[i]:', norm_stock1.iloc[i], 'norm_stock2.iloc[i]:', norm_stock2.iloc[i])
#
#             if spread > threshold:
#                 signals.append(-1)  # Short stock 1, long stock 2
#             elif spread < -threshold:
#                 signals.append(1)   # Short stock 2, long stock 1
#             else:
#                 signals.append(0)   # No trading
#         return signals[-1]
#     except Exception as e:
#         print(f"Error in pairs_trading: {e}")
#         raise

# Step 6: strategy backtest
# calculate returns
# def cumulative_returns(stock1, stock2, signals):
#     # Remove the last signal
#     positions = np.array(signals[:-1])
#     returns = (stock1.pct_change() - stock2.pct_change())[1:]
#
#     # Keep positions and returns the same length
#     min_len = min(len(positions), len(returns))
#     print('min_len', min_len)
#     positions = positions[:min_len]
#     # print('positions', positions)
#     returns = returns[:min_len]
#     # print('returns', returns)
#
#     strategy_returns = positions * returns.values
#     # print('strategy_returns', strategy_returns)
#     total_returns = np.cumsum(strategy_returns)
#     # total_returns = np.array([np.cumsum(strategy_returns)])
#     # total_returns = sum(strategy_returns)
#
#     return returns, total_returns

def cumulative_returns(stock1, stock2, signals):
    import numpy as np
    import pandas as pd

    # Remove the last signal
    positions = np.array(signals[:-1])

    # Calculate percentage changes for both stocks
    returns = (stock1.pct_change() - stock2.pct_change())[1:]  # Skip the first NaN value

    # Align positions and returns to the same length
    min_len = min(len(positions), len(returns))
    print('min_len', min_len)
    positions = positions[:min_len]
    returns = returns[:min_len]

    # Calculate strategy returns
    strategy_returns = positions * returns.values

    # Create a pandas Series for total returns with timestamps
    total_returns = pd.Series(np.cumsum(strategy_returns), index=returns.index)
    print('total_returns', total_returns)

    return returns, total_returns


# Step 7: Calculate performance metrics for backtest
def backtest(returns, total_returns):
    import numpy as np
    import pandas as pd
    global risk_metrics
    # Total Return
    # total_return = total_returns[-1] / (total_returns[0] - 1) if total_returns[0] != 0 else 0
    print('total_returns', total_returns)
    total_return = total_returns[-1] / (total_returns[0] - 1)
    # total_return = round(total_return, 2)
    if isinstance(total_returns, np.ndarray):
        total_returns = np.round(total_returns, 2)
    else:
        total_returns = round(total_returns, 2)

    # Annualized Return
    annual_return = (1 + total_return) ** (252 / len(total_returns)) - 1
    annual_return = round(annual_return, 2)

    # Volatility (Standard Deviation)
    volatility = np.std(total_returns) * np.sqrt(252)  # Annualized volatility
    volatility = round(volatility, 2)

    # Sharpe Ratio (Assume a risk-free rate of 1%)
    risk_free_rate = 0.01
    excess_returns = total_returns - (risk_free_rate / 252)  # daily excess return
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0
    sharpe_ratio = round(sharpe_ratio, 2)

    # Maximum Drawdown
    cumulative_returns = np.cumsum(total_returns)
    max_drawdown = np.min(cumulative_returns - np.maximum.accumulate(cumulative_returns))
    max_drawdown = round(max_drawdown, 2)

    # Stability: Volatility
    stability = volatility

    # Efficiency: Sharpe ratio (higher is better)
    efficiency = sharpe_ratio
    efficiency = round(efficiency, 2)

    # Volatility: Calculate annualized volatility based on daily returns
    # print('cumulative_returns', cumulative_returns, 'cumulative_returns type', type(cumulative_returns))
    # cumulative_returns as a numpy array
    cumulative_returns = np.array(cumulative_returns)
    # Convert to pandas Series
    cumulative_returns_series = pd.Series(cumulative_returns)
    daily_returns = pd.Series(cumulative_returns).pct_change().dropna()

    # Calculate daily returns and drop NaN values
    # daily_returns = cumulative_returns_series.pct_change().dropna()
    # Replace invalid values
    daily_returns = daily_returns.replace([np.inf, -np.inf], np.nan).dropna()
    daily_returns = daily_returns[1:]
    print('daily_returns', daily_returns)
    if daily_returns.empty or daily_returns.isna().all():
        # print("Error: No valid daily returns data.")
        annual_volatility = None
    else:
        # Calculate annual volatility
        # annual_volatility = daily_returns.std() * (252 ** 0.5)
        annual_volatility = daily_returns.std() * np.sqrt(252)
        if isinstance(annual_volatility, np.ndarray):
            annual_volatility = np.round(annual_volatility, 2)
        else:
            annual_volatility = round(annual_volatility, 2)

    print('annual_volatility', daily_returns.std())
    print('annual_volatility', annual_volatility)

    # Win ratio: The percentage of earnings signals counted in Signals
    # win_rate = sum(signals['profit'] > 0) / len(signals)
    # Convert to list of dictionaries
    signals_dic = [{'profit': value} for value in returns]
    print('signals_dic', signals_dic)
    win_rate = sum(signal['profit'] > 0 for signal in signals_dic) / len(returns)
    win_rate = round(win_rate, 2)
    print('win_rate', win_rate)

    # Profit/loss ratio: The ratio of the average profit on a profitable trade to the average loss on a losing trade.
    # avg_profit = signals[signals['profit'] > 0]['profit'].mean()
    # avg_loss = signals[signals['profit'] <= 0]['profit'].mean()
    # profit_loss_ratio = avg_profit / abs(avg_loss)

    # Calculate average profit (only profits > 0)
    positive_profits = [signal['profit'] for signal in signals_dic if signal['profit'] > 0]
    avg_profit = sum(positive_profits) / len(positive_profits) if positive_profits else 0

    # Calculate average loss (only profits <= 0)
    negative_profits = [signal['profit'] for signal in signals_dic if signal['profit'] <= 0]
    avg_loss = sum(negative_profits) / len(negative_profits) if negative_profits else 0

    # Calculate profit/loss ratio (avg_profit / abs(avg_loss))
    profit_loss_ratio = avg_profit / abs(avg_loss) if avg_loss != 0 else float('inf')
    if isinstance(profit_loss_ratio, np.ndarray):
        profit_loss_ratio = np.round(profit_loss_ratio, 2)
    else:
        profit_loss_ratio = round(profit_loss_ratio, 2)

    # Print results
    print('Average Profit:', avg_profit)
    print('Average Loss:', avg_loss)
    print('Profit/Loss Ratio:', profit_loss_ratio)

    # 交易次数：信号数量
    num_trades = len(returns)

    # 基准对比收益：将策略收益与市场指数（如 S&P 500）对比。
    # benchmark_returns = benchmark_cumulative_returns[-1] / benchmark_cumulative_returns[0] - 1
    # alpha = total_return - benchmark_returns

    # Beta值：计算策略收益与基准收益的回归系数。
    # beta = np.cov(daily_returns, benchmark_daily_returns)[0, 1] / np.var(benchmark_daily_returns)


    # Initialize Alpaca client
    client = StockHistoricalDataClient(API_KEY, API_SECRET)

    # Parameters
    benchmark_ticker = "SPY"  # SPY ETF as a proxy for S&P 500
    # start_date = "2020-01-01"
    # end_date = "2023-01-01"
    start_date = pairs_info['start_date']
    end_date = pairs_info['end_date']

    # Fetch benchmark data
    request_params = StockBarsRequest(
        symbol_or_symbols=benchmark_ticker,
        timeframe=TimeFrame.Day,
        start=pd.Timestamp(start_date, tz="UTC"),
        end=pd.Timestamp(end_date, tz="UTC"),
    )

    # Get benchmark historical data
    bars = client.get_stock_bars(request_params)
    df = bars.df.reset_index()  # Reset index to access 'timestamp' column if needed
    df = df[df['symbol'] == benchmark_ticker]  # Filter for benchmark ticker

    # Extract adjusted closing prices
    benchmark_data = df.set_index('timestamp')['close']

    # Calculate daily returns
    benchmark_daily_returns = benchmark_data.pct_change().dropna()
    # print('daily_returns:', daily_returns, 'benchmark_daily_returns:', benchmark_daily_returns)

    # Calculate cumulative returns
    benchmark_cumulative_returns = (1 + benchmark_daily_returns).cumprod()

    # Calculate benchmark return
    # benchmark_returns = benchmark_cumulative_returns[-1] / benchmark_cumulative_returns[0] - 1
    # Accessing values by position using iloc
    benchmark_returns = benchmark_cumulative_returns.iloc[-1] / benchmark_cumulative_returns.iloc[0] - 1

    # Assuming `daily_returns` and `total_return` are already calculated for your strategy
    # Replace these with actual data
    # daily_returns = strategy_returns / strategy_initial_investment
    # daily_returns = np.random.normal(0, 0.01, len(benchmark_daily_returns))  # Replace with actual daily returns
    # total_return = np.sum(daily_returns)  # Replace with actual total return
    # Clean up data
    daily_returns = np.nan_to_num(daily_returns, nan=0.0, posinf=0.0, neginf=0.0)
    daily_returns = np.clip(daily_returns, -0.99, 0.99)  # Avoid values less than -1

    # Calculate total and cumulative return
    total_return = np.sum(daily_returns)
    cumulative_return = np.prod(1 + daily_returns) - 1

    print(f"Total Return: {total_return}")
    print(f"Cumulative Return: {cumulative_return}")
    print('total_return', total_return)
    if isinstance(total_return, np.ndarray):
        total_return = np.round(total_return, 2)
    else:
        total_return = round(total_return, 2)

    # Alpha: Strategy performance vs. benchmark
    alpha = total_return - benchmark_returns
    if isinstance(alpha, np.ndarray):
        alpha = np.round(alpha, 2)
    else:
        alpha = round(alpha, 2)

    # print('backtest-alpha', alpha)

    # Beta: Covariance of strategy returns with benchmark returns
    # print('daily_returns', daily_returns, 'benchmark_daily_returns', benchmark_daily_returns, 'benchmark_daily_returns', benchmark_daily_returns)
    # beta = np.cov(daily_returns, benchmark_daily_returns)[0, 1] / np.var(benchmark_daily_returns)
    # Ensure inputs are numpy arrays
    strategy_returns = np.array(daily_returns)
    # print('--length:', len(strategy_returns))
    benchmark_returns = np.array(benchmark_daily_returns)
    # print('--length:', len(benchmark_returns))
    minilength = min(len(strategy_returns), len(benchmark_returns))
    # print('minilength', minilength)
    strategy_returns = strategy_returns[:minilength]
    print('--length:', len(strategy_returns))
    benchmark_returns = benchmark_returns[:minilength]
    print('--length:', len(benchmark_returns))

    # Compute covariance matrix (2x2)
    covariance_matrix = np.cov(strategy_returns, benchmark_returns)

    # Extract covariance between stock and benchmark (off-diagonal element)
    covariance = covariance_matrix[0, 1]

    # Compute variance of benchmark returns
    variance = np.var(benchmark_returns, ddof=1)  # Use ddof=1 for sample variance

    # Calculate beta
    beta = covariance / variance

    if isinstance(beta, np.ndarray):
        beta = np.round(beta, 2)
    else:
        beta = round(beta, 2)

    # total_return = 0.15  # 策略总收益
    # benchmark_returns = 0.10  # 基准总收益
    risk_free_rate = 0.02  # 无风险收益率
    beta = 1.2  # 策略的 Beta

    # 计算市场超额收益
    market_excess_return = benchmark_returns - risk_free_rate

    # # 计算 Alpha
    # alpha = total_return - (risk_free_rate + beta * market_excess_return)
    # if isinstance(alpha, np.ndarray):
    #     alpha = np.round(alpha, 2)
    # else:
    #     alpha = round(alpha, 2)
    #
    # print(f"Alpha: {alpha}")

    # Output results
    print(f"Benchmark Returns: {benchmark_returns.mean():.4f}")
    print(f"Alpha: {alpha:.4f}")
    # print(f"Alpha: {alpha}")
    print(f"Beta: {beta:.4f}")

    risk_metrics['volatility'] = volatility
    risk_metrics['sharpe_ratio'] = sharpe_ratio
    risk_metrics['max_drawdown'] = max_drawdown
    risk_metrics['stability'] = stability
    risk_metrics['annual_volatility'] = annual_volatility

    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'stability': stability,
        'efficiency': efficiency,
        'annual_volatility': annual_volatility,
        'win_rate': win_rate,
        'profit_loss_ratio': profit_loss_ratio,
        'num_trades': num_trades,
        'alpha': alpha,
        'beta': beta
    }


@maxmindistance_strategy.route('/set_up_parameter', methods=['POST'])
def set_up_parameter():
    global pairs_info  # Use the global dictionary to store parameters

    print('set_up_parameter')
    try:
        # Retrieve form data
        start_date = request.form.get('start_date')
        print('start_date', start_date)
        end_date = request.form.get('end_date')
        formation_period = request.form.get('formation_period')
        trading_period = request.form.get('trading_period')
        window_size = request.form.get('window_size')
        threshold = request.form.get('threshold')

        # Validate inputs
        if not (start_date and end_date and formation_period and trading_period and window_size and threshold):
            flash("All fields are required.", "danger")
            return redirect(url_for('maxmindistance_strategy.parameter_form'))

        # Store validated parameters in the dictionary
        pairs_info = {
            "pairs_list": pairs_list,
            "start_date": start_date,
            "end_date": end_date,
            "formation_period": int(formation_period),
            "trading_period": int(trading_period),
            "window_size": int(window_size),
            "threshold": float(threshold)
        }
        print('pairs_info', pairs_info)

        # flash("Parameters set successfully!", "success")
        return {"message": "Parameters set successfully!", "pairs_info": pairs_info}, 200

    except ValueError as e:
        # flash(f"Invalid input: {e}", "danger")
        return "Error: No parameters set successfully!.", 400  # Return an error response if Parameters not set successfully!

# @maxmindistance_strategy.route('/parameter_form')
# def parameter_form():
#     # Render the HTML form for parameter setup
#     print(parameter_form)
#     return render_template('parameter_form.html', parameter=parameter)


@maxmindistance_strategy.route('/strategy1')
def strategy1():
    global pairs_info
    try:
        # Step 1: Define Parameters
        # tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']  # List of tickers
        # start_date = '2020-01-01'
        # end_date = '2023-01-01'
        # tickers = pairs_info['pairs_list']
        print('pairs_info', pairs_info)
        tickers = pairs_info.get('pairs_list', [])
        if len(tickers) == 0:
            return render_template('error.html', message="The pairs list is empty.")

        print('strategy1-tickers', tickers, 'pairs_info', pairs_info)
        print('0')
        if len(tickers) <= 1:
            return render_template('error.html', message="Not enough tickers to perform the strategy.")
        print("pairs_info['start_date']", pairs_info)
        if 'formation_period' not in pairs_info:
            print('1')
            start_date = pairs_info['start_date']
            end_date = pairs_info['end_date']
            print('start_date', start_date, 'end_date', end_date, 'pairs_info', pairs_info)
            formation_period = 252  # Formation period (1 year)
            trading_period = 252  # Trading period (1 year)
            window_size = 30  # Rolling window size
            threshold = 0.02  # Price spread threshold
        else:
            print('2')
            print('pairs_info', pairs_info)
            start_date = pairs_info['start_date']
            print('start_date', start_date)
            end_date = pairs_info['end_date']
            formation_period = pairs_info['formation_period']  # Formation period (1 year)
            trading_period = pairs_info['trading_period']  # Trading period (1 year)
            window_size = pairs_info['window_size']  # Rolling window size
            threshold = pairs_info['threshold']  # Price spread threshold

        print('3')
        # Step 2: Fetch Stock Data
        data = get_data(tickers, start=start_date, end=end_date)
        print('strategy1-data', data)
        if data.empty:
            return render_template('error.html', message="Failed to retrieve stock data.")

        # Step 3: Identify Pair with Minimum Distance
        best_pair, min_distance = find_pairs_min_distance(data, formation_period)
        print(f"Best pair: {best_pair}, Minimum distance: {min_distance}")

        # Step 4: Extract Trading Data for the Pair
        # print('length of best_pair[0]', len(best_pair[0]))
        # stock1 = data[best_pair[0]].iloc[formation_period:formation_period + trading_period]
        # # print('stock1', stock1)
        # print('length of best_pair[1]', len(best_pair[1]))
        # stock2 = data[best_pair[1]].iloc[formation_period:formation_period + trading_period]
        # # print('stock2', stock2)
        stock1 = best_pair[0]
        print('best_pair[0]', best_pair[0])
        stock1 = data[best_pair[0]]
        print('data[best_pair[0]]', data[best_pair[0]])
        stock2 = best_pair[1]
        print('best_pair[1]', best_pair[1])
        stock2 = data[best_pair[1]]
        print('data[best_pair[1]]', data[best_pair[1]])

        # Step 5: Generate Trading Signals
        signals = pairs_trading(stock1, stock2, window_size, threshold)
        print('signals', signals)

        # Step 6: Backtest the Strategy
        returns, total_returns = cumulative_returns(stock1, stock2, signals)
        print('4')

        # print('the type of total_returns', type(total_returns), 'total_returns', total_returns)
        metrics = backtest(returns, total_returns)
        print('metrics', metrics)
        print('4')
        # Step 7: Visualize the Results using Base64 Encoding
        from matplotlib.figure import Figure
        import io
        import base64

        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(total_returns, label='Cumulative Strategy Returns', color='blue')
        ax.set_title(f"Pair Trading Strategy for {best_pair}")
        ax.set_xlabel('Time')
        ax.set_ylabel('Cumulative Returns')
        ax.legend()
        ax.grid(True)
        print('5')

        # Save the plot as a Base64-encoded image
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        print('6')

        # Step 8: Render the Results
        # Render the HTML template and pass the image data
        # return render_template('backtest_strategy1.html', best_pair=best_pair, min_distance=min_distance, img_data=img_data)
        return render_template('backtest_strategy1.html', metrics=metrics, img_data=img_data)

    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('error.html', message=str(e))


@maxmindistance_backtest.route('/backtest1')
def backtest1():
    print("backtest 1 route accessed")
    return "backtest 1 executed successfully!"


@minimumdistance_bp.route('/minimumdistance_stockpair1', methods=['POST'])
def minimumdistance_stockpair1():
    global pairs_list
    global pairs_info
    # Retrieve form data
    stock = request.form.get('stock').upper()  # Stock symbol
    print('minimumdistance_stockpair1')
    button_name = request.form
    print('button_name', button_name)
    # Perform logic with stock
    if not stock or not is_valid_ticker(stock):
        return "Error: No stock provided.", 400  # Return an error response if 'stock' is missing

    if 'minimum_add' in request.form:
        print('minimumdistance_stockpair1-minimum_add')
        # Append stock into pairs_list
        pairs_list.append(stock)
        pairs_info['pairs_list'] = pairs_list
        print('pairs_list', pairs_list)
        print('pairs_info', pairs_info)
        # Return a success response
        message = "Stock added successfully"
        # return {"message": "Stock added successfully", "pairs_list": pairs_list}, 200
        return render_template('minimum_distance.html', message=message)
    elif 'minimum_remove' in request.form:
        print('minimumdistance_stockpair1-minimum_remove')
        # Remove all stocks from pairs_list
        pairs_list = []
        print('pairs_list', pairs_list)
        # Return a success response
        message = "Stock removed successfully"
        return render_template('minimum_distance.html', message=message)
        # return {"message": "Stock removed successfully", "pairs_list": []}, 200

    # # Return a success response
    message = "bad request!"
    return render_template('minimum_distance.html', message=message)
    # return {"message": "bad request!"}, 200


@minimumdistance_bp.route('/minimumdistance_stockpair4', methods=['POST'])
def minimumdistance_stockpair4():
    import io
    import base64
    from matplotlib.figure import Figure
    # using global pairs_info
    global pairs_info
    global pairs_list

    print('minimumdistance_stockpair2')
    # Retrieve form data
    start_date = request.form.get('start_date')  # Start date
    end_date = request.form.get('end_date')  # End date
    print('start_date', start_date, 'end_date', end_date)
    # Check if the required data is provided
    if not start_date or not end_date:
        return {"message": "Error: Both start_date and end_date are required."}, 400

    # Update the pairs_info dictionary
    pairs_info['start_date'] = start_date
    pairs_info['end_date'] = end_date
    try:
        tickers = pairs_info['pairs_list']
        # print('strategy1-tickers', tickers)
        if len(tickers) <= 1:
            return {"message": "Error: The number of tickers must be two."}, 400
        start_date = pairs_info['start_date']
        end_date = pairs_info['end_date']
        print('start_date', start_date, 'end_date', end_date)
        formation_period = 252  # Formation period (1 year)

        # Step 2: Fetch Stock Data
        data = get_data(tickers, start=start_date, end=end_date)
        # print('strategy1-data', data)
        if data.empty:
            return render_template('error.html', message="Failed to retrieve stock data.")

        # Step 3: Identify Pair with Minimum Distance
        best_pair, min_distance = find_pairs_min_distance(data, formation_period)
        min_distance = round(min_distance, 2)
        print(f"Best pair: {best_pair}, Minimum distance: {min_distance}")

         # Step 4: Insert into the database
        stock1, stock2 = best_pair
        query = """
        INSERT INTO stock_analysis_2 (Symbol_1, Symbol_2, min_distance)
        VALUES (%s, %s, %s)
        """
        data_to_insert = (stock1, stock2, min_distance)

        cursor, connection = getCursor()
        cursor.execute(query, data_to_insert)
        connection.commit()
        cursor.close()
        connection.close()

        print('--------')

        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(1, 1, 1)
        stock1 = data[best_pair[0]]
        stock2 = data[best_pair[1]]

        # Plot the price spread
        spread = stock1 - stock2
        ax.plot(spread.index, spread.values, label="Price Spread", color="blue")
        ax.set_title(f"Spread Chart for {best_pair[0]} and {best_pair[1]}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price Spread")
        ax.legend()
        ax.grid(True)

        # Encode the plot as Base64
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        plot_data = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        # Return a success response
        return render_template('minimum_distance.html', best_pair=best_pair, min_distance=min_distance, plot_data=plot_data)
    except:
        message = "Data analysis not successfully"
        return render_template('minimum_distance.html', message=message)


@minimumdistance_bp.route('/minimumdistance_stockpair2', methods=['POST'])
def minimumdistance_stockpair2():
    import io
    import base64
    from matplotlib.figure import Figure

    # Using global variables
    global pairs_info
    global pairs_list

    print('minimumdistance_stockpair2')

    # Retrieve form data
    start_date = request.form.get('start_date')  # Start date
    end_date = request.form.get('end_date')  # End date
    print('start_date', start_date, 'end_date', end_date)

    # Validate input
    if not start_date or not end_date:
        return {"message": "Error: Both start_date and end_date are required."}, 400

    # Update pairs_info with the input dates
    pairs_info['start_date'] = start_date
    pairs_info['end_date'] = end_date

    try:
        tickers = pairs_info.get('pairs_list', [])
        if len(tickers) < 2:
            return {"message": "Error: At least two tickers are required."}, 400

        formation_period = 252  # Formation period (1 year)

        # Step 2: Fetch Stock Data
        data = get_data(tickers, start=start_date, end=end_date)
        if data.empty:
            return render_template('error.html', message="Failed to retrieve stock data.")

        # Step 3: Identify Pair with Minimum Distance
        best_pair, min_distance = find_pairs_min_distance(data, formation_period)
        min_distance = round(min_distance, 2)
        stock1, stock2 = best_pair
        print(f"Best pair: {best_pair}, Minimum distance: {min_distance}")

        try:
            # Step 4: Insert into the database
            query = """
            INSERT INTO stock_analysis_2 (Symbol_1, Symbol_2, min_distance)
            VALUES (%s, %s, %s)
            """
            data_to_insert = (stock1, stock2, min_distance)

            cursor, connection = getCursor()
            cursor.execute(query, data_to_insert)
        except Exception as e:
            print(f"Error analyzing pair {stock1} & {stock2}: {e}")

        # Commit changes and close the connection
        try:
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"Error closing the database connection: {e}")
            # connection.commit()
            # cursor.close()
            # connection.close()

        # Step 5: Generate the spread chart
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(1, 1, 1)

        stock1_data = data[stock1]
        stock2_data = data[stock2]
        spread = stock1_data - stock2_data

        # Plot the price spread
        ax.plot(spread.index, spread.values, label="Price Spread", color="blue")
        ax.set_title(f"Spread Chart for {stock1} and {stock2}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price Spread")
        ax.legend()
        ax.grid(True)

        # Encode the plot as Base64
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        plot_data = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        # Return a success response
        return render_template(
            'minimum_distance.html',
            best_pair=best_pair,
            min_distance=min_distance,
            plot_data=plot_data
        )
    except Exception as e:
        print(f"Error: {e}")
        message = "Data analysis not successfully completed due to an error."
        return render_template('minimum_distance.html', message=message)


@minimumdistance_bp.route('/minimumdistance_stockpair3', methods=['POST'])
def minimumdistance_stockpair3():
    global pairs_list
    global pairs_info
    # Retrieve form data
    stock = request.form.get('stock').upper()  # Stock symbol
    print('minimumdistance_stockpair1')
    button_name = request.form
    print('button_name', button_name)
    # Perform logic with stock
    if not stock or not is_valid_ticker(stock):
        return "Error: No stock provided.", 400  # Return an error response if 'stock' is missing

    if 'minimum_add' in request.form:
        print('minimumdistance_stockpair1-minimum_add')
        # Append stock into pairs_list
        pairs_list.append(stock)
        pairs_info['pairs_list'] = pairs_list
        print('pairs_list', pairs_list)
        print('pairs_info', pairs_info)
        # Return a success response
        message = "Stock added successfully"
        # return {"message": "Stock added successfully", "pairs_list": pairs_list}, 200
        return render_template('minimum_distance_method_parameter_form.html', message=message)
    elif 'minimum_remove' in request.form:
        print('minimumdistance_stockpair1-minimum_remove')
        # Remove all stocks from pairs_list
        pairs_list = []
        print('pairs_list', pairs_list)
        # Return a success response
        message = "Stock removed successfully"
        return render_template('minimum_distance_method_parameter_form.html', message=message)
        # return {"message": "Stock removed successfully", "pairs_list": []}, 200

    # # Return a success response
    message = "bad request!"
    return render_template('minimum_distance_method_parameter_form.html', message=message)
    # return {"message": "bad request!"}, 200


@minimumdistance_bp.route('/minimumdistance_stockpair_page')
def minimumdistance_stockpair_page():
    # print('minimum page')
    return render_template('minimum_distance.html')


@minimumdistance_bp.route('/minimumdistancemethod_page')
def minimumdistancemethod_page():
    # print('minimum page')
    return render_template('minimum_distance_method_parameter_form.html')

@minimumdistance_bp.route('/pairs_trading_minimum_distance')
def pairs_trading_minimum_distance():
    stock_pairs = [['aapl', 'msft', 0.1],]
    return render_template('pairs_trading_minimum_distance.html', stock_pairs=stock_pairs)


if __name__ == '__main__':
    # Step 1: Define Parameters
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']  # List of tickers
    start_date = '2020-01-01'
    end_date = '2023-01-01'
    formation_period = 252  # Formation period (1 year)
    trading_period = 252  # Trading period (1 year)
    window_size = 30  # Rolling window size
    threshold = 0.02  # Price spread threshold

    # Step 2: Fetch Stock Data
    data = get_data(tickers, start=start_date, end=end_date)
    print('data', data)

    # Step 3: Identify Pair with Minimum Distance
    # best_pair, min_distance = find_pairs_min_distance(data, formation_period)
    # # print(f"Best pair: {best_pair}, Minimum distance: {min_distance}")
    #
    # # Step 4: Extract Trading Data for the Pair
    # stock1 = data[best_pair[0]].iloc[formation_period:formation_period + trading_period]
    # # print('stock1', stock1)
    # stock2 = data[best_pair[1]].iloc[formation_period:formation_period + trading_period]
    # # print('stock2', stock2)
    #
    # # Step 5: Generate Trading Signals
    # signals = pairs_trading(stock1, stock2, window_size, threshold)
    # # print('signals', signals)
    #
    # # Step 6: Backtest the Strategy
    # returns, total_returns = cumulative_returns(stock1, stock2, signals)
    # print('returns', returns)
    # # print('the type of total_returns', type(total_returns), 'total_returns', total_returns)
    # metrics = backtest(returns, total_returns)
    # print('metrics', metrics)
