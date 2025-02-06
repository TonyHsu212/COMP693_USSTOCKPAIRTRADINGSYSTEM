from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderStatus
from flask import Blueprint, render_template
from datetime import datetime

order_management_pb = Blueprint('order_management', __name__, template_folder='templates')


# Replace with your Alpaca API credentials
API_KEY = 'PK30X482MH0Y5RX80FPR'
API_SECRET = 'LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano'

# Initialize the trading client
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)  # Use paper=True for paper trading


# @order_management_pb.route('/accepted_orders')
# def accepted_orders():
#     # Define the request parameters (optional)
#     # Fetch all orders (other options: OPEN, CLOSED)
#     orders_request = GetOrdersRequest()
#
#     # Fetch all orders
#     orders = trading_client.get_orders(filter=orders_request)
#
#     # Display orders
#     for order in orders:
#         formatted_datetime = time_transform(order)
#         order.created_at = formatted_datetime
#         print(f"Order ID: {order.id}")
#         print(f"Symbol: {order.symbol}")
#         print(f"Quantity: {order.qty}")
#         print(f"Side: {order.side}")
#         print(f"Status: {order.status}")
#         print(f"Created At: {formatted_datetime}")
#         print(f"---")
#
#     return render_template('accepted_orders.html', orders=orders)


@order_management_pb.route('/accepted_orders')
def accepted_orders():
    # Fetch all orders
    orders_request = GetOrdersRequest()
    orders = trading_client.get_orders(filter=orders_request)

    # if there is on orders
    if not orders:
        print("No orders fetched.")
        return render_template('accepted_orders.html', orders=[])

    # Format datetime for all orders
    for order in orders:
        order.created_at = time_transform(order)

    # Filter only accepted orders
    accepted_orders = [order for order in orders if order.status == OrderStatus.ACCEPTED]
    print('accepted_orders', accepted_orders)

    # Render the appropriate template
    if accepted_orders:
        return render_template('accepted_orders.html', orders=accepted_orders)
    else:
        return render_template('error.html')


@order_management_pb.route('/filled_orders')
def filled_orders():
    # obtain all position
    positions = trading_client.get_all_positions()
    i = 0
    positions_dict = {}

    # print all position info
    # for position in positions:
        # print(f"Symbol: {position.symbol}")
        # print(f"Quantity: {position.qty}")
        # print(f"Current price: {position.current_price}")
        # print(f"Market value: {position.market_value}")
        # print(f"Cost basis: {position.cost_basis}")
        # print(f"Unrealized P&L: {position.unrealized_pl}")
        # print("-----------", positions)

    # Render the appropriate template
    if positions:
        return render_template('filled_orders.html', orders=positions)
    else:
        return render_template('error.html')


@order_management_pb.route('/closed_orders')
def closed_orders():
    # obtain all orders (FILLED)
    orders_request = GetOrdersRequest(status="closed")
    orders = trading_client.get_orders(filter=orders_request)
    print('closed_orders', orders)

    # obtain order
    # open_positions = trading_client.get_all_positions()
    # open_symbols = {position.symbol for position in open_positions}

    # selected 'filled and closed order'
    # closed_orders = [
    #     order for order in orders
    #     if order.status == OrderStatus.FILLED and order.symbol not in open_symbols
    # ]

    # Apply time transformation after filtering
    print('--1--')
    for order in orders:
        order.created_at = time_transform(order)
    print('--2--')
    # render
    if orders:
        return render_template('historical_orders.html', orders=orders)
    else:
        return render_template('error.html', message="there is no closed order。")

def time_transform(order):
    # timezone-aware datetime string
    datetime_str = order.created_at

    # Parse the string into a datetime object
    datetime_str = str(datetime_str)
    dt = datetime.fromisoformat(datetime_str)

    # Remove the timezone information
    dt_naive = dt.replace(tzinfo=None)

    # Format the datetime object to the desired string format
    formatted_datetime = dt_naive.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_datetime


@order_management_pb.route('/other_orders', methods=['GET'])
def other_orders():
    from alpaca.trading.enums import OrderStatus
    try:
        # Fetch all orders
        orders = trading_client.get_orders()

        # Filter orders that are NOT accepted or filled
        other_orders = [order for order in orders if order.status not in {OrderStatus.ACCEPTED, OrderStatus.FILLED}]

        print("Other orders:", other_orders)
        return render_template('other_orders.html', orders=other_orders)
    except:
        return render_template('error.html', message="there is no closed order。")


