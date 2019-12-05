from smtplib import SMTPException

import flask
from flask import request, jsonify, current_app
from flask_cors import CORS, cross_origin
from flask_mail import Mail, Message
from cryptography.fernet import Fernet

import pymysql, json, sys, jwt, string, secrets

db = pymysql.connect(host="127.0.0.1", user="root", passwd="", db="payroll", port=3306 )
cursor = db.cursor()
app = flask.Flask(__name__)
mail = Mail(app)
app.config["Debug"] = True
app.config["SECRET_KEY"] = "thisissecretkey"
CORS(app, support_credentials=True)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'emailId'
app.config['MAIL_PASSWORD'] = 'password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# key = Fernet.generate_key()                                   # To AutoGenerate Key from Fernet

key = "Zk2TMHAVOWNX7-p8EWuIFmDcDr-Ea3MXNlYp5oq5ZgY="            # Create Personal Key



@app.route('/', methods=['GET'])
def home():
    return "API Running"


def checkmail(email):
    query = "select * from employeereg where emailId=%s"
    try:
        test = cursor.execute(query, email)
        if test == 1:
            return False
        else:
            return True
    except TypeError as e:
        print(e)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))


def mailpass(email):
    if email != '':
        rnum = id_generator()
        password = encpass(rnum)
        query = "update logindata set password=%s where email=%s"
        recordtupple = (password, email)
        test = cursor.execute(query, recordtupple)
        if test:
            try:
                msg = Message('Hello', sender='college.managemement@gmail.com', recipients=[email])
                msg.body = 'Hello ' + email + ', Your Reset Code Is: ' + rnum
                mail.send(msg)
                return True
            except SMTPException as e:
                print(e.message)
                return False
        else:
            return False
    else:
        return False
        # return json.dumps({'success': False, 'Message': 'Fields Not Set'}), 401, {'ContentType': 'application/json'}


def encpass(password):
    if password != "":
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(bytes(password, 'utf-8'))   #required to be bytes
        return cipher_text
    else:
        return "Empty Password"


def decpass(password):
    if password != "":
        cipher_suite = Fernet(key)
        uncipher_text = (cipher_suite.decrypt(bytes(password, 'utf-8')))
        plain_text = bytes(uncipher_text).decode("utf-8")  # convert to string
        return plain_text
    else:
        return "Empty Password"


@app.route('/login', methods=['POST'])
def login():
    try:
        details = request.json
        if details['email'] != '' and details['password'] != '':
            email = details['email']
            pwd = details['password']
            if not checkmail(email):
                query = "select * from logindata where email=%s"
                cursor.execute(query, email)
                result = cursor.fetchall()

                for x in result:
                    empid = (x[1])
                    em = (x[2])
                    pv = (x[4])
                    passwd = ("password", (decpass(x[3])))

                if passwd[1] == pwd:
                    query = "select * from headers where privLevel=%s"
                    cursor.execute(query, pv)
                    result = json.dumps(cursor.fetchall())
                    token = jwt.encode({'email': em}, app.config["SECRET_KEY"], algorithm='HS256')
                    # token=jwt.encode({"user": em[1], "exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=30)}, app.config["SECRET_KEY"], algorithm='HS256')
                    # printval=jwt.decode(token, app.config["SECRET_KEY"], algorithms=['HS256'])
                    # print(printval)
                    return json.dumps({'token': token.decode('UTF-8'), 'success': True, 'message': 'User Login Successful', 'empId': empid, 'email': em, 'headers': result}), 200, {'ContentType': 'application/json'}
                else:
                    return json.dumps({'success': False, 'Message': 'Invalid Credentials'}), 401, {'ContentType': 'application/json'}
            else:
                return json.dumps({'success': False, 'Message': 'Invalid Credentials'}), 401, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False, 'Message': 'All Credentials Not Set'}), 401, {'ContentType': 'application/json'}
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if (str(exc_type.__class__)) == KeyError:
            return json.dumps({'success': False,'Message': 'Failed to upload data due to missing key : ' + str(exc_value)}), 401, {'ContentType': 'application/json'}
        elif (str(exc_type.__class__)) == KeyError:
            return json.dumps({'success': False, 'Message': 'Failed to upload data due to missing key : ' + str(exc_value)}), 401, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


@app.route('/register', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        try:
            details = request.json
            if details['name'] != '' and details['contactNo'] != '' and details['password'] != '' and details['email'] != '':
                name = details['name']
                mblno = details['contactNo']
                pwd = details['password']
                passwd = encpass(pwd)
                email = details['email']
                if checkmail(email):
                    query = "INSERT INTO regdata(name,contactNo,password,email) VALUES (%s, %s, %s, %s)"
                    recordtuple = (name, mblno, passwd, email)
                    insert = cursor.execute(query, recordtuple)
                    print(insert)
                    # db.close()
                    # cursor.close()
                    return json.dumps({'success': True, 'Message': 'User Registered Successfully'}), 200, {'ContentType': 'application/json'}
                else:
                    return json.dumps({'success': False, 'Message': 'Email already Exist'}), 401, {'ContentType': 'application/json'}
            else:
                return json.dumps({'success': False, 'Message': 'All Fields Not Set'}), 401, {'ContentType': 'application/json'}
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if (str(exc_type.__class__)) == KeyError:
                return json.dumps({'success': False, 'Message': 'Failed to upload data due to missing key : ' + str(exc_value)}), 401, {'ContentType': 'application/json'}
            elif (str(exc_type.__class__)) == KeyError:
                return json.dumps({'success': False, 'Message': 'Failed to upload data due to missing key : ' + str(exc_value)}), 401, {'ContentType': 'application/json'}
            else:
                return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
    elif request.method == "GET":
        return json.dumps({'success': True, 'Message': 'GET Method detected'}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False, 'Message': 'Method Not Allowed'}), 405, {'ContentType': 'application/json'}


@app.route('/resetpass', methods=['POST'])
def resetpass():
    if request.json['email'] != '':
        try:
            mailavl = checkmail(request.json['email'])
            if not mailavl:
                if mailpass(request.json['email']):
                    return json.dumps({'success': True, 'Message': 'Password Reset Successfully. Please Check Your Mail'}), 200, {'ContentType': 'application/json'}
                else:
                    return json.dumps({'success': True, 'Message': 'Password Reset Unsuccessful. Try Again'}), 200, {'ContentType': 'application/json'}
            else:
                return json.dumps({'success': False, 'Message': 'Email Not Registered'}), 401, {'ContentType': 'application/json'}
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if (str(exc_type.__class__)) == KeyError:
                return json.dumps({'success': False, 'Message': 'Failed to upload data due to missing key : ' + str(exc_value)}), 401, {'ContentType': 'application/json'}
            elif (str(exc_type.__class__)) == KeyError:
                return json.dumps({'success': False, 'Message': 'Failed to upload data due to missing key : ' + str(exc_value)}), 401, {'ContentType': 'application/json'}
            else:
                return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False, 'Message': 'Enter Email-Id'}), 401, {'ContentType': 'application/json'}


@app.route('/updatepass', methods=['POST'])
def updatepass(email, oldpass, newpass):
    if oldpass != '' and newpass != '' and email != '':
        try:
            query = "select password from regdata where email=%s"
            cursor.execute(query, email)
            result = cursor.fetchall()
            for x in result:
                pw = (decpass(x[0]))
            if pw == oldpass:
                query = "update regdata set password=%s where email=%s"
                recordtupple = (encpass(newpass), email)
                test = cursor.execute(query, recordtupple)
                if test:
                    return json.dumps({'success': True, 'Message': 'Password Updatation Successful'}), 200, {'ContentType': 'application/json'}
                else:
                    return json.dumps({'success': False, 'Message': 'Password Updatation UnSuccessful'}), 401, {'ContentType': 'application/json'}
            else:
                return "Old and New Password not match"
        except:
            return False
    else:
        return json.dumps({'success': False, 'Message': 'All Fields Not Set'}), 401, {'ContentType': 'application/json'}


app.run()
