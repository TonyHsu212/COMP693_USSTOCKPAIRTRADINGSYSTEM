from flask import Blueprint, render_template

# Define the blueprint
test_bp = Blueprint('test', __name__, template_folder='templates')


@test_bp.route('/test', methods=['GET'])
def test():
    return render_template('strategy_file.html')
