import os

from flask import Flask, render_template
import mysql.connector
from flask_hashing import Hashing

import connect
import globalvaluemanagement
from accountManagement import auth_bp

app = Flask(__name__)

dbconn = None
connection = None
app.secret_key = os.urandom(24)
UploadDir = '/static/images/'
login_num = 0
globalvaluemanagement._init()
globalvaluemanagement.set_value('0', 0)

# Register the auth blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')


@app.route("/")
def dashboard():
    return render_template("home.html")


# @app.route("/")
# def dashboard():
#     return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(port=7000)

