# import requests
# import alpaca_trade_api as trade_api
# import config
import threading
import time

# ORDER_URL = '{}/v2/orders'.format(config.APCA_API_BASE_URL)
#
# def createMarketOrder():
#     ticker = 'AAPL'
#     qty = '2'
#     side = 'buy'
#     ordertype = 'market'
#
#     data = {'symbol': ticker, 'qty': qty, 'side': side, 'type': ordertype, 'time_in_force': 'day'}
#     r = requests.post(ORDER_URL, json=data, headers=config.HEADERS)
#     return r.content
#
#
# def createLimitOrder():
#     ticker = 'AAPL'
#     qty = '2'
#     side = 'buy'
#     ordertype = 'market'
#     limitprice = '140'
#
#     data = {'symbol': ticker, 'qty': qty, 'side': side, 'type': ordertype, 'time_in_force': 'day', 'limit_price': limitprice}
#     r = requests.post(ORDER_URL, json=data, headers=config.HEADERS)
#     return r.content

# print(createMarketOrder())
# print(createLimitOrder())
##########################################################################
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus, QueryOrderStatus
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for, flash

APCA_API_KEY_ID = 'PK30X482MH0Y5RX80FPR'
APCA_API_SECRET_KEY = 'LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano'

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.enums import OrderStatus


# Authenticate the client
client_trading = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)

qty_num_sell = 0
qty_num_buy = 0

# Prepare the Sell order
request_order = MarketOrderRequest(
    symbol='SPY',
    qty=1,
    side=OrderSide.SELL,
    time_in_force=TimeInForce.GTC
)

# Prepare the buy order
request_order = MarketOrderRequest(
    symbol='SPY',
    qty=1,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.GTC
)

try:
    # Retrieve open orders
    # Different order states for apis
    # Open: Commission order, not yet closed.
    # Filled: The order is filled.
    # Partially Filled: The order is partially filled, but there is still some remaining.
    # Cancelled: The order has been cancelled.
    # Rejected: The order is rejected.
    # Pending: The order is pending.
    # accepted：The order is received，but not filled

    all_orders = client_trading.get_orders()
    # print("Retrieved all orders:", all_orders)

    # Manually filter based on status if needed
    fill_orders = [order for order in all_orders if order.status == "Filled"]
    # print("Filtered filled orders:", fill_orders)
    open_orders = [order for order in all_orders if order.status == "accepted"]
    # print("Filtered opened orders:", open_orders)

    if not open_orders:
        print("No open orders found. Proceeding with order submission.")
        request_order_submit = client_trading.submit_order(order_data=request_order)
        print("Order submitted successfully!")
        print(request_order_submit)
    else:
        print("Conflicting open orders exist. Review and cancel them if needed:")
        for order in open_orders:
            print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
#     # request_order_submit = client_trading.submit_order(order_data=request_order)
#     # client_trading.cancel_order_by_id(order_id="92e70b70-ed02-4be4-959b-308d0fd594e8")
except Exception as e:
    print("An error occurred while submitting the order:", e)


###############################stop profit and loss#########################################
# import alpaca.trading.requests
# from alpaca.trading.enums import OrderSide, TimeInForce
#
# bracket_order = alpaca.trading.requests.BracketOrderRequest(
#     symbol="SPY",
#     qty=1,
#     side=OrderSide.BUY,
#     time_in_force=TimeInForce.GTC,
#     take_profit={"limit_price": 450.00},  # Replace with your desired price
#     stop_loss={"stop_price": 430.00}     # Replace with your desired price
# )
#
# client_trading.submit_order(order_data=bracket_order)

##########################check for existing order############################
# open_orders = client_trading.list_orders(status='open')
# for order in open_orders:
#     print(order)
###########################cancel for order##################################
# client_trading.cancel_order_by_id(order_id="d9983490-9f7f-48f6-937b-b3d74ec0d877")
##########################################################################
# import alpaca_trade_api as trade_api
# #api key linked from env file
# APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'
# APCA_API_KEY_ID = 'PK30X482MH0Y5RX80FPR'
# APCA_API_SECRET_KEY = 'LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano'
#
# alpaca = trade_api.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL, api_version='v2')
# account = alpaca.get_account()
# print(account.status)
#
# AMSC_order = alpaca.submit_order('AMSC', qty=1, side='buy', type='market')
# AAPL_order = alpaca.submit_order('AAPL', qty=1, side='sell', type='market')
# print(AMSC_order)

# Define the blueprint
order_bp = Blueprint('order', __name__, template_folder='templates')


# Route to handle GET and POST requests
# buy stock1, and sell stock2
@order_bp.route('/order_buy', methods=['GET', 'POST'])
def order_buy_pair():
    print('order_buy_pair-1')
    if request.method == 'POST':
        print('order_buy_pair-2')
        # Retrieve form data
        stock_code1 = request.form.get('stock_code1')
        stock_code2 = request.form.get('stock_code2')
        quantity_stock1 = request.form.get('quantity_stock1')
        quantity_stock2 = request.form.get('quantity_stock2')
        action = 'Long' if request.form.get('buy') else 'Short'  # Determine action based on button clicked

        # Process or display the received data (this can be adjusted for your needs)
        # print(f"Stock Code 1: {stock_code1}")
        # print(f"Stock Code 2: {stock_code2}")
        # print(f"Quantity for Stock 1: {quantity_stock1}")
        # print(f"Quantity for Stock 2: {quantity_stock2}")
        # print(f"Action: {action}")

        # Prepare the buy order
        request_order_buy = MarketOrderRequest(
            symbol=stock_code1,
            qty=quantity_stock1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC
        )

        try:
            print('order_buy_pair-3')
            all_orders = client_trading.get_orders()
            # print("Retrieved all orders:", all_orders)

            # Manually filter based on status if needed
            fill_orders = [order for order in all_orders if order.status == "Filled"]
            # print("Filtered filled orders:", fill_orders)
            open_orders = [order for order in all_orders if order.status == "accepted"]
            # print("Filtered opened orders:", open_orders)

            if not open_orders:
                # print("No open orders found. Proceeding with order submission.")
                request_order_submit = client_trading.submit_order(order_data=request_order_buy)
                # print("Order submitted successfully!")
                # print(request_order_submit)
            else:
                # print("Conflicting open orders exist. Review and cancel them if needed:")
                for order in open_orders:
                    print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
        except Exception as e:
            print("An error occurred while submitting the order:", e)

        # Prepare the Sell order
        request_order_sell = MarketOrderRequest(
            symbol=stock_code2,
            qty=quantity_stock2,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        try:
            all_orders = client_trading.get_orders()
            # print("Retrieved all orders:", all_orders)

            # Manually filter based on status if needed
            fill_orders = [order for order in all_orders if order.status == "Filled"]
            # print("Filtered filled orders:", fill_orders)
            open_orders = [order for order in all_orders if order.status == "accepted"]
            # print("Filtered opened orders:", open_orders)

            if not open_orders:
                print("No open orders found. Proceeding with order submission.")
                request_order_submit = client_trading.submit_order(order_data=request_order_sell)
                print("Order submitted successfully!")
                print(request_order_submit)
            else:
                print("Conflicting open orders exist. Review and cancel them if needed:")
                for order in open_orders:
                    print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
        except Exception as e:
            print("An error occurred while submitting the order:", e)
    return render_template('dashboard.html')


# Route to handle GET and POST requests
# sell stock1, and buy stock2
@order_bp.route('/order_sell', methods=['GET', 'POST'])
def order_sell_pair():
    if request.method == 'POST':
        # Retrieve form data
        stock_code1 = request.form.get('stock_code1')
        stock_code2 = request.form.get('stock_code2')
        quantity_stock1 = request.form.get('quantity_stock1')
        quantity_stock2 = request.form.get('quantity_stock2')
        action = 'Long' if request.form.get('buy') else 'Short'  # Determine action based on button clicked

        # Process or display the received data (this can be adjusted for your needs)
        print(f"Stock Code 1: {stock_code1}")
        print(f"Stock Code 2: {stock_code2}")
        print(f"Quantity for Stock 1: {quantity_stock1}")
        print(f"Quantity for Stock 2: {quantity_stock2}")
        # print(f"Action: {action}")

        # Prepare the SELL order
        request_order_sell = MarketOrderRequest(
            symbol=stock_code1,
            qty=quantity_stock1,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )

        try:
            print('sell-sell')
            all_orders = client_trading.get_orders()
            # print("Retrieved all orders:", all_orders)

            # Manually filter based on status if needed
            fill_orders = [order for order in all_orders if order.status == "Filled"]
            # print("Filtered filled orders:", fill_orders)
            # open_orders = [order for order in all_orders if order.status == "accepted"]
            # print("Filtered opened orders:", open_orders)
            open_orders = False

            if not open_orders:
                print("No open orders found. Proceeding with order submission.")
                request_order_submit = client_trading.submit_order(order_data=request_order_sell)
                print("Order submitted successfully!")
                print(request_order_submit)
            else:
                print("Conflicting open orders exist. Review and cancel them if needed:")
                for order in open_orders:
                    print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
        except Exception as e:
            print("An error occurred while submitting the order:", e)


        # Prepare the buy order
        request_order_buy = MarketOrderRequest(
            symbol=stock_code2,
            qty=quantity_stock2,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC
        )
        try:
            print('sell-buy')
            all_orders = client_trading.get_orders()
            # print("Retrieved all orders:", all_orders)

            # Manually filter based on status if needed
            fill_orders = [order for order in all_orders if order.status == "Filled"]
            # print("Filtered filled orders:", fill_orders)
            # open_orders = [order for order in all_orders if order.status == "accepted"]
            # print("Filtered opened orders:", open_orders)
            open_orders = False

            if not open_orders:
                print("No open orders found. Proceeding with order submission.")
                request_order_submit = client_trading.submit_order(order_data=request_order_buy)
                print("Order submitted successfully!")
                print(request_order_submit)
            else:
                print("Conflicting open orders exist. Review and cancel them if needed:")
                for order in open_orders:
                    print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
        except Exception as e:
            print("An error occurred while submitting the order:", e)
    return render_template('dashboard.html')


def order_buy_pair(stock_code1, quantity_stock1, stock_code2, quantity_stock2):
    global qty_num_sell
    global qty_num_buy
    # Prepare the buy order
    request_order_buy = MarketOrderRequest(
        symbol=stock_code1,
        qty=quantity_stock1,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )

    try:
        print('order_buy_pair-3')
        all_orders = client_trading.get_orders()
        # print("Retrieved all orders:", all_orders)

        # Manually filter based on status if needed
        fill_orders = [order for order in all_orders if order.status == "Filled"]
        # print("Filtered filled orders:", fill_orders)
        open_orders = [order for order in all_orders if order.status == "accepted"]
        # print("Filtered opened orders:", open_orders)
        open_orders_or_not = False

        if qty_num_buy < 1:
            # print("No open orders found. Proceeding with order submission.")
            request_order_submit = client_trading.submit_order(order_data=request_order_buy)
            qty_num_buy += 1
            # print("Order submitted successfully!")
            # print(request_order_submit)
        else:
            # print("Conflicting open orders exist. Review and cancel them if needed:")
            for order in open_orders:
                print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
    except Exception as e:
        print("An error occurred while submitting the order:", e)

    # Prepare the Sell order
    request_order_sell = MarketOrderRequest(
        symbol=stock_code2,
        qty=quantity_stock2,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )

    try:
        all_orders = client_trading.get_orders()
        # print("Retrieved all orders:", all_orders)

        # Manually filter based on status if needed
        fill_orders = [order for order in all_orders if order.status == "Filled"]
        # print("Filtered filled orders:", fill_orders)
        open_orders = [order for order in all_orders if order.status == "accepted"]
        # print("Filtered opened orders:", open_orders)

        if qty_num_sell < 1:
            print("No open orders found. Proceeding with order submission.")
            request_order_submit = client_trading.submit_order(order_data=request_order_sell)
            qty_num_sell += 1
            print("Order submitted successfully!")
            print(request_order_submit)
        else:
            print("Conflicting open orders exist. Review and cancel them if needed:")
            for order in open_orders:
                print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
    except Exception as e:
        print("An error occurred while submitting the order:", e)


def order_sell_pair(stock_code1, quantity_stock1, stock_code2, quantity_stock2):
    global qty_num_sell
    global qty_num_buy
    # Prepare the SELL order
    request_order_sell = MarketOrderRequest(
        symbol=stock_code1,
        qty=quantity_stock1,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )

    try:
        print('order sell pair')
        all_orders = client_trading.get_orders()
        # print("Retrieved all orders:", all_orders)

        # Manually filter based on status if needed
        # fill_orders = [order for order in all_orders if order.status == "Filled"]
        # print("Filtered filled orders:", fill_orders)
        open_orders = [order for order in all_orders if order.status == "accepted"]
        # print("Filtered opened orders:", open_orders)
        open_orders_or_not = False

        if qty_num_sell < 1:
            print("No open orders found. Proceeding with order submission.")
            request_order_submit = client_trading.submit_order(order_data=request_order_sell)
            qty_num_sell += 1
            print("Order submitted successfully!")
            print(request_order_submit)
        else:
            print("Conflicting open orders exist. Review and cancel them if needed:")
            for order in open_orders:
                print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
    except Exception as e:
        print("An error occurred while submitting the order:", e)

    # Prepare the buy order
    request_order_buy = MarketOrderRequest(
        symbol=stock_code2,
        qty=quantity_stock2,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )

    try:
        all_orders = client_trading.get_orders()
        # print("Retrieved all orders:", all_orders)

        # Manually filter based on status if needed
        fill_orders = [order for order in all_orders if order.status == "Filled"]
        # print("Filtered filled orders:", fill_orders)
        open_orders = [order for order in all_orders if order.status == "accepted"]
        # print("Filtered opened orders:", open_orders)

        if qty_num_buy < 1:
            print("No open orders found. Proceeding with order submission.")
            request_order_submit = client_trading.submit_order(order_data=request_order_buy)
            qty_num_buy =+ 1
            print("Order submitted successfully!")
            print(request_order_submit)
        else:
            print("Conflicting open orders exist. Review and cancel them if needed:")
            for order in open_orders:
                print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
    except Exception as e:
        print("An error occurred while submitting the order:", e)

def order_buy(stock, quantity):
    # Prepare the buy order
    request_order_buy = MarketOrderRequest(
        symbol=stock,
        qty=quantity,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )

    try:
        print('order_buy_pair-3')
        all_orders = client_trading.get_orders()
        # print("Retrieved all orders:", all_orders)

        # Manually filter based on status if needed
        fill_orders = [order for order in all_orders if order.status == "Filled"]
        # print("Filtered filled orders:", fill_orders)
        open_orders = [order for order in all_orders if order.status == "accepted"]
        # print("Filtered opened orders:", open_orders)

        if not open_orders:
            # print("No open orders found. Proceeding with order submission.")
            request_order_submit = client_trading.submit_order(order_data=request_order_buy)
            # print("Order submitted successfully!")
            print(request_order_submit)
        else:
            # print("Conflicting open orders exist. Review and cancel them if needed:")
            for order in open_orders:
                print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
    except Exception as e:
        print("An error occurred while submitting the order:", e)

    return render_template('dashboard.html')

def order_sell(stock, quantity):
    # Prepare the Sell order
    request_order_sell = MarketOrderRequest(
        symbol=stock,
        qty=quantity,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )
    try:
        all_orders = client_trading.get_orders()
        # print("Retrieved all orders:", all_orders)

        # Manually filter based on status if needed
        fill_orders = [order for order in all_orders if order.status == "Filled"]
        # print("Filtered filled orders:", fill_orders)
        open_orders = [order for order in all_orders if order.status == "accepted"]
        # print("Filtered opened orders:", open_orders)

        if not open_orders:
            print("No open orders found. Proceeding with order submission.")
            request_order_submit = client_trading.submit_order(order_data=request_order_sell)
            print("Order submitted successfully!")
            print(request_order_submit)
        else:
            print("Conflicting open orders exist. Review and cancel them if needed:")
            for order in open_orders:
                print(f"Order ID: {order.id}, Symbol: {order.symbol}, Side: {order.side}, Quantity: {order.qty}")
    except Exception as e:
        print("An error occurred while submitting the order:", e)
    return render_template('dashboard.html')

# trading_thread = None
# stop_trading = False
# def order_buy_automatic_thread():
#     # function that runs in a separate thread for automatic trading
#     global stop_trading
#     try:
#         print("Starting automatic trading...")
#         # Extract and validate form data
#         stock1 = request.form.get('stock_code1')
#         stock2 = request.form.get('stock_code2')
#         quantity1 = request.form.get('quantity_stock1')
#         quantity2 = request.form.get('quantity_stock2')
#         window_size = request.form.get('window_size')
#         threshold = request.form.get('threshold')
#
#         # Convert inputs to the required types
#         window_size = int(window_size) if window_size else None
#         threshold = float(threshold) if threshold else None
#         quantity1 = int(quantity1) if quantity1 else None
#         quantity2 = int(quantity2) if quantity2 else None
#
#         print(f"Inputs: stock1: {stock1}, stock2: {stock2}, quantity1: {quantity1}, quantity2: {quantity2}, window_size: {window_size}, threshold: {threshold}")
#
#         # Validate required fields
#         if not all([stock1, stock2, quantity1, quantity2, window_size, threshold]):
#             print('Validate required fields')
#             raise ValueError("Missing or invalid input fields.")
#
#         # Normalize prices and prepare for trading
#         from minimum_distance_strategy import normalize_prices, pairs_trading
#
#         # Check if stock data is available in the session and handle gracefully if not
#         # norm_stock1 = session.get(stock1)
#         # norm_stock2 = session.get(stock2)
#         from minimum_distance_strategy import stock_pairs_info, pairs_list
#         norm_stock1 = stock_pairs_info[pairs_list[0]]
#         norm_stock2 = stock_pairs_info[pairs_list[1]]
#         spread_list = []
#         for i in range(window_size, len(norm_stock1)):
#             spread = norm_stock1.iloc[i] - norm_stock2.iloc[i]
#             spread_list.append(spread)
#             print('spread', spread, 'spread_list[-1]', spread_list[-1])
#
#         if norm_stock1 is None or norm_stock2 is None:
#             print(f"Missing data for stocks: {stock1 if norm_stock1 is None else ''}, {stock2 if norm_stock2 is None else ''}")
#             return "Stock data is missing. Please ensure the session contains the required data."
#
#         # Log the normalized stock data for debugging
#         print(f"Normalized data for {stock1}: {norm_stock1}")
#         print(f"Normalized data for {stock2}: {norm_stock2}")
#
#         if not hasattr(norm_stock1, 'iloc') or not hasattr(norm_stock2, 'iloc'):
#             raise ValueError("Normalized prices are not valid pandas objects.")
#     except ValueError as ve:
#         print(f"Input validation error: {ve}")
#         return "Invalid input. Please check your data."
#     except Exception as e:
#         print(f"Error in setup: {e}")
#         return "An unexpected error occurred during setup."
#
#     # Set session flag
#     session['ture_false'] = True
#     try:
#         print("Starting automatic trading...")
#         while session.get('ture_false', False) and not stop_trading:
#             # Fetch trading signal
#             # signal = pairs_trading(norm_stock1, norm_stock2, window_size, threshold)
#             # print(f"Signal received: {signal} (type: {type(signal)})")
#             #
#             # if signal == 1:  # Buy signal
#             #     print("Executing buy order...")
#             #     order_buy_pair()
#             # elif signal == -1:  # Sell signal
#             #     print("Executing sell order...")
#             #     order_sell_pair()
#             # else:  # Neutral signal
#             #     print("No actionable signal. Waiting...")
#
#             if spread_list[-1] > threshold:
#                 order_sell_pair
#             if spread_list[-1] < threshold:
#                 order_buy_pair
#             # Pause before the next check
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Automatic trading stopped by user.")
#     except Exception as e:
#         print(f"An error occurred during trading: {e}")
#     finally:
#         # Ensure the session flag is reset
#         session['ture_false'] = False
#         print("Trading session has ended.")
#
#     # Redirect to the appropriate page after the trading session ends
#     # return redirect(url_for('minimumdistance.pairs_trading_minimum_distance'))
#
# @order_bp.route('/order_buy_automatic', methods=['GET', 'POST'])
# def order_buy_automatic():
#     # starts the automatic trading in a separate thread
#     global trading_thread, stop_trading
#     stop_trading = False
#     if trading_thread is None or not trading_thread.is_alive():
#         trading_thread = threading.Thread(target=order_buy_automatic_thread)
#         trading_thread.start()
#         message = "Automatic trading started"
#     else:
#         message = "Trading is already running"
#
#     # Redirect to the appropriate page after the trading session ends
#     return redirect(url_for('minimumdistance.pairs_trading_minimum_distance'))

import threading
import time
from flask import Blueprint, request, redirect, url_for, session
from minimum_distance_strategy import stock_pairs_info, pairs_list

order_bp = Blueprint('order', __name__)

# Global control variables
trading_thread = None
stop_trading = threading.Event()  # Thread-safe stop signal

def order_buy_automatic_thread(stock1, quantity1, stock2, quantity2, window_size, threshold):
    from minimum_distance_strategy import stock_pairs_info
    """Background thread for automatic trading."""
    try:
        print(f"Starting automatic trading for {stock1} and {stock2}...")

        # Get stock data
        stock1 = stock1.upper()
        stock2 = stock2.upper()
        norm_stock1 = stock_pairs_info.get(stock1)
        norm_stock2 = stock_pairs_info.get(stock2)
        print('stock1', stock1, 'norm_stock1', norm_stock1, 'stock_pairs_info', stock_pairs_info)

        if norm_stock1 is None or norm_stock2 is None:
            print(f"Error: Missing data for stocks: {stock1}, {stock2}")
            return
        print('----1----')
        spread_list = [
            norm_stock1.iloc[i] - norm_stock2.iloc[i]
            for i in range(window_size, len(norm_stock1))
        ]
        print('----2-----')
        print('spread_list', spread_list, 'spread_list[-1]', spread_list[-1])

        while not stop_trading.is_set():
            if spread_list[-1] > threshold:
                print("Executing SELL order...")
                order_sell_pair(stock1, quantity1, stock2, quantity2)
            elif spread_list[-1] < threshold:
                print("Executing BUY order...")
                order_buy_pair(stock1, quantity1, stock2, quantity2)
            else:
                print("No actionable signal. Waiting...")

            if spread_list[-1] > threshold * 1.2:
                order_stop()
            elif spread_list[-1] < threshold * 0.8:
                order_stop()
            time.sleep(1)  # Avoid CPU overload
    except Exception as e:
        print(f"Error in trading thread: {e}")
    finally:
        print("Trading session has ended.")

@order_bp.route('/order_buy_automatic', methods=['POST'])
def order_buy_automatic():
    """Start automatic trading in a separate thread."""
    global trading_thread

    # Extract form data BEFORE launching the thread
    stock1 = request.form.get('stock_code1')
    stock2 = request.form.get('stock_code2')
    quantity1 = int(request.form.get('quantity_stock1', 1))
    quantity2 = int(request.form.get('quantity_stock2', 1))
    window_size = int(request.form.get('window_size', 10))
    threshold = float(request.form.get('threshold', 1.0))
    print(stock1, quantity1, stock2, quantity2, window_size, threshold)

    try:
        norm_stock1 = stock_pairs_info.get(stock1, None)
        norm_stock2 = stock_pairs_info.get(stock2, None)

        if norm_stock1 is None or norm_stock2 is None:
            raise KeyError("One or both stocks are missing in stock_pairs_info.")

    except KeyError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    if not all([stock1, quantity1, stock2, quantity2, window_size, threshold]):
        return "Missing input values", 400

    # Reset stop flag and start thread
    stop_trading.clear()
    if trading_thread is None or not trading_thread.is_alive():
        trading_thread = threading.Thread(
            target=order_buy_automatic_thread,
            args=(stock1, quantity1, stock2, quantity2, window_size, threshold),
            daemon=True
        )
        trading_thread.start()
        message = "Automatic trading started"
    else:
        message = "Trading is already running"

    return redirect(url_for('minimumdistance.pairs_trading_minimum_distance'))

def order_sell_automatic_thread(stock1, quantity1, stock2, quantity2, window_size, threshold):
    from minimum_distance_strategy import stock_pairs_info
    """Background thread for automatic trading."""
    try:
        print(f"Starting automatic trading for {stock1} and {stock2}...")

        # Get stock data
        stock1 = stock1.upper()
        stock2 = stock2.upper()
        norm_stock1 = stock_pairs_info.get(stock1)
        norm_stock2 = stock_pairs_info.get(stock2)
        print('stock1', stock1, 'norm_stock1', norm_stock1, 'stock_pairs_info', stock_pairs_info)

        if norm_stock1 is None or norm_stock2 is None:
            print(f"Error: Missing data for stocks: {stock1}, {stock2}")
            return
        print('----1----')
        spread_list = [
            norm_stock1.iloc[i] - norm_stock2.iloc[i]
            for i in range(window_size, len(norm_stock1))
        ]
        print('----2-----')
        print('spread_list', spread_list, 'spread_list[-1]', spread_list[-1])

        while not stop_trading.is_set():
            if spread_list[-1] > threshold:
                print("Executing SELL order...")
                order_sell_pair(stock1, quantity1, stock2, quantity2)
            elif spread_list[-1] < threshold:
                print("Executing BUY order...")
                order_buy_pair(stock1, quantity1, stock2, quantity2)
            else:
                print("No actionable signal. Waiting...")

            time.sleep(1)  # Avoid CPU overload
    except Exception as e:
        print(f"Error in trading thread: {e}")
    finally:
        print("Trading session has ended.")

@order_bp.route('/order_sell_automatic', methods=['POST'])
def order_sell_automatic():
    """Start automatic trading in a separate thread."""
    global trading_thread

    # Extract form data BEFORE launching the thread
    stock1 = request.form.get('stock_code1')
    stock2 = request.form.get('stock_code2')
    quantity1 = int(request.form.get('quantity_stock1', 1))
    quantity2 = int(request.form.get('quantity_stock2', 1))
    window_size = int(request.form.get('window_size', 10))
    threshold = float(request.form.get('threshold', 1.0))
    print(stock1, quantity1, stock2, quantity2, window_size, threshold)

    try:
        norm_stock1 = stock_pairs_info.get(stock1, None)
        norm_stock2 = stock_pairs_info.get(stock2, None)

        if norm_stock1 is None or norm_stock2 is None:
            raise KeyError("One or both stocks are missing in stock_pairs_info.")

    except KeyError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    if not all([stock1, quantity1, stock2, quantity2, window_size, threshold]):
        return "Missing input values", 400

    # Reset stop flag and start thread
    stop_trading.clear()
    if trading_thread is None or not trading_thread.is_alive():
        trading_thread = threading.Thread(
            target=order_sell_automatic_thread,
            args=(stock1, quantity1, stock2, quantity2, window_size, threshold),
            daemon=True
        )
        trading_thread.start()
        message = "Automatic trading started"
    else:
        message = "Trading is already running"

    return redirect(url_for('minimumdistance.pairs_trading_minimum_distance'))


@order_bp.route('/order_quit_automatic', methods=['POST'])
def order_quit_automatic():
    # Stop the trading thread
    stop_trading.set()
    session['ture_false'] = False
    return redirect(url_for('minimumdistance.pairs_trading_minimum_distance'))


# @order_bp.route('/order_sell_automatic', methods=['GET', 'POST'])
# def order_sell_automatic():
#     from minimum_distance_strategy import pairs_trading, pairs_info, pairs_list
#     stock1 = pairs_list[0]
#     stock2 = pairs_list[1]
#     window_size = pairs_info[5]
#     threshold = pairs_info[6]
#
#     session['ture_false'] = True
#
#     # Continuously monitor signals
#     try:
#         while session['ture_false']:
#             signal = pairs_trading(stock1, stock2, window_size, threshold)
#             positions = client_trading.get_all_positions()
#             if signal == 1:
#                 if not positions:
#                     order_sell_pair()
#                 else:
#                     print("Position already exists. Skipping buy order.")
#             elif signal == -1:
#                 if not positions:
#                     order_buy_pair()
#                 else:
#                     print("Position already exists. Skipping sell order.")
#             else:
#                 # No action for neutral signal
#                 print("No actionable signal. Waiting...")
#                 pass
#             # Pause for 1 second before re-checking
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Automatic trading stopped.")


@order_bp.route('/order_cancel', methods=['GET', 'POST'])
def order_cancel():
    order_id = request.form.get('order_id')
    print('order_id', order_id)
    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400

    try:
        # Cancel the order using Alpaca-py by order id
        response = client_trading.cancel_order_by_id(order_id)
        # cancel all orders
        # response = client_trading.cancel_orders()
        # return jsonify({"success": f"Order {order_id} canceled successfully."})
        return redirect(url_for('order_management.order_management'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @order_bp.route('/order_stop', methods=['GET', 'POST'])
# def order_stop():
#     print('order_stop')
#     if request.method == 'POST':
#         # obtain position_symbol
#         position_symbol = request.form.get('position_id')
#         # Get the open position for the asset (stock symbol)
#         position = client_trading.get_account().get_position(position_symbol)
#
#         if position:
#             # Get the corresponding position
#             # position = client_trading.get_position(position_id)
#             position = client_trading.get_all_positions(position_id)
#
#             if position:
#                 symbol = position.symbol
#                 qty = position.qty
#
#                 # Select the operation according to the position direction
#                 if qty > 0:  # If long
#                     # Create a sell market order and close a position
#                     market_order = MarketOrderRequest(
#                         symbol=symbol,
#                         qty=qty,
#                         side=OrderSide.SELL,  # sell
#                         time_in_force="gtc"  # permanent validity
#                     )
#                 elif qty < 0:  # if short
#                     # Create buy market order, cover operation
#                     market_order = MarketOrderRequest(
#                         symbol=symbol,
#                         qty=abs(qty),  # The amount to be replaced is the absolute value of a negative number
#                         side=OrderSide.BUY,  # long
#                         time_in_force="gtc"  # permanent validity
#                     )
#                 else:
#                     return render_template('error.html')  # If there is no position, go to the error page
#
#                 # submit order
#                 client_trading.submit_order(market_order)
#
#                 # If the processing succeeds, a success message or redirect is displayed
#                 return redirect(url_for('dashboard.dashboard'))
#             else:
#                 # The position could not be found
#                 return render_template('error.html')
#
#
# @order_bp.route('/order_stop', methods=['POST'])
# def order_stop():
#     position_id = request.form.get('position_id')
#
#     if not position_id:
#         return jsonify({"success": False, "message": "Invalid position ID"})
#
#     try:
#         # 获取所有订单并筛选出 "open" 状态的订单
#         open_orders = client_trading.get_orders()
#         open_orders = [order for order in open_orders if order.status == "open" and order.symbol == position_id]
#
#         # 先取消所有未完成的订单，避免 wash trade
#         if open_orders:
#             for order in open_orders:
#                 client_trading.cancel_order(order.id)
#             time.sleep(2)  # 确保订单被取消
#
#         # 平仓指定持仓
#         close_response = client_trading.close_position(symbol_or_asset_id=position_id)
#
#         if isinstance(close_response, dict) and "id" in close_response:
#             return jsonify({"success": True, "message": f"Closed {position_id}"})
#         else:
#             return jsonify({"success": False, "message": f"Failed to close {position_id}"})
#     except Exception as e:
#         return jsonify({"success": False, "message": f"Error: {str(e)}"})




# @order_bp.route('/order_quit_automatic', methods=['POST'])
# def order_quit_automatic():
#     session['ture_false'] = False
#     # stop the automatic trading thread
#     global stop_trading
#
#     # signal the thread to stop
#     stop_trading = True
#
#     return render_template('pairs_trading_minimum_distance.html')


@order_bp.route('/order_stop', methods=['POST'])
def order_stop():
    print('order_stop')
    msft_orders = client_trading.get_orders()
    print('msft_orders', msft_orders)
    if request.method == 'POST':
        print('post')
        # Obtain position symbol and quantity
        position_symbol = request.form.get('stock_code')
        total_quantity = request.form.get('total_quantity_stock')
        quantity = request.form.get('quantity_stock')
        # trader_id = session.get('trader_id')  # Assuming the trader is logged in
        print('position_symbol', position_symbol, 'total_quantity', total_quantity, 'quantity', quantity)

        if not position_symbol or not quantity:
            print('Invalid input. Please enter a valid quantity')
            flash('Invalid input. Please enter a valid quantity.', 'danger')
            return redirect(url_for('order_management.filled_orders'))
        print('before try')
        try:
            print('after try')
            quantity = int(quantity)
            # position = client_trading.get_account().get_position(position_symbol)
            try:
                print(f"Fetching position for symbol: {position_symbol}")
                position = client_trading.get_open_position(position_symbol)

                if not position:
                    flash("Position not found.", "danger")
                    return redirect(url_for("order_management.filled_orders"))
                # available_qty = int(position.qty) - int(position.held_for_orders)
                # if available_qty <= 0:
                #     flash(f'No available shares to trade. {position.qty} held for orders.', 'danger')
                #     print(f'No available shares to trade. {position.qty} held for orders')
                #     return redirect(url_for('order_management.filled_orders'))

            except Exception as e:
                flash(f"Error fetching position: {str(e)}", "danger")
                print(f'Error fetching position: {str(e)}')
                return redirect(url_for("order_management.filled_orders"))
            print('position', position)

            if not position:
                flash('Position not found.', 'danger')
                print('not position')
                return redirect(url_for('order_management.filled_orders'))

            symbol = position.symbol
            # qty = int(position.qty)
            qty = float(total_quantity)
            print('symbol', symbol, 'quantity')

            if quantity <= 0 or quantity > abs(qty):
                print('quantity <= 0 or quantity > qty:', 'quantity', quantity, 'qty', qty)
                flash('Invalid quantity. Must be greater than 0 and less than available.', 'danger')
                return redirect(url_for('order_management.filled_orders'))

            # Select operation based on position direction
            if qty > 0:  # If long
                print('long')
                market_order = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=OrderSide.SELL,  # Sell
                    time_in_force="gtc"  # Permanent validity
                )
            elif qty < 0:  # If short
                print('short')
                market_order = MarketOrderRequest(
                    symbol=symbol,
                    qty=abs(quantity),
                    side=OrderSide.BUY,  # Cover operation
                    time_in_force="gtc"
                )
            else:
                flash('No valid position to close.', 'danger')
                return redirect(url_for('order_management.filled_orders'))

            # Submit order
            print('Submit order')
            order_submited= client_trading.submit_order(market_order)
            print('Successfully closed')
            flash(f'Successfully closed {quantity} of {symbol}.', 'success')

        except ValueError:
            flash('Invalid quantity input.', 'danger')
        except Exception as e:
            flash(f'Error closing position: {str(e)}', 'danger')
            print(f'Error closing position: {str(e)}')

        msft_orders = client_trading.get_order_by_id(order_submited.id)
        print('msft_orders', msft_orders)

        return redirect(url_for('order_management.filled_orders'))


