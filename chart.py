import alpaca_trade_api as trade_api
import config

def convertWatchlist1():
    stocklist = ['AAPL', 'NVDA', 'AMD', 'IBM', 'AMZN']
    api = trade_api.REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY, config.APCA_API_BASE_URL)
    watchlist = []

    for stock in stocklist:
        data = api.get_asset(stock)
        symbol = data.__getattr__('symbol')
        exchange = data.__getattr__('exchange')
        x = str(exchange + ':' + symbol)
        watchlist.append(x)
    return watchlist

def convertWatchlist():
    stocklist = ['AAPL', 'NVDA', 'AMD', 'IBM', 'AMZN']
    # from stock_pair import get_us_stock_symbols
    # stocklist = get_us_stock_symbols()
    api = trade_api.REST(config.APCA_API_KEY_ID, config.APCA_API_SECRET_KEY, config.APCA_API_BASE_URL)
    watchlist = []

    for stock in stocklist:
        try:
            data = api.get_asset(stock)
            symbol = data.__getattr__('symbol')
            exchange = data.__getattr__('exchange')
            if symbol and exchange:  # Ensure valid data
                watchlist.append(f"{exchange}:{symbol}")
        except Exception as e:
            print(f"Error fetching data for {stock}: {e}")
    return watchlist
