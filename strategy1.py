import os

import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from flask import Blueprint, render_template

# Define the blueprint
maxmindistance_strategy = Blueprint('strategy', __name__, template_folder='templates')


# Step 1: 获取股票数据
def get_data(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)['Adj Close']
    return data


# Step 2: 标准化股票价格
def normalize_prices(prices):
    return prices / prices.iloc[0]

# Step 3: 计算平方距离
def squared_distance(series1, series2):
    return np.sum((series1 - series2) ** 2)

# Step 4: 寻找最小距离的股票对
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

# Step 5: 配对交易策略
def pairs_trading(stock1, stock2, window_size, threshold):
    norm_stock1 = normalize_prices(stock1)
    norm_stock2 = normalize_prices(stock2)

    signals = [0] * window_size  # 初始信号长度为 window_size
    for i in range(window_size, len(norm_stock1)):
        spread = norm_stock1.iloc[i] - norm_stock2.iloc[i]
        print('spread', spread, 'norm_stock1.iloc[i]', norm_stock1.iloc[i], 'norm_stock2.iloc[i]', norm_stock2.iloc[i])

        if spread > threshold:
            signals.append(-1)  # 做空股票1，做多股票2
        elif spread < -threshold:
            signals.append(1)   # 做多股票1，做空股票2
        else:
            signals.append(0)   # 不交易

    return signals

# Step 6: 策略回测
def backtest(stock1, stock2, signals):
    positions = np.array(signals[:-1])  # 去除最后一个信号
    returns = (stock1.pct_change() - stock2.pct_change())[1:]

    # 保持 positions 和 returns 长度一致
    min_len = min(len(positions), len(returns))
    positions = positions[:min_len]
    returns = returns[:min_len]

    strategy_returns = positions * returns.values
    cumulative_returns = np.cumsum(strategy_returns)

    return cumulative_returns


# @maxmindistance_strategy.route('/strategy1')
# def strategy1():
#     print('strategy1')
#     # Step 7: 主函数
#     tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']  # 可以选择更多的股票
#     start_date = '2020-01-01'
#     end_date = '2023-01-01'
#
#     # 获取股票数据
#     data = get_data(tickers, start=start_date, end=end_date)
#
#     # 设定形成期和交易期
#     formation_period = 252  # 形成期：1年
#     trading_period = 252  # 交易期：1年
#
#     # Step 8: 寻找形成期内最小平方距离的股票对
#     best_pair, min_distance = find_pairs_min_distance(data, formation_period)
#     print(f"最小距离的股票对: {best_pair}，最小距离: {min_distance}")
#
#     # Step 9: 交易期内的配对交易
#     stock1 = data[best_pair[0]].iloc[formation_period:formation_period + trading_period]
#     stock2 = data[best_pair[1]].iloc[formation_period:formation_period + trading_period]
#
#     # 设定窗口大小和阈值
#     window_size = 30  # 滚动窗口大小
#     threshold = 0.02  # 根据经验设定的价差阈值
#
#     # 生成交易信号
#     signals = pairs_trading(stock1, stock2, window_size, threshold)
#
#     # 回测策略
#     cumulative_returns = backtest(stock1, stock2, signals)
#
#     # 可视化策略表现
#     plt.figure(figsize=(14, 7))
#     plt.plot(cumulative_returns, label='Cumulative Strategy Returns')
#     plt.title(f'Pair Trading Strategy for {best_pair}')
#     plt.legend()
#     plt.show()
#     return render_template('strategy_file.html')


@maxmindistance_strategy.route('/strategy1')
def strategy1():
    try:
        print('strategy1 started')

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
        if data.empty:
            return render_template('error.html', message="Failed to retrieve stock data.")

        # Step 3: Identify Pair with Minimum Distance
        best_pair, min_distance = find_pairs_min_distance(data, formation_period)
        print(f"Best pair: {best_pair}, Minimum distance: {min_distance}")

        # Step 4: Extract Trading Data for the Pair
        stock1 = data[best_pair[0]].iloc[formation_period:formation_period + trading_period]
        print('stock1', stock1)
        stock2 = data[best_pair[1]].iloc[formation_period:formation_period + trading_period]
        print('stock2', stock2)

        # Step 5: Generate Trading Signals
        signals = pairs_trading(stock1, stock2, window_size, threshold)
        print('signals', signals)

        # Step 6: Backtest the Strategy
        cumulative_returns = backtest(stock1, stock2, signals)
        print('cumulative_returns', cumulative_returns)

        # Step 7: Visualize the Results
        # plt.figure(figsize=(14, 7))
        # plt.plot(cumulative_returns, label='Cumulative Strategy Returns')
        # plt.title(f'Pair Trading Strategy for {best_pair}')
        # plt.legend()

        # Save the plot as an image to serve in the HTML template
        # plot_path = '/static/strategy1_plot.png'
        # plt.savefig(f".{plot_path}")
        # plt.close()

        # Step 7: Visualize the Results using Base64 Encoding
        from matplotlib.figure import Figure
        import io
        import base64

        fig = Figure(figsize=(14, 7))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(cumulative_returns, label='Cumulative Strategy Returns', color='blue')
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
        return render_template(
            'strategy1.html',
            best_pair=best_pair,
            min_distance=min_distance,
            img_data=img_data
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('error.html', message=str(e))


# @maxmindistance_strategy.route('/strategy1')
# def strategy1():
#     print("Strategy 1 route accessed")
#     return "Strategy 1 executed successfully!"


@maxmindistance_strategy.route('/strategy2')
def strategy2():
    print("Strategy 2 route accessed")
    return "Strategy 2 executed successfully!"
