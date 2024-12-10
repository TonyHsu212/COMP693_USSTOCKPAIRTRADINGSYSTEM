
import bcrypt
import mysql.connector
import connect
from flask import Blueprint, render_template, request, redirect, url_for, session
import globalvaluemanagement

# Define the blueprint
auth_bp = Blueprint('auth', __name__, template_folder='templates')

# ---- define dbconn and connection variables HERE ----
dbconn = None
connection = None
# ---- PUT YOUR database user name HERE ----
dbuser = "root"
# ---- PUT YOUR PASSWORD HERE ----
dbpass = "801221789801"
# ---- PUT YOUR local host HERE ----
dbhost = "localhost"
dbport = "3306"
# ---- PUT YOUR database name HERE ----
dbname = "tradingsystem"


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user="root",\
    password="801221789801", host="localhost", \
    database="tradingsystem", autocommit=True)
    dbconn = connection.cursor()
    return dbconn


def hashing_password(password):
    # Generate the hashed password with a salt
    hashedpassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # print('password hashed:', hashedpassword)
    return hashedpassword


def password_check(hashed_password, user_password):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)


@auth_bp.route('/registerlogin')
def register_login():
    return render_template('registerlogin.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # print('register')
    connection = getCursor()
    if request.method == 'POST':
        user_name = request.form.get('userName')
        # print(user_name)
        pwd = request.form.get('password')
        # print(pwd)
        repwd = request.form.get('password2')
        # print(repwd)
        fname = request.form.get('firstName')
        # print(fname)
        lname = request.form.get('lastName')
        # print(lname)
        userType = request.form.get('userType')
        # print(userType)
        accountState = 'Active'

        connection.execute('select * from User where username = %s', (user_name, ))
        account_username = connection.fetchall()

        # if not user_name.isalnum() and len(user_name) < 8 and not pwd.isalnum() and len(pwd) < 8:
        #     msg = 'the length for user name and password should be more than 8 !'
        #     return render_template('register.html')

        # if not re.match(r'[A-Za-z0-9]+', user_name):
        #     msg = 'Username must contain only characters and numbers!'
        #     return render_template('register.html')

        if not user_name or not pwd or not repwd:
            msg1 = 'Please fill out the form!'
            return render_template('registerlogin.html', msg1=msg1)

        if account_username:
            msg1 = 'this account already exists!'
            return render_template('registerlogin.html', msg1=msg1)

        if pwd == repwd and userType == 'Trader':
            # print('pwd = repwd ')
            hashed_pwd = hashing_password(pwd)
        else:
            msg1 = 'please ensure the two pwd are the same!'
            # print('pwd != repwd ')
            return render_template('registerlogin.html', msg1=msg1)

        # Insert hashed password into the database
        query = "INSERT INTO User (userName, firstName, lastName, userType, pwd, accountState) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (user_name, fname, lname, userType, hashed_pwd.decode('utf-8'), accountState)
        connection.execute(query, values)
        msg1 = 'register successfully, please login!'
        return render_template('registerlogin.html', msg1=msg1)
    else:
        # print('it is get methon: ')
        msg1 = 'register again!'
        return render_template('registerlogin.html', msg1=msg1)


@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    account_state: str = ''
    connection = getCursor()
    # print('login')
    if request.method == 'POST':
        # print('post')
        user_name = request.form.get('username')
        # print(user_name)
        if not user_name:
            msg2 = 'please input your user name !'
            # print(msg)
            return render_template('registerlogin.html', msg2=msg2)
        pwd = request.form.get('password')
        if not pwd:
            msg2 = 'please input your password !'
            # print(msg)
            return render_template('registerlogin.html', msg2=msg2)

        connection.execute('select * from User where username = %s', (user_name, ))
        account_user = connection.fetchone()
        connection.clear_attributes()
        if account_user is not None:
            account_user = list(account_user)
            # print('account_user:', account_user)
            account_state = account_user[6]
            # print('here1')
            if account_user and account_state != 'Active':
                # print('here2')
                if len(account_user) == 13:
                    msg2 = 'please notice your account is inactive!'
                    # print(msg2)
                    return render_template('registerlogin.html', msg2=msg2)
                else:
                    # print('here3')
                    account_state = account_user[14]
        if account_user is not None:
            # print('account_user', account_user[0])
            hashed_password = account_user[5]
        else:
            msg2 = 'Incorrect user name !'
            return render_template('registerlogin.html', msg2=msg2)
        if hashed_password is not None:
            # print('sql successful 2')
            t_true = password_check(hashed_password, pwd)
            if t_true and account_state == 'Active':
                session['loggedin'] = True
                session['id'] = account_user[0]
                session['user_name'] = account_user[1]
                session['role'] = account_user[4]
                # print('role:', account_user[4])
                if session['role'] == 'Trader':
                    # print(session['role'])
                    id = account_user[0]
                    connection.execute('select * from User where UserID = %s', (id, ))
                    account_info = connection.fetchone()
                    # account_info_new = list(account_info)
                    return render_template('dashboard.html', user_name=user_name)
                else:
                    msg2 = 'no account found.'
                    return render_template('registerlogin.html', msg2=msg2)
            elif t_true and account_state == 'Locked':
                msg2 = 'msg1: your account is locked, please contact manager to unlock it!'
                return render_template('registerlogin.html', msg2=msg2)
            elif t_true and account_state != 'Active':
                msg2 = 'your account is not active. please contact manager to active your account!'
                # print('msg inactive2', msg2)
                return render_template('registerlogin.html', msg2=msg2)
            else:
                login_num = globalvaluemanagement.get_value('0')
                msg2 = 'your password is not correct, please input again!'
                login_num = login_num + 1
                globalvaluemanagement.set_value('0', login_num)
                # print('login_num', login_num)
                if login_num > 3:
                    account_user[6] = 'Locked'
                    connection.execute('update User set accountState = %s where userName = %s', ('Locked', user_name, ))
                    login_num = 0
                    msg2 = 'your password has been not correct for three times, your account is locked, waiting for manager to unlock it!'
                    return render_template('registerlogin.html', msg2=msg2)
                return render_template('registerlogin.html', msg2=msg2)
        else:
            msg2 = 'please input your password!'
            return render_template('registerlogin.html', msg2=msg2)
        msg2 = 'no account found.'
    return render_template('registerlogin.html', msg2=msg2)


@auth_bp.route('/to_logout', methods=['POST', 'GET'])
def logout():
    # print('session:', session['user_name'])
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('user_name', None)
    return render_template('home.html')

