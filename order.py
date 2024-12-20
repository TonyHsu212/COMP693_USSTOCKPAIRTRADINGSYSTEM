# import requests
# import alpaca_trade_api as trade_api
# import config

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
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from flask import Blueprint, request, render_template

APCA_API_KEY_ID = 'PK30X482MH0Y5RX80FPR'
APCA_API_SECRET_KEY = 'LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano'

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.enums import OrderStatus


# Authenticate the client
client_trading = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)

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
    print("Retrieved all orders:", all_orders)

    # Manually filter based on status if needed
    fill_orders = [order for order in all_orders if order.status == "Filled"]
    print("Filtered filled orders:", fill_orders)
    open_orders = [order for order in all_orders if order.status == "accepted"]
    print("Filtered opened orders:", open_orders)

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
client_trading.cancel_order_by_id(order_id="d9983490-9f7f-48f6-937b-b3d74ec0d877")
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
@order_bp.route('/order_buy', methods=['GET', 'POST'])
def order_buy_pair():
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
        print(f"Action: {action}")

        # Prepare the buy order
        request_order_buy = MarketOrderRequest(
            symbol=stock_code1,
            qty=quantity_stock1,
            side=OrderSide.Buy,
            time_in_force=TimeInForce.GTC
        )

        try:
            all_orders = client_trading.get_orders()
            print("Retrieved all orders:", all_orders)

            # Manually filter based on status if needed
            fill_orders = [order for order in all_orders if order.status == "Filled"]
            print("Filtered filled orders:", fill_orders)
            open_orders = [order for order in all_orders if order.status == "accepted"]
            print("Filtered opened orders:", open_orders)

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


        # Prepare the Sell order
        request_order_sell = MarketOrderRequest(
            symbol=stock_code2,
            qty=quantity_stock2,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        try:
            all_orders = client_trading.get_orders()
            print("Retrieved all orders:", all_orders)

            # Manually filter based on status if needed
            fill_orders = [order for order in all_orders if order.status == "Filled"]
            print("Filtered filled orders:", fill_orders)
            open_orders = [order for order in all_orders if order.status == "accepted"]
            print("Filtered opened orders:", open_orders)

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
        print(f"Action: {action}")

        # Prepare the SELL order
        request_order_sell = MarketOrderRequest(
            symbol=stock_code1,
            qty=quantity_stock1,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )

        try:
            all_orders = client_trading.get_orders()
            print("Retrieved all orders:", all_orders)

            # Manually filter based on status if needed
            fill_orders = [order for order in all_orders if order.status == "Filled"]
            print("Filtered filled orders:", fill_orders)
            open_orders = [order for order in all_orders if order.status == "accepted"]
            print("Filtered opened orders:", open_orders)

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
            all_orders = client_trading.get_orders()
            print("Retrieved all orders:", all_orders)

            # Manually filter based on status if needed
            fill_orders = [order for order in all_orders if order.status == "Filled"]
            print("Filtered filled orders:", fill_orders)
            open_orders = [order for order in all_orders if order.status == "accepted"]
            print("Filtered opened orders:", open_orders)

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
