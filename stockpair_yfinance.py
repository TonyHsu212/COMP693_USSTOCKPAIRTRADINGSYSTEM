from flask import Flask, request, jsonify, Blueprint, render_template, redirect, url_for, get_flashed_messages
import yfinance as yf
from scipy.stats import pearsonr
from flask import flash

# Define the blueprint
pairanalyze_bp = Blueprint('pairanalyze', __name__, template_folder='templates')


@pairanalyze_bp.route('/analyze_stock_pair', methods=['POST'])
def analyze_stock_pair():
    print('---analyze_stock_pair---')
    if request.method == 'POST':
        try:
            # Get parameters from the form (POST data)
            stock1 = request.form.get('stock1')
            stock1 = stock1.upper()  # Capitalize the stock symbol to uppercase
            stock2 = request.form.get('stock2')
            stock2 = stock2.upper()  # Capitalize the stock symbol to uppercase
            period = request.form.get('period')  # Retrieve the period from the form
            interval = request.form.get('interval')  # Retrieve the interval from the form

             # Debugging: Print the data to ensure it's correctly received
            print(f"Stock1: {stock1}, Stock2: {stock2}, Period: {period}, Interval: {interval}")

            if not stock1 or not stock2 or not period or not interval:
                return jsonify({"error": "All parameters (stock1, stock2, period, interval) are required."}), 400

            # Fetch stock data using yfinance
            data1 = yf.download(stock1, period=period, interval=interval)
            print('data1', data1)
            data2 = yf.download(stock2, period=period, interval=interval)
            print('data2', data2)

            if data1.empty or data2.empty:
                return jsonify({"error": "Unable to fetch stock data. Check stock symbols or parameters."}), 400

            # Align both datasets by date
            combined_data = data1[['Close']].join(data2[['Close']], lsuffix=f'_{stock1}', rsuffix=f'_{stock2}', how='inner')
            # print('combined_data', combined_data)
            print("Columns of combined_data:", combined_data.columns.tolist())
            # Ensure the columns are correctly renamed (single-level column names)
            combined_data.columns = [f'Close_{stock1}', f'Close_{stock2}']
            print('Updated combined_data columns:', combined_data.columns.tolist())
            combined_data.dropna(inplace=True)

            # Calculate correlation and p-value
            corr, p_value = pearsonr(combined_data[f'Close_{stock1}'], combined_data[f'Close_{stock2}'])
            print('corr:', corr,  'p_value:', p_value)
            corr, p_value = round(float(corr), 3), round(float(p_value), 3)
            print('corr:', corr,  'p_value:', p_value)

            # Calculate spread
            spread = combined_data[f'Close_{stock1}'] - combined_data[f'Close_{stock2}']
            print('spread', spread)

            # Prepare data for frontend
            result = {
                "correlation": corr,
                "pValue": p_value,
                "dates": combined_data.index.strftime('%Y-%m-%d').tolist(),
                "spread": spread.tolist(),
            }
            # After processing the result

            flash(result)
            # return redirect(url_for('pairanalyze.analyze_pair_page'))
            return render_template('stock_pair.html', result=result)

        except Exception as e:
            return jsonify({"error": str(e)}), 500


@pairanalyze_bp.route('/analyze_pair_page')
def analyze_pair_page():
    # Get the flashed messages
    result = get_flashed_messages()
    print('')
    if not result:
        return render_template('stock_pair.html', result=result)
    else:
        return render_template('stock_pair.html')

