import os

import np as np
import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from flask import Blueprint, render_template

# Define the blueprint
maxmindistance_strategy = Blueprint('strategy', __name__, template_folder='templates')


# Step 1: Get stock data
def get_data(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)['Adj Close']
    return data


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

    return best_pair, min_distance

# Step 5: Pair trading strategies
def pairs_trading(stock1, stock2, window_size, threshold):
    norm_stock1 = normalize_prices(stock1)
    norm_stock2 = normalize_prices(stock2)

    signals = [0] * window_size  # 初始信号长度为 window_size
    for i in range(window_size, len(norm_stock1)):
        spread = norm_stock1.iloc[i] - norm_stock2.iloc[i]
        # print('spread', spread, 'norm_stock1.iloc[i]', norm_stock1.iloc[i], 'norm_stock2.iloc[i]', norm_stock2.iloc[i])

        if spread > threshold:
            signals.append(-1)  # 做空股票1，做多股票2
        elif spread < -threshold:
            signals.append(1)   # 做多股票1，做空股票2
        else:
            signals.append(0)   # 不交易

    return signals


# Step 6: strategy backtest
# calculate returns
def cumulative_returns(stock1, stock2, signals):
    # Remove the last signal
    positions = np.array(signals[:-1])
    returns = (stock1.pct_change() - stock2.pct_change())[1:]

    # Keep positions and returns the same length
    min_len = min(len(positions), len(returns))
    print('min_len', min_len)
    positions = positions[:min_len]
    # print('positions', positions)
    returns = returns[:min_len]
    # print('returns', returns)

    strategy_returns = positions * returns.values
    # print('strategy_returns', strategy_returns)
    total_returns = np.cumsum(strategy_returns)
    # total_returns = np.array([np.cumsum(strategy_returns)])
    # total_returns = sum(strategy_returns)

    return returns, total_returns


# Step 7: Calculate performance metrics for backtest
def backtest(returns, total_returns):
    import numpy as np
    import pandas as pd
    # Total Return
    # total_return = total_returns[-1] / (total_returns[0] - 1) if total_returns[0] != 0 else 0
    total_return = total_returns[-1] / (total_returns[0] - 1)
    total_return = round(total_return, 2)

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

    # Calculate daily returns and drop NaN values
    daily_returns = cumulative_returns_series.pct_change().dropna()
    daily_returns = daily_returns[1:]
    # print('daily_returns', daily_returns)
    if daily_returns.empty or daily_returns.isna().all():
        # print("Error: No valid daily returns data.")
        annual_volatility = None
    else:
        # Calculate annual volatility
        annual_volatility = daily_returns.std() * (252 ** 0.5)
    # print('annual_volatility', daily_returns.std())

    # Win ratio: The percentage of earnings signals counted in Signals
    print('signals', signals)
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

    # Print results
    print('Average Profit:', avg_profit)
    print('Average Loss:', avg_loss)
    print('Profit/Loss Ratio:', profit_loss_ratio)

    # 交易次数：信号数量
    num_trades = len(signals)

    # 基准对比收益：将策略收益与市场指数（如 S&P 500）对比。
    # benchmark_returns = benchmark_cumulative_returns[-1] / benchmark_cumulative_returns[0] - 1
    # alpha = total_return - benchmark_returns

    # Beta值：计算策略收益与基准收益的回归系数。
    # beta = np.cov(daily_returns, benchmark_daily_returns)[0, 1] / np.var(benchmark_daily_returns)

    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    import pandas as pd
    import numpy as np

    # Alpaca API credentials
    API_KEY = 'PK30X482MH0Y5RX80FPR'
    API_SECRET = 'LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano'

    # Initialize Alpaca client
    client = StockHistoricalDataClient(API_KEY, API_SECRET)

    # Parameters
    benchmark_ticker = "SPY"  # SPY ETF as a proxy for S&P 500
    start_date = "2020-01-01"
    end_date = "2023-01-01"

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

    # Calculate cumulative returns
    benchmark_cumulative_returns = (1 + benchmark_daily_returns).cumprod()

    # Calculate benchmark return
    # benchmark_returns = benchmark_cumulative_returns[-1] / benchmark_cumulative_returns[0] - 1
    # Accessing values by position using iloc
    benchmark_returns = benchmark_cumulative_returns.iloc[-1] / benchmark_cumulative_returns.iloc[0] - 1

    # Assuming `daily_returns` and `total_return` are already calculated for your strategy
    # Replace these with actual data
    # Example: daily_returns = strategy_returns / strategy_initial_investment
    daily_returns = np.random.normal(0, 0.01, len(benchmark_daily_returns))  # Replace with actual daily returns
    total_return = np.sum(daily_returns)  # Replace with actual total return

    # Alpha: Strategy performance vs. benchmark
    alpha = total_return - benchmark_returns

    # Beta: Covariance of strategy returns with benchmark returns
    beta = np.cov(daily_returns, benchmark_daily_returns)[0, 1] / np.var(benchmark_daily_returns)

    # Output results
    print(f"Benchmark Returns: {benchmark_returns:.4f}")
    print(f"Alpha: {alpha:.4f}")
    print(f"Beta: {beta:.4f}")

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


@maxmindistance_strategy.route('/strategy1')
def strategy1():
    try:
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
        # print('data', data)
        if data.empty:
            return render_template('error.html', message="Failed to retrieve stock data.")

        # Step 3: Identify Pair with Minimum Distance
        best_pair, min_distance = find_pairs_min_distance(data, formation_period)
        print(f"Best pair: {best_pair}, Minimum distance: {min_distance}")

        # Step 4: Extract Trading Data for the Pair
        stock1 = data[best_pair[0]].iloc[formation_period:formation_period + trading_period]
        # print('stock1', stock1)
        stock2 = data[best_pair[1]].iloc[formation_period:formation_period + trading_period]
        # print('stock2', stock2)

        # Step 5: Generate Trading Signals
        signals = pairs_trading(stock1, stock2, window_size, threshold)
        # print('signals', signals)

        # Step 6: Backtest the Strategy
        total_returns = cumulative_returns(stock1, stock2, signals)
        # print('the type of total_returns', type(total_returns), 'total_returns', total_returns)
        metrics = backtest(total_returns)
        print('metrics', metrics)

        # Step 7: Visualize the Results using Base64 Encoding
        from matplotlib.figure import Figure
        import io
        import base64

        fig = Figure(figsize=(14, 7))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(total_returns, label='Cumulative Strategy Returns', color='blue')
        ax.set_title(f"Pair Trading Strategy for {best_pair}")
        ax.set_xlabel('Time')
        ax.set_ylabel('Cumulative Returns')
        ax.legend()
        ax.grid(True)

        # Save the plot as a Base64-encoded image
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        # Step 8: Render the Results
        # Render the HTML template and pass the image data
        return render_template('strategy1.html', best_pair=best_pair, min_distance=min_distance, img_data=img_data)

    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('error.html', message=str(e))


@maxmindistance_strategy.route('/strategy2')
def strategy2():
    print("Strategy 2 route accessed")
    return "Strategy 2 executed successfully!"


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

    # Step 3: Identify Pair with Minimum Distance
    best_pair, min_distance = find_pairs_min_distance(data, formation_period)
    # print(f"Best pair: {best_pair}, Minimum distance: {min_distance}")

    # Step 4: Extract Trading Data for the Pair
    stock1 = data[best_pair[0]].iloc[formation_period:formation_period + trading_period]
    # print('stock1', stock1)
    stock2 = data[best_pair[1]].iloc[formation_period:formation_period + trading_period]
    # print('stock2', stock2)

    # Step 5: Generate Trading Signals
    signals = pairs_trading(stock1, stock2, window_size, threshold)
    # print('signals', signals)

    # Step 6: Backtest the Strategy
    returns, total_returns = cumulative_returns(stock1, stock2, signals)
    print('returns', returns)
    # print('the type of total_returns', type(total_returns), 'total_returns', total_returns)
    metrics = backtest(returns, total_returns)
    print('metrics', metrics)
