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


@order_management_pb.route('/order_management')
def order_management():
    # Define the request parameters (optional)
    # Fetch all orders (other options: OPEN, CLOSED)
    orders_request = GetOrdersRequest()

    # Fetch all orders
    orders = trading_client.get_orders(filter=orders_request)

    # Display orders
    for order in orders:
        formatted_datetime = time_transform(order)
        order.created_at = formatted_datetime
        print(f"Order ID: {order.id}")
        print(f"Symbol: {order.symbol}")
        print(f"Quantity: {order.qty}")
        print(f"Side: {order.side}")
        print(f"Status: {order.status}")
        print(f"Created At: {formatted_datetime}")
        print(f"---")

    return render_template('order_management.html', orders=orders)


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
