from alpaca.trading.client import TradingClient
from flask import Blueprint, render_template

# Define the blueprint
account_bp = Blueprint('account', __name__, template_folder='templates')

# Alpaca API credentials
API_KEY = 'PK30X482MH0Y5RX80FPR'
API_SECRET = 'LJif4LRSDC4BLhu3EprXOvzcaSc5Y9dp3W8Afano'

# create trading client
trading_client = TradingClient(API_KEY, API_SECRET)


# get account info
def accountinfo():
    account = trading_client.get_account()
    return account


if __name__ == '__main__':
    print('account info')
    # print("account ID:", account.id)
    # print("status:", account.status)
    # print("equity:", account.equity)
    # print("cash:", account.cash)
    # print("initial margin:", account.initial_margin)
    # print("maintenance margin:", account.maintenance_margin)
