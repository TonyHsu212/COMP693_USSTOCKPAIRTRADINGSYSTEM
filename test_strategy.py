from flask import Blueprint, render_template

# Define the blueprint
test_bp = Blueprint('test_strategy', __name__, template_folder='templates')


@test_bp.route('/test_strategy', methods=['GET'])
def test_strategy():
    return render_template('strategy_file.html')
