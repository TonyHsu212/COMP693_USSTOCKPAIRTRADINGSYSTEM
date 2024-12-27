from flask import Blueprint, render_template

from account_management import getCursor

pair_bp = Blueprint('pair', __name__, template_folder='templates')


@pair_bp.route('/stock_pairs')
def stock_pairs():
    stock_pairs_data = []
    # Connect to the database
    conn = getCursor()
    connection = conn[0]
    try:
        # with connection.cursor() as cursor:
        # Execute the SQL query
        sql_query = "SELECT Symbol_1, Symbol_2, Correlation, p_value FROM stock_analysis"
        connection.execute(sql_query)

        # Fetch all rows
        stock_pairs_data = connection.fetchall()
        print('stock_pairs_data', stock_pairs_data)
    finally:
        connection.close()
    return render_template('pairs_trading.html', stock_pairs=stock_pairs_data)
