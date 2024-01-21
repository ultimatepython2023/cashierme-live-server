from flask import Flask, render_template,current_app ,redirect, flash, url_for, request, session, make_response,abort,Response, make_response, send_file,jsonify
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy,get_debug_queries
from sqlalchemy import and_, or_
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask_login import login_user, login_required, LoginManager, UserMixin, logout_user, current_user
import os
import pdfkit
import random
import datetime
import requests, json
from flask_babel import Babel, gettext, lazy_gettext
from datetime import datetime,timedelta
from flask_recaptcha import ReCaptcha
from logging import WARNING, FileHandler
import qrcode
from io import BytesIO
import base64
import hexa2base64
import hexaConvertFunction
from binascii import unhexlify
from flask_apscheduler import APScheduler
import time
from functools import wraps
from flask_jwt import JWT
import jwt
import logging
from threading import Thread
from sqlalchemy.pool import NullPool
from sqlalchemy import func
import SECURE_KEYS
import verify_email
import urllib
from urllib.request import urlopen
import json
import requset_api
from decimal import *
import razorpay
from ultimate_saas_functions.payment_3d_turkish import payment_3d_turkish_request
from ultimate_saas_functions.generate_qr_code import generate_normal_qr_code
from ultimate_saas_functions.revpay_hash512 import get_hashing
from flask_socketio import SocketIO, send
from sqlalchemy.orm import backref, relationship
from sqlalchemy import Column, Integer, ForeignKey
import verify_auth_api
from flask_cors import CORS, cross_origin
import check_account_status


#>>>>>>>> add logging and transactions  system in log file <<<<<<<<<<<<<<<<<<<<<

# from flask_compress import Compress
class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Africa/Cairo'


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + SECURE_KEYS.DB_USER + ':' + SECURE_KEYS.DB_PASSWORD + '@' + SECURE_KEYS.DB_HOST + '/' + SECURE_KEYS.DB_NAME
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SECRET_KEY'] = SECURE_KEYS.SESSION_KEY
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['BABEL_DEFAULT_LOCALE'] = SECURE_KEYS.DEFAULT_LANGUAGE

socket = SocketIO(app)

app.config.update(dict(
    RECAPTCHA_ENABLED = True,
    RECAPTCHA_SITE_KEY =SECURE_KEYS.RECAPTCHA_KEY ,
    RECAPTCHA_SECRET_KEY = SECURE_KEYS.RECAPTCHA_SECRET
))

paytabs_request_url = SECURE_KEYS.REQ_URL
url_query = SECURE_KEYS.URLQUERY
merchant_saudi_id = SECURE_KEYS.MERCHANT_ID
saudi_currancy = SECURE_KEYS.CURRENCY
paytabs_saudi_api_key = SECURE_KEYS.API_KEY_AUTH


#>>>>>>>>>>>>> error handler   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>
file_handler = FileHandler('errors_log.txt')
file_handler.setLevel(WARNING)
app.logger.addHandler(file_handler)
#>>>>>>>>>>>>>>>>>>  end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#>>>>>>>>>>>>>>>>>>>>>>>>>  objects <<<<<<<<<<<<<<<<<<<<<<<
db = SQLAlchemy(app)
migrate = Migrate(app,db)
mysql = MySQL(app)
mail = Mail(app)
babel = Babel(app)
recaptcha = ReCaptcha(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
engine_container = db.get_engine(app)
CORS(app)

# Compress(app)

def cleanup(session):
    """
    This method cleans up the session object and also closes the connection pool using the dispose method.
    """
    session.close()
    engine_container.dispose()



global COOKIE_TIME_OUT
COOKIE_TIME_OUT = 15000*10000



@socket.on('message')
def check_reg_code(msg):
    '''web socket io functiom'''
    try:
        check_account = Subscription.query.filter_by(business_name = msg).first()
        if check_account:
            send('success')
        else:
            send('pending')
    except Exception as Error:
        ssend('error')



#<<<<<<<<<<<<<<<<<<<<<<<<<<<< custom function token <<<<<<<<<<<<<<<<<<<<
def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.get.args('token')
        if not token:
            return jsonify({'message':'error message'}),403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message':'error message'}),403
        return fun(*args, **kwargs)
    return wrapped



def check_coutry(func):
    """Check if user is logged in."""
    @wraps(func)
    def decorator(*args, **kwargs):
        if 'country_code' not in session:
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorator

def smtp_config(mail_config, smtp=1):
    if smtp not in {1,2}:
        pass
    if smtp == 2:
        MAIL_SERVER = mail_config["MAIL_SERVER"][0]
        MAIL_PORT = mail_config["MAIL_PORT"][0]
        MAIL_USERNAME = mail_config["MAIL_USERNAME"][1]
        MAIL_PASSWORD = mail_config["MAIL_PASSWORD"][1]
    else:
        MAIL_SERVER = mail_config["MAIL_SERVER"][0]
        MAIL_PORT = mail_config["MAIL_PORT"][0]
        MAIL_USERNAME = mail_config["MAIL_USERNAME"][0]
        MAIL_PASSWORD = mail_config["MAIL_PASSWORD"][0]
    return [MAIL_USERNAME, MAIL_PASSWORD, MAIL_SERVER, MAIL_PORT]



def jsonify_or_raw(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        raw = False
        if "raw" in kwargs:
            raw = kwargs["raw"]
            del kwargs["raw"]
        result = func(*args, **kwargs)
        return jsonify(result) if not raw else result
    return wrapper
#<<<<<<<<<<<<<<<<<<<<<<< end <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


class Subscription(db.Model, UserMixin):
    id = db.Column(db.Integer , primary_key=True)
    subscription = relationship("Sessions", backref="Subscription")
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    stores_number = db.Column(db.String(255))
    business_name = db.Column(db.String(255),unique=True,nullable=False)
    company_string_name= db.Column(db.String(255))
    best_time_call = db.Column(db.String(255))
    city = db.Column(db.String(255))
    contact = db.Column(db.String(255))
    #>>>>>>>>>>> start logging fields  <<<<<<
    user_id =  db.Column(db.String(120))
    user_name = db.Column(db.String(120))
    last_update_user = db.Column(db.String(50))
    last_update_date = db.Column(db.DateTime)
    db_create_date = db.Column(db.DateTime)
    created_from = db.Column(db.String(50))
    #>>>>>>>>>>>>>  end <<<<<<<<<<<<<<<<<<<<<
    password = db.Column(db.String(255))
    tax_file = db.Column(db.String(255))
    commercial_register = db.Column(db.String(255))
    check_email_time = db.Column(db.DateTime)
    expire_db = db.Column(db.DateTime)
    order_id = db.Column(db.Integer)
    Country = db.Column(db.String(255))
    subscription_type = db.Column(db.String(20))
    payment_status = db.Column(db.String(20))
    street = db.Column(db.String(255))
    postcode = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    random_code = db.Column(db.String(255))
    company_token = db.Column(db.String(255),unique=True)
    plan_type = db.Column(db.String(255))
    price = db.Column(db.String(255))
    subscription_status = db.Column(db.String(255))
    db_status = db.Column(db.String(100))
    country_code_id = db.Column(db.String(100))
    payment_getway = db.Column(db.String(100))
    account_type = db.Column(db.String(100))
    notes = db.Column(db.String(1500))
    is_active = db.Column(db.Boolean(), default=1)
    test = db.Column(db.String(100))
    delete_account_at = db.Column(db.DateTime)




    def __init__(self, name,email ,stores_number, business_name,
                 best_time_call, city, contact, db_create_date,
                 password,tax_file,commercial_register,expire_db,
                 check_email_time,Country,subscription_type,
                 street,postcode,password_hash,company_string_name,created_from,company_token,db_status,notes,country_code_id,account_type):
        self.name = name
        self.email = email
        self.stores_number = stores_number
        self.business_name  = business_name
        self.best_time_call = best_time_call
        self.city = city
        self.contact = contact
        self.db_create_date = db_create_date
        self.password = password
        self.tax_file = tax_file
        self.commercial_register = commercial_register
        self.expire_db = expire_db
        self.check_email_time = check_email_time
        self.Country = Country
        self.subscription_type = subscription_type
        self.street = street
        self.postcode = postcode
        self.password_hash = password_hash
        self.company_string_name = company_string_name
        self.created_from = created_from
        self.company_token = company_token
        self.db_status = db_status
        self.notes = notes
        self.country_code_id = country_code_id
        self.account_type = account_type



class Order(db.Model, UserMixin):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    stores_number = db.Column(db.String(255))
    business_name = db.Column(db.String(255))
    company_string_name= db.Column(db.String(255))
    best_time_call = db.Column(db.String(255))
    street = db.Column(db.String(255))
    Country = db.Column(db.String(255))
    postcode = db.Column(db.String(255))
    contact = db.Column(db.String(255))
    password = db.Column(db.String(255))
    tax_file = db.Column(db.String(255))
    commercial_register = db.Column(db.String(255))
    subscription_id = db.Column(db.String(255))
    order_date = db.Column(db.DateTime)
    status_order = db.Column(db.String(255))
    order_code = db.Column(db.String(255))
    order_id = db.Column(db.Integer)
    tans_ref = db.Column(db.String(255))
    amount = db.Column(db.String(255))
    customer_token = db.Column(db.String(255))
    city = db.Column(db.String(255))
    sub_type = db.Column(db.String(255))
    expire_db = db.Column(db.DateTime)
    auto_payment_status = db.Column(db.String(20))
    password_hash = db.Column(db.String(255))
    qr_code_base64 = db.Column(db.String(500))
    random_code = db.Column(db.String(255))
    package_id = db.Column(db.String(255))
    sub_type_toUpdate = db.Column(db.String(50))
    pos_no_toUpdate = db.Column(db.String(31))
    price_toUpdate = db.Column(db.String(31))
    country_code_id = db.Column(db.String(100))
    country_code_id_test = db.Column(db.String(100))
    payment_getway = db.Column(db.String(100))
    razorpay_payment_id = db.Column(db.String(200))
    razorpay_order_id = db.Column(db.String(200))
    razorpay_signature = db.Column(db.String(200))
    account_type = db.Column(db.String(100))
    turkish_hash_number = db.Column(db.String(200))
    tran_ref_to_update = db.Column(db.String(255))
    tran_ref_old = db.Column(db.String(255))
    cs_token_old = db.Column(db.String(255))

    # company_token = db.Column(db.String(255))

    def __init__(self, name,email ,stores_number, business_name, city, contact,password,tax_file,commercial_register,order_date,street,Country,postcode,status_order,order_code,amount,sub_type,expire_db,password_hash, package_id,company_string_name):
                self.name = name
                self.email = email
                self.stores_number = stores_number
                self.business_name = business_name
                self.city = city
                self.contact = contact
                self.password = password
                self.tax_file = tax_file
                self.commercial_register = commercial_register
                self.order_date = order_date
                self.street = street
                self.Country = Country
                self.postcode = postcode
                self.status_order = status_order
                self.order_code = order_code
                self.amount = amount
                self.sub_type = sub_type
                self.expire_db = expire_db
                self.password_hash = password_hash
                self.package_id = package_id
                self.company_string_name = company_string_name

class Packages(db.Model, UserMixin):
    id = db.Column(db.Integer , primary_key=True)
    price = db.Column(db.String(255))
    pos_no_code = db.Column(db.String(255))
    pos_no = db.Column(db.Integer())
    pos_string_en = db.Column(db.String(255))
    pos_string_ar = db.Column(db.String(255))
    type = db.Column(db.String(255))
    currency_en = db.Column(db.String(255))
    currency_ar = db.Column(db.String(255))
    code_hash = db.Column(db.String(255))
    country_code = db.Column(db.String(255))

    def __init__(self,price,pos_no_code,pos_string_en,pos_string_ar,type,currency_en,currency_ar,code_hash,pos_no ,country_code):
        self.price = price
        self.pos_no_code = pos_no_code
        self.pos_string_en = pos_string_en
        self.pos_string_ar = pos_string_ar
        self.type = type
        self.currency_en = currency_en
        self.currency_ar = currency_ar
        self.code_hash = code_hash
        self.pos_no = pos_no
        self.country_code = country_code

class TemporaryTokens(db.Model, UserMixin):
    id = db.Column(db.Integer , primary_key=True)
    email = db.Column(db.String(255))
    subscription_id = db.Column(db.String(255))
    token = db.Column(db.String(255))
    active_code = db.Column(db.String(255))
    expiration = db.Column(db.DateTime)
    status = db.Column(db.String(255))

    def __init__(self,email,subscription_id,token,active_code,expiration,status):
        self.email = email
        self.subscription_id = subscription_id
        self.token = token
        self.active_code = active_code
        self.expiration = expiration
        self.status = status



class Logs(db.Model, UserMixin):

    id = db.Column(db.Integer , primary_key=True)
    function_name = db.Column(db.String(255))
    msg_type = db.Column(db.String(255))
    message = db.Column(db.Text)
    source = db.Column(db.String(255))
    create_datetime = db.Column(db.DateTime)
    user_id = db.Column(db.DateTime)
    test = db.Column(db.Text)

    def __init__(self,function_name,msg_type,message,source,create_datetime):
        self.function_name = function_name
        self.msg_type = msg_type
        self.message = message
        self.source = source
        self.create_datetime = create_datetime


class Countries(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer , primary_key=True)
    country_code = db.Column(db.String(50))
    country_name = db.Column(db.String(50))
    language = db.Column(db.String(50))
    default_language = db.Column(db.String(50))
    currency = db.Column(db.String(50))
    monthly_amount = db.Column(db.String(50))
    annually_amount = db.Column(db.String(50))
    payment_name = db.Column(db.String(200))
    payment_merchant_id = db.Column(db.String(50))
    payment_currency = db.Column(db.String(50))
    payment_request_api_url = db.Column(db.String(200))
    payment_api_key = db.Column(db.String(200))
    payment_query_link = db.Column(db.String(200))
    google_script = db.Column (db.String(500))
    payment_getway = db.Column(db.String(200))
    usd_convert = db.Column(db.String(50))
    payment_with_usd = db.Column(db.Boolean)
    global_currency_name = db.Column(db.String(50))
    arabic_currency = db.Column(db.String(50))
    free_trail_days = db.Column(db.String(50))
    turkish_merchant_id = db.Column(db.String(200))
    turkish_merchant_key = db.Column(db.String(200))
    country_code_2d = db.Column(db.String(50))


    def __init__(self,country_code,country_code_2d,country_name,language,default_language,
                 currency,monthly_amount,annually_amount,payment_name,
                 payment_merchant_id,payment_currency,payment_request_api_url,
                 payment_api_key, payment_query_link):
        self.country_code = country_code
        self.country_code_2d = country_code_2d
        self.country_name = country_name
        self.language = language
        self.default_language = default_language
        self.currency = currency
        self.monthly_amount = monthly_amount
        self.annually_amount = annually_amount
        self.payment_name = payment_name
        self.payment_merchant_id = payment_merchant_id
        self.payment_currency = payment_currency
        self.payment_request_api_url = payment_request_api_url
        self.payment_api_key = payment_api_key
        self.payment_query_link = payment_query_link



class Sessions(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,ForeignKey('users.id'))
    subscription_id = db.Column(db.Integer,ForeignKey('subscription.id'))
    user_name = db.Column(db.String(100))
    access_token = db.Column(db.String(1000))
    session_token = db.Column(db.String(1000))
    created_date = db.Column(db.DateTime, default=db.func.now())
    update_date = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    language = db.Column(db.String(120))
    account_type = db.Column(db.String(120))


    def __init__(self,user_id,subscription_id,user_name,access_token,session_token,last_login,account_type):
        self.user_id = user_id
        self.subscription_id = subscription_id
        self.user_name = user_name
        self.access_token = access_token
        self.session_token = session_token
        self.last_login = last_login
        self.account_type = account_type

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Users = relationship("Sessions", backref="Users")
    user_name = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default=db.func.now())
    update_date = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    activate = db.Column(db.Boolean)
    permission = db.Column(db.String(20))
    language = db.Column(db.String(120))
    is_saudi = db.Column(db.Boolean)
    is_turkey = db.Column(db.Boolean)
    is_india = db.Column(db.Boolean)
    is_malaysia = db.Column(db.Boolean)
    is_global = db.Column(db.Boolean)
    is_egypt = db.Column(db.Boolean)
    is_georgia = db.Column(db.Boolean)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    mobile = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    job_grade = db.Column(db.String(255))
    country = db.Column(db.String(255))
    address = db.Column(db.String(255))
    forgot_password_code = db.Column(db.String(255))
    auth_code = db.Column(db.String(255))
    payment_cash = db.Column(db.Boolean)


    def __init__(self,user_name,email,password,country, address,mobile,gender,job_grade, activate):
        self.user_name = user_name
        self.email = email
        self.password = password
        self.country = country
        self.address = address
        self.mobile = mobile
        self.gender = gender
        self.job_grade = job_grade
        self.activate = activate

#>>>>>>>>>>>>>>>>>>>>>>>>>>>  start logging functions   <<<<<<<<<<<<<<<<<<<<<<<<<
############################## add logging events in file and databases  #######
def get_logger_function(fun_name,msg_type, msg, source):
    logger = logging.getLogger(fun_name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('logs.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    if msg_type == 'error':
        logger.error(msg+'---------source--------:'+source)
        save_logger_db(fun_name,msg_type, msg, source)
    elif msg_type == 'info':
        logger.info(msg+'---------source--------:'+source)
        save_logger_db(fun_name,msg_type, msg, source)
    else:
        pass

############################  created in database logging #################
def save_logger_db(fun_name,msg_type, msg, source):
    try:
        datetime_now = datetime.now()
        add_log_data = Logs(fun_name, msg_type,msg, source,datetime_now)
        db.session.add(add_log_data)
        db.session.commit()
    except:
        pass

# ########################  get and check api ###########################
@app.route('/AddLoggingApi', methods=['POST'])
def add_logging_api():
    applications = ['Portal','Portal CP','APP','APP API','APP CP']
    get_api = request.json
    function_name = get_api['fun_name']
    msg_type = get_api['msg_type']
    message = get_api['msg']
    app_code = get_api['source']
    if function_name and msg_type and message and app_code:
        if app_code in applications:
            get_logger_function(function_name,msg_type, message, app_code)
            return jsonify({'info':'created successfully'})
        else:
            return jsonify({'error':'invalid application code'})
    else:
        return jsonify({'error':'null fields'})


############################ scheduler delete record in log file ###############
@scheduler.task('interval', id='created_function',seconds=84400)
def read_log_file():
    with open(r"logs.log" , 'r+') as fp:
        lines = fp.readlines()
        for number in lines:
            getdate = number[0:10]
            datetime_object = datetime.strptime(getdate,"%Y-%m-%d") + timedelta(days=6)
            convert_to_datetime = datetime_object.strftime("%Y-%m-%d")
            datetime_object_converted = datetime.strptime(convert_to_datetime,"%Y-%m-%d")
            if datetime_object_converted < datetime.now():
                data_list = number
                print(number)
                new_file = open("logs.log" , "w")
                data = [dat for dat in lines if dat != data_list]
                for line in data:
                    new_file.write(line)
                new_file.close()

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> end logging functions <<<<<<<<<<<<<<<<<<<<<<
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

############################start   add css to html email ##############
def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)
app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>    end   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@login_manager.user_loader
def UsersLogin(user_id):
    return Subscription.query.get(user_id)

#>>>>>>>>>>>>>>>>>>>>>>>>>>> start  language <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
@babel.localeselector
def get_babel():
    if "language" in session:
        lang = session['language']
        return lang


@app.route('/create_countries', methods=['POST', 'GET'])
def create_countries():
    data = [{"country_code": "EGY",
             "country_name":"Egypt",
             "language": "ar",
            "default_language": "ar",
            "currency": "EGP",
            "monthly_amount": "30",
            "annually_amount": "30",
            "payment_name": "Egyptian_payment",
            "payment_merchant_id": "85475",
            "payment_currency": "EGP",
            "payment_request_api_url": "https://secure-egypt.paytabs.com/payment/request",
            "payment_api_key": "SLJNBJZRTJ-J2NGGRMDTL-KLKNR2KZB6",
            "payment_query_link": "https://secure.paytabs.sa/payment/query"},

            {"country_code":"SAU",
             "country_name":"Saudi arabia",
             "language": "ar",
            "default_language": "ar",
            "currency": "SAR",
            "monthly_amount": "30",
            "annually_amount": "30",
            "payment_name": "Egyptian_payment",
            "payment_merchant_id": "85475",
            "payment_currency": "EGP",
            "payment_request_api_url": "https://secure-egypt.paytabs.com/payment/request",
            "payment_api_key": "SLJNBJZRTJ-J2NGGRMDTL-KLKNR2KZB6",
            "payment_query_link": "https://secure.paytabs.sa/payment/query"},

            {"country_code":"TUR",
             "country_name":"Turkish",
             "language": "tr",
            "default_language": "tr",
            "currency": "TRY",
            "monthly_amount": "138",
            "annually_amount": "1382",
            "payment_name": "Egyptian_payment",
            "payment_merchant_id": "99073",
            "payment_currency": "AED",
            "payment_request_api_url": "https://secure-global.paytabs.com/payment/request",
            "payment_api_key": "STJNGD9KGL-JD9M9MB6JB-WHND9JRDBK",
            "payment_query_link": "https://secure.paytabs.sa/payment/query"
            },

            {"country_code":"MYS",
             "country_name":"Malysia",
             "language": "en",
            "default_language": "en",
            "currency": "MYR",
            "monthly_amount": "35",
            "annually_amount": "353",
            "payment_name": "Egyptian_payment",
            "payment_merchant_id": "99071",
            "payment_currency": "AED",
            "payment_request_api_url": "https://secure-global.paytabs.com/payment/request",
            "payment_api_key": "SRJNGD92TB-JD9M9GTH99-6HL66DDMWR",
            "payment_query_link": "https://secure-global.paytabs.com/payment/query"
            },
            {"country_code":"IND",
             "country_name":"India",
             "language": "en",
            "default_language": "en",
            "currency": "INR",
            "monthly_amount": "623",
            "annually_amount": "6238",
            "payment_name": "Egyptian_payment",
            "payment_merchant_id": "99072",
            "payment_currency": "INR",
            "payment_request_api_url": "https://secure-global.paytabs.com/payment/request",
            "payment_api_key": "S2JNGD9BRB-JD9M9KLZR6-LJMJ9GNTHK",
            "payment_query_link": "https://secure-global.paytabs.com/payment/query "
            }

            ]
    for res in data:
        add_data = Countries(res["country_code"],res['country_name'],res["language"],res["default_language"]
                             ,res["currency"],res["monthly_amount"],
                            res["annually_amount"],res["payment_name"],res["payment_merchant_id"],
                            res["payment_currency"],res["payment_request_api_url"],res["payment_api_key"],res["payment_query_link"] )
        db.session.add(add_data)
        db.session.commit()
    return "success"

@app.route("/english/<string:custom_url>")
def language_en(custom_url):
    language = 'en'
    session['language'] = language
    session['second_lang'] = language
    return redirect('/'+custom_url)

@app.route("/arabic/<string:custom_url>")
def language_ar(custom_url):
    language = 'ar'
    session['language'] = language
    session['second_lang'] = language
    return redirect ('/' + custom_url)

@app.route("/Turkish/<string:custom_url>")
def language_tr(custom_url):
    language = 'tr'
    session['language'] = language
    session['second_lang'] = language
    return redirect ('/' + custom_url)

@app.route("/gorgia/<string:custom_url>")
def language_geo(custom_url):
    language = 'gl'
    session['language'] = language
    session['second_lang'] = language
    return redirect ('/' + custom_url)

@app.route('/get_countries_price',methods=['POST', 'GET'])
def get_countries_price():
    try:
        data = request.json
        # saudi_code = data["saudi"]
        # turky_code = data["turkish"]
        # india_code = data["india"]
        # malysia_code = data["malaysia"]
        # global_code = data["global"]
        all_data = []
        get_contries_price = Countries.query.all()
        for data in get_contries_price:
            code = data.country_code
            monthly_price = data.monthly_amount
            annually_price = data.annually_amount
            google_script = data.google_script
            all_data.append({"code":code, "m_price":monthly_price, "a_price": annually_price, "google_script":google_script})
        return {"data": all_data}
    except Exception as Error:
        print(Error)
        return {"data": all_data}


@app.route('/changePosAmountOfCountry', methods=['POST', 'GET'])
def changePosAmountOfCountry():
    try:
        data = request.json
        country_code = data['country_code']
        monthly_price = data['monthly_price']
        annually_price = data['annually_price']
        googleScript = data['googleScript']
        country_tab = Countries.query.filter_by(country_code = country_code).first()
        if country_tab and monthly_price != "" and annually_price != "":
            if country_tab.monthly_amount != monthly_price or  country_tab.annually_amount != annually_price:
                country_tab.monthly_amount = str(monthly_price)
                country_tab.annually_amount = str(annually_price)
                country_tab.google_script = str(googleScript)
                db.session.commit()
                get_package_id = Packages.query.filter_by(country_code = country_code).all()
                for ress in get_package_id:
                    pos_count = ress.pos_no
                    pos_type = ress.type
                    if pos_type == "Monthly":
                        ress.price = str(int(monthly_price) * int(pos_count))
                        db.session.commit()
                    if pos_type == "yearly":
                        annually_price_to_add = int(int(annually_price) * 12)
                        ress.price = str(int(annually_price_to_add) * int(pos_count ))
                        db.session.commit()
                return {"status": "Done"}
            else:
                country_tab.monthly_amount = str (monthly_price)
                country_tab.annually_amount = str (annually_price)
                country_tab.google_script = str(googleScript)
                db.session.commit ()
                return {"status": "Done"}
        else:
            return {"status": "Failed"}
    except Exception as Error:
        print(Error)
        return {"status": "Failed"}

@app.route("/get_ajax_lang")
def get_ajax_lang():
    if "language" in session:
        lang = session['language']
        return lang
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  end language  <<<<<<<<<<<<<<<<<<<<<<<<<<
#home page
def get_country_code_function(data):
    try:
        check_ip_list = [int(x) for x in data.split('.')]
        octet_a = check_ip_list[0]
        octet_b = check_ip_list[1]
        octet_c = check_ip_list[2]
        octet_d = check_ip_list[3]
        calculation_range = octet_a*(256*256*256)+octet_b*(256*256)+octet_c*256+octet_d
        import mysql.connector
        rec = mysql.connector.connect(user=SECURE_KEYS.DB_USER, password=SECURE_KEYS.DB_PASSWORD, host='localhost', database=SECURE_KEYS.COUNTRY_DB)
        if rec:
            connect_db = rec.cursor()
            connect_db.execute("SELECT countrySHORT FROM country_ip.ipcountry where "+ str(calculation_range) +" between ipFROM and ipTO  ")
            all_data = connect_db.fetchall()
            connect_db.close()
            return str(all_data[0][0])
        rec.close()
    except Exception as Error:
        return "Error"
        pass

@app.route('/home')
@app.route('/')
def index():
    try:
        country_session = ""
        if session.get("country_code") == None:
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ call database ^^^^^^^^^^^^^^^^^^^^^^^^^^")
            ip_address = request.remote_addr
            #ip_address = SECURE_KEYS.COUNTRY_MANUAL_SELECT_IP
            get_country_code = get_country_code_function(ip_address)
            print(get_country_code)
            if get_country_code == "SA":
                country_session = "SAU"
            elif get_country_code == "IN":
                country_session = "IND"
            elif get_country_code == "MY":
                country_session = "MYS"
            elif get_country_code == "TR":
                country_session = "TUR"
            # elif get_country_code == "GE":
            #     country_session = "GEO"
            elif get_country_code == "EG":
                country_session = "EGY"
            elif get_country_code == "Error":
                return redirect('/error')
            else:
                country_session = "GLB"
        else:
            country_session = session['country_code']
        session['country_code'] =  country_session
        get_google_script = Countries.query.filter_by(
            country_code=session['country_code']).first()
        default_lang = get_google_script.default_language
        languages = get_google_script.language
        languages_list = json.loads(languages)
        session['language']= default_lang
        if session['language'] in languages_list:
            try:
                session['language'] = session['second_lang']
            except:
                session["language"] = default_lang
        else:
            session["language"] = default_lang
        print(type(languages_list))
        google_script_id = get_google_script.google_script.find("id=")
        final_get_google_script = get_google_script.google_script[google_script_id:google_script_id+17]
        final_script = final_get_google_script.replace('"', '').replace("id=", '').replace(">", '')
        print(session['country_code'])
        return render_template('index.html',google_script=final_script,active_page="home")
    except Exception as Error:
        print(Error)
        return redirect('/error')




@app.route('/error')
def error():
    return render_template("errorPage.html")


#convert TRY To USd confirm_upgrade_posNo_subscription_monthly
@scheduler.task('interval', id='change_currency',seconds=84400)
def CheckCurrencyApi():
    try:
        get_country=Countries.query.all()
        for recs in get_country:
            payload={}
            response=requests.request("GET", "https://api.apilayer.com/currency_data/convert?to=USD&from=" + recs.global_currency_name +"&amount=1", headers=SECURE_KEYS.CURRENCY_API_KEY, data=payload)
            result=json.loads(response.content)
            response_status = result['success']
            response_value = result['result']
            print(result['result'], result['success'])
            if response_status == True:
                recs.usd_convert = response_value
                db.session.commit()
                get_logger_function('/CheckCurrencyApi','Info',"your USD currency has been upgraded Successfully at >>"+str(datetime.now()),'cashier me site')
                print("upgraded Successfully")
        print("end upgraded")
    except Exception as Error:
        get_logger_function('/CheckCurrencyApi', 'Error',
                            "Cannot access api to change currency please check api or code and countries table >>"+str(
                                Error), 'cashier me site')
        print(Error)
        pass

#subscription page
@app.route('/subscriptions')
@check_coutry
def subscriptions():  # put application's code here
    return render_template('subscriptions.html', active_page='subscriptions')


def tusers_created_database(id,name, fullname, passsword, db_name, email):
    import mysql.connector
    rec = mysql.connector.connect(user=SECURE_KEYS.DB_USER, password=SECURE_KEYS.DB_PASSWORD, host='localhost', database=db_name)
    if rec:
        connect_db = rec.cursor()
        connect_db.execute("INSERT INTO  users (U_ID ,U_L_NAME,U_F_NAME,Password,EMAIL,U_TYP)"
                           " VALUES (%s,%s,%s,%s, %s, %s)"
                           ,(id,name,fullname, passsword, email, 1))
        rec.commit()
        connect_db.close()
    rec.close()
    get_logger_function('/tusers_created_database','info', 'success add data in table users in database>>>>'+db_name,'cashier me site')



@app.route("/sendEmailCustom")
def sendEmailCustom():
    sendSubscriptionEmail("sameer mostaf", "test_12352222", "1", "Admin*99*99",
                          "18-3-1992", "Demo",
                          "samerfathey2002@gmail.com")
    return "ok"

def sendSubscriptionEmail(customer_name ,business_name,user_no,password,expiration_date,sub_type,email, country):
    no_days = ""
    try:
        if sub_type == "Demo":
            no_days = "60"
        elif sub_type == "Enterprise" and payment_methods == "Monthly":
            no_days = "30"
        elif sub_type == "Enterprise" and payment_methods == "yearly":
            no_days = "365"
        with app.test_request_context():
            if country == "TUR":
                smtp = 2
            else:
                smtp = 1
            select_mail_config = smtp_config(SECURE_KEYS.MAIL_CONFIG, smtp=smtp)
            app.config.update(dict(
                MAIL_SERVER=select_mail_config[2],
                MAIL_PORT=select_mail_config[3],
                MAIL_USERNAME=select_mail_config[0],
                MAIL_PASSWORD=select_mail_config[1],
            ))
            mail.init_app(app)
            msg = Message (recipients=[email], sender=select_mail_config[0],subject="Registration Details")
            db_link = SECURE_KEYS.DASHBOARD_URL + business_name
            msg.html = render_template('successDemoEmail2.html',
                                       customer_name=customer_name,
                                       business_name=business_name,
                                       user_no=user_no,
                                       password=password,
                                       db_link=db_link,
                                       no_days=no_days,
                                       expiration_date=str(expiration_date),country= country)

            mail.send(msg)
        get_logger_function ('/sendSubscriptionEmail', 'Info','Success send Email for >>>'+str(customer_name), 'cashier me site')
    except Exception as Error :
        print(Error)
        get_logger_function ('/sendSubscriptionEmail', 'Error','error for send subscription its error' + str(Error), 'cashier me site')
        pass

@app.route('/checkDbUpdated/<string:user_id>', methods=['POST'])
def checkDbUpdated(user_id):
    try:
        check_status = Subscription.query.filter_by(id=current_user.id).first()
        status = check_status.db_status
        get_device = request.headers.get('User-Agent')
        if "Android" in str(get_device):
            get_device_type = "Android"
        elif "Windows" in str(get_device):
            get_device_type = "Windows"
        else:
            get_device_type = "Ios"
        if status == "pending":
            return {"status":"Errors",
                    }
        elif status == "Activated":
            return {"status":"success",
                    "password" : str(check_status.password),
                    "reg_code" : str(check_status.business_name),
                    "device_type" : str(get_device_type)
                    }
    except Exception as Error:
        pass


#create db function
@scheduler.task('interval', id='generate_database_scheduler',seconds=100)
def createDatabaseScheduler():
    try:
        records = Subscription.query.filter_by (db_status="pending").limit(10)
        for rec in records:
            db_name = rec.business_name
            send_api_request = requset_api.createDabaseFromRequestApi(db_name,rec.password,rec.company_string_name,
                                                                      rec.company_token,rec.Country,
                                                                      rec.city,rec.street, rec.postcode,
                                                                      rec.commercial_register,rec.tax_file,
                                                                      rec.contact,rec.email,rec.name,rec.stores_number)
            rec.db_status = send_api_request['status']
            db.session.commit( )
            try:
                change_admin_status(rec.business_name,send_api_request['status'],send_api_request['message'])
            except Exception as Error:
                get_logger_function ('/createDatabaseScheduler', 'error', 'upgrade status error' + str(Error),'cashier me site')
                continue
            get_logger_function ('/createDatabaseScheduler', 'info', 'the request>>>>' + str(send_api_request['request'])+str(send_api_request['message']),'cashier me site')
            cleanup(db.session)
            if send_api_request['status'] == "Activated":
                with app.test_request_context():
                     sendSubscriptionEmail(rec.name, rec.business_name,"1", rec.password,rec.expire_db,rec.subscription_type,rec.email,rec.country_code_id)
    except Exception as Error:
        print(Error)
        get_logger_function ('/createDatabaseScheduler', 'error', 'createDatabaseScheduler >>>>' + str(Error),'cashier me site')
        return "Error"




def change_admin_status(db_name, status, message):
    import mysql.connector
    try:
        conMysql = mysql.connector.connect(user=SECURE_KEYS.DB_USER,
                                           password=SECURE_KEYS.DB_PASSWORD,
                                           host='localhost',
                                           database=SECURE_KEYS.CONTROLLER_DB_NAME)
        connect = conMysql.cursor( )
        connect.execute("UPDATE  subscriptions set  db_status='"+str(status)+"', alert_message='"+str(message)+"'where db_name='"+str(
            db_name)+"'")
        conMysql.commit( )
        connect.close()
        conMysql.close()
    except Exception as Error :
        print(Error)
        pass


@app.route('/firstCsLogin/<string:email>')
def firstCsLogin(email):
    return render_template('login.html', email = email)

#feature page

#feature page
# @app.route('/features')
# @check_coutry
# def features():
#     return render_template('features.html',active_page="features")
#>>>>>>>>>>>>>>>>>>>  end <<<<<<<<<<<<<<<<<<<<<<<

#pricing page
#pricing page
@app.route('/pricing')
@check_coutry
def pricing():
    try:
        get_price= Countries.query.filter_by(country_code = session['country_code']).first()
        # print(get_debug_queries())
        return render_template ('pricing.html', monthly_price=get_price.monthly_amount,
                                annually_price=get_price.annually_amount,active_page="pricing")

    except Exception as Error:
        pass
#>>>>>>>>>>>>>>>>>>> end <<<<<<<<<<<<<<<<<<<<<<<

#contact page
@app.route('/contact')
@check_coutry
def contact():
    return render_template('contact.html', active_page="contact")
#>>>>>>>>>>>>>>>> end <<<<<<<<<<<<<<<<<<<<<<<<<
#

@app.route('/send_email/<string:name>/<string:email>/<string:subject>/<string:message>', methods=['POST'])
def send_email(name,email,subject,message):
    try:
        msg = Message(subject, recipients=[email])
        msg.body = 'Name :' + name +  '\n'+ 'Message :' + message
        mail.send(msg)
        get_logger_function('/send_mail','info','send email from '+email+'-content-'+subject+'---has ben completed successfully send' ,'cashier me site')
        return "ok"
    except:
        get_logger_function('/send_mail','error' ,'error send message from--'+email+'--content--'+subject,'cashier me site')
        return "failed"

#>>>>>>>>>>>>>>>>>>>  <<<<<<<<<<<<<<<<<<<<<<<
#About page
@app.route('/help')
@check_coutry
def about():
    return render_template('help.html', active_page="help")

#thanks page
@app.route('/url')
def url():
    return render_template('url.html')

#send data to email if email already Exists
@app.route('/check_email')
@check_coutry
def check_email_data():
    return render_template('email_back.html',active_page='check_email')

#submit  data to email if email already Exists
@app.route('/submit_check_email', methods=['POST'])
@check_coutry
def submit_check_email():
    if recaptcha.verify():
        email = request.form['email']
        data = Subscription.query.filter_by(email = email).first()
        if data:
            time_now = datetime.now()
            old_time = data.check_email_time
            calculation_time = time_now - old_time
            end_calculation = calculation_time.total_seconds()
            if end_calculation <= 299.9:
                flash("You can,t Send Email Now please Wait ", "warning")
                ok_send = 'ok_send'
                return render_template('email_back.html',ok=ok_send)
            else:
                try:
                    msg = Message(recipients=[email])
                    msg.body = gettext('User No :') + '1' +  '\n' + gettext('password :') + data.password + '\n' + gettext('Registration Code For Application:') + '\n' + data.business_name + '\n' + gettext('Application Expire in:') + data.expire_db.strftime("%b %d %Y") +'\n' + SECURE_KEYS.DASHBOARD_URL + data.business_name
                    mail.send(msg)
                    print("ok send")
                    get_logger_function('/submit_check_email','info', "Successsend email",'cashier me site')
                except Exception as error:
                    get_logger_function('/submit_check_email','error', error,'cashier me site')
                    pass
                data.check_email_time = datetime.now()
                db.session.commit()
                cleanup(db.session)
                flash("Send Email Has ben Successful You can Send Another Email in ","success")
                ok_send = 'ok_send'
                return render_template('email_back.html',ok=ok_send)
        else:
            flash("Email Not Exists Please Wait  ","error")
            ok_send = 'ok_send'
            return render_template('email_back.html',ok=ok_send)
    else:
        return redirect('/check_email')
#>>>>>>>>>>>>>>>>>>>  <<<<<<<<<<<<<<<<<<<<<<<
################################ enterprise payment getway code#########################
#enterprise payment page
@app.route('/enterprise_order_page/<string:subtype>')
@check_coutry
def enterprise_order_url(subtype, ):
    check_data = Packages.query.filter(and_(Packages.type == subtype,Packages.country_code == session['country_code'])).first()
    if check_data:
        print("ok",check_data)
        return render_template('enterprise_subscription.html', subtype=subtype)
    else:
        return redirect('/pricing')

@app.route('/enterprise_order_page/login/<string:subtype>')
@check_coutry
def enterprise_order_url_forCurrent_user(subtype, ):
    check_data = Packages.query.filter(and_(Packages.type == subtype, Packages.country_code == session['country_code'])).first()
    if check_data:
        print("ok",check_data)
        return render_template('upgrade_to_enterprise_subscription.html' , subtype=subtype)
    else:
        return redirect('/pricing')


#submit billing and payment
@app.route('/biling_submit', methods=['POST'])
@check_coutry
def biling_submit():
    if recaptcha.verify():
        email = request.form['email']
        check_email_verify = verify_email.check (email)
        if check_email_verify == "Success":
            sub_type = request.form['subtype']
            pos_num = request.form['pos_num']
            get_data =  Packages.query.filter(and_(Packages.type == sub_type, Packages.pos_no_code == pos_num,Packages.country_code==session['country_code'])).first()
            if get_data:
                name = request.form['name']
                check_email = Subscription.query.filter_by(email = email).first()
                if check_email:
                    try:
                        get_logger_function('/biling_submit','info', email + 'Email Already Exists!!','cashier me site')
                        return redirect('/')
                    except:
                        get_logger_function('/biling_submit', 'error','error for submit check email alraedy Exists this line code is 369','cashier me site')
                        return redirect('/')
                else:
                    from datetime import timedelta
                    business_name = request.form['business_name']
                    company_string_name = request.form['business_name_string']
                    city = request.form['city']
                    contact = request.form['phone']
                    password = request.form['password']
                    tax_file = request.form['tax_number']
                    commercial_register = request.form['commercial_register']
                    street = request.form['street']
                    postcode = request.form['postcode']
                    country= request.form['country']
                    password_bcrypt = bcrypt.generate_password_hash(password).decode("utf-8")
                    expire_db = datetime.now()+ timedelta(31)
                    date_order = datetime.now()
                    random_code1 = random.randint(1, 100000)
                    random_code2 = random.randint(1, 100000)
                    order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
                    status_order = "In-Progress"
                    amounts = get_data.price
                    package_id = get_data.id
                    stores_number = get_data.pos_no_code
                    try:
                        data = Order(name, email, stores_number, business_name, city, contact ,password, tax_file, commercial_register, date_order,street,country,postcode,status_order,order_code,amounts,sub_type,expire_db,password_bcrypt,package_id,company_string_name)
                        db.session.add(data)
                        db.session.commit()
                        data.country_code_id = session['country_code']
                        db.session.commit()
                        get_logger_function('/biling_submit', 'info','created record in order has ben created successfully--->name:'+name+'--company:'+business_name+'--->code line: 569','cashier me site')
                        db.session.flush()
                        get_id = data.id
                        get_payment_data = Countries.query.filter_by(country_code = data.country_code_id).first()
                        if get_payment_data.payment_getway == "paytabs":
                            if get_payment_data.country_code == "TUR" and get_payment_data.payment_with_usd == True:
                                calculation_payment_amount = float(amounts) * float(get_payment_data.usd_convert)
                                payment_amount = Decimal(float(calculation_payment_amount)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
                            else:
                                payment_amount = amounts
                            try:
                                create_json={'profile_id':str(
                                    get_payment_data.payment_merchant_id),
                                    'tran_type':str('sale'),
                                    'tran_class':str('ecom'),
                                    "tokenise":"2",
                                    'cart_description':str(
                                        str(data.id)+str(
                                            sub_type)+'_'+str(
                                            pos_num)+'_'+str(
                                            amounts)),
                                    'cart_id':str(order_code),
                                    'cart_currency':str(
                                        get_payment_data.payment_currency),
                                    'cart_amount':float(payment_amount),
                                    'callback':str(
                                        SECURE_KEYS.CALL_BACK_URL + '/get_transaction'),
                                    'return':str(
                                        SECURE_KEYS.CALL_BACK_URL + '/get_transaction'),
                                    "hide_shipping":True,
                                    'customer_details':{
                                        'name':str(name),
                                        'email':str(email),
                                        'city':str(city),
                                        'phone':str(contact),
                                        'street1':str(street),
                                        'country':"SA",
                                        'state':"Makkah"
                                    }}
                                response = requests.post(str(get_payment_data.payment_request_api_url), data = json.dumps(create_json), headers = {'authorization':str(get_payment_data.payment_api_key) ,'content-type':'https://cashierme.com/json'})
                                print(response.content)
                                datas = json.loads(response.content)
                                print(datas.get('redirect_url'))
                                get_url_response = datas.get('redirect_url')
                                transaction_ref = datas.get('tran_ref')
                                all_data = str(datas)
                                session['transaction_code'] = transaction_ref
                                update_tab = Order.query.filter_by(id = get_id).first()
                                update_tab.order_id = get_id
                                update_tab.tans_ref = transaction_ref
                                db.session.commit()
                                cleanup(db.session)
                                get_logger_function('/biling_submit','info','connect to payment getway success and request api get :--->'+ all_data ,'cashier me site')
                                return redirect(get_url_response)
                            except Exception as error:
                                print(error)
                                db.session.delete(get_id)
                                db.session.commit()
                                get_logger_function('/biling_submit','error', 'Cannot connect to payment getway please check api request and url and response.content and check order table -->code line:606','cashier me site')
                                flash('Cannot process this request  now please try again letter.')
                                cleanup(db.session)
                                return redirect('/pricing')
                        elif get_payment_data.payment_getway == "razorpay":
                            import razorpay
                            amount = int(amounts)*100
                            client = razorpay.Client(
                                auth=(SECURE_KEYS.RAZORPAY_ID,
                                      SECURE_KEYS.RAZORPAY_SECRET))
                            razorpay_data = {"amount" :amount, "currency" :"INR",
                                    "receipt" :"order_rcptid_11"}
                            payment = client.order.create(data=razorpay_data)
                            data.payment_getway = "razorpay"
                            data.razorpay_order_id = payment['id']
                            db.session.commit( )
                            print(payment)
                            return render_template('payment.html',payment=payment,customer_name=name,payment_type="ES")
                        elif get_payment_data.payment_getway == "revpay":
                            merchant_id = get_payment_data.payment_merchant_id
                            m_key = get_payment_data.payment_api_key
                            random_revpay_ref = random.randint(1,100000000000)
                            ref_number = str('RF'+str(random_revpay_ref))
                            data.tans_ref = ref_number
                            data.payment_getway = "revpay"
                            db.session.commit()
                            amount = amounts
                            signature = get_hashing(merchant_id,m_key,ref_number,amount)
                            print(signature['hash'])
                            return render_template('revpay_loader.html', merchant_id = merchant_id,ref_number = ref_number,amount = amount,signature=signature['hash'])
                    except Exception as error:
                        print(error)
                        get_logger_function('/biling_submit','error', 'check connect ta database-->order table and check request api-----> code line: 610,565'+str(error),'cashier me site')
                        flash('Cannot process this request  now please try again letter.')
                        return redirect('/pricing')
                    # return render_template('enterprise_subscription.html')
            else:
                return redirect('/pricing')
        else:
            return redirect ('/pricing')
    else:
        return redirect('/pricing')


#submit billing and payment
@app.route('/upgrade_demo_to_enterprise_subscription', methods=['POST'])
@check_coutry
def upgrade_demo_to_enterprise_subscription():
    from datetime import timedelta
    print("okasdad")
    sub_type = request.form['subtype']
    pos_num = request.form['pos_num']
    get_data =  Packages.query.filter(and_(Packages.type == sub_type, Packages.pos_no_code == pos_num,Packages.country_code == session['country_code'])).first()
    if get_data:
        print("ok check package")
        name = request.form['name']
        company_string_name = request.form['business_name_string']
        city = request.form['city']
        contact = request.form['phone']
        password = request.form['password']
        tax_file = request.form['tax_number']
        commercial_register = request.form['commercial_register']
        street = request.form['street']
        postcode = request.form['postcode']
        country= request.form['country']
        password_bcrypt = bcrypt.generate_password_hash(password).decode("utf-8")
        expire_db = datetime.now()+ timedelta(31)
        date_order = datetime.now()
        random_code1 = random.randint(1, 100000)
        random_code2 = random.randint(1, 100000)
        order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
        status_order = "In-Progress"
        amounts = get_data.price
        package_id = get_data.id
        stores_number = get_data.pos_no_code
        print(name)
        try:
            print("ok check try")
            data = Order(name, current_user.email, stores_number, current_user.business_name, city, contact ,password, tax_file, commercial_register, date_order,street,country,postcode,status_order,order_code,amounts,sub_type,expire_db,password_bcrypt,package_id,company_string_name)
            db.session.add(data)
            db.session.commit()
            print("ok add ordr")
            data.country_code_id = current_user.country_code_id
            db.session.commit()
            get_logger_function('/upgrade_demo_to_enterprise_subscription', 'info','created record in order has ben created successfully--->name:'+name+'--company:'+current_user.business_name,'cashier me site')
            db.session.flush()
            get_id = data.id
            get_payment_data = Countries.query.filter_by(country_code = current_user.country_code_id).first()
            if get_payment_data.payment_getway == "paytabs":
                if get_payment_data.country_code == "TUR" and get_payment_data.payment_with_usd == True:
                    calculation_payment_amount=float(amounts) * float(
                        get_payment_data.usd_convert)
                    payment_amount=Decimal(float(calculation_payment_amount)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
                else:
                    payment_amount=amounts
                try:
                    create_json={
                        'profile_id':str(get_payment_data.payment_merchant_id),
                        'tran_type':str('sale'),
                        'tran_class':str('ecom'),
                        "tokenise":"2",
                        'cart_description':str(str(data.id)+str(sub_type)+'_'+str(pos_num)+'_'+str(amounts)),
                        'cart_id':str(order_code),
                        'cart_currency':str(get_payment_data.payment_currency),
                        'cart_amount':float(payment_amount),
                        'callback':str(SECURE_KEYS.CALL_BACK_URL + '/getResponseForUpgrade_subscription'),
                        'return':str(SECURE_KEYS.CALL_BACK_URL + '/getResponseForUpgrade_subscription'),
                        "hide_shipping":True,
                        'customer_details':{
                            'name':str(name),
                            'email':str(current_user.email),
                            'city':str(city),
                            'phone':str(contact),
                            'street1':str(street),
                            'country':"SA",
                            'state':"Makkah"
                        }}
                    response = requests.post(str(get_payment_data.payment_request_api_url), data = json.dumps(create_json), headers = {'authorization': str(get_payment_data.payment_api_key),'content-type':'https://cashierme.com/json'})
                    print(response.content)
                    datas = json.loads(response.content)
                    print(datas.get('redirect_url'))
                    get_url_response = datas.get('redirect_url')
                    transaction_ref = datas.get('tran_ref')
                    all_data = str(datas)
                    session['transaction_code'] = transaction_ref
                    update_tab = Order.query.filter_by(id = get_id).first()
                    update_tab.order_id = get_id
                    update_tab.tans_ref = transaction_ref
                    db.session.commit()
                    get_logger_function('/upgrade_demo_to_enterprise_subscription','info','connect to payment getway success and request api get :--->'+ all_data ,'cashier me site')
                    return redirect(get_url_response),cleanup(db.session)
                except Exception as error:
                    print(error)
                    get_logger_function('/upgrade_demo_to_enterprise_subscription','error', 'Cannot connect to payment getway please check api request and url and response.content and check order table -->code line:606','cashier me site')
                    flash('Cannot process this request  now please try again letter.')
                    return redirect('/pricing'),cleanup(db.session)
            elif get_payment_data.payment_getway == "razorpay":
                import razorpay
                amount = int(amounts) * 100
                client = razorpay.Client(
                    auth=(SECURE_KEYS.RAZORPAY_ID,
                          SECURE_KEYS.RAZORPAY_SECRET))
                razorpay_data = {"amount" :amount, "currency" :"INR",
                                 "receipt" :"order_rcptid_11"}
                payment = client.order.create(data=razorpay_data)
                data.payment_getway = "razorpay"
                data.razorpay_order_id = payment['id']
                db.session.commit( )
                print(payment)
                return render_template('payment.html', payment=payment, customer_name=name, payment_type="UTE")
            elif get_payment_data.payment_getway == "revpay":
                merchant_id = get_payment_data.payment_merchant_id
                m_key = get_payment_data.payment_api_key
                random_revpay_ref = random.randint(1,100000000000)
                ref_number = str('RF'+str(random_revpay_ref))
                data.tans_ref = ref_number
                data.payment_getway = "revpay"
                db.session.commit()
                amount = amounts
                signature = get_hashing(merchant_id,m_key,ref_number,amount)
                print(signature['hash'])
                return render_template('revpay_loader.html', merchant_id = merchant_id,ref_number = ref_number,amount = amount,signature=signature['hash'])
                # create_enterprise_subscription(data.id)
            return redirect('/')
        except Exception as error:
            print(error)
            get_logger_function('/upgrade_demo_to_enterprise_subscription','error', str(error),'cashier me site')
            flash('Cannot process this request  now please try again letter.')
            return redirect('/pricing'),cleanup(db.session)
            # return render_template('enterprise_subscription.html')
    else:
        get_logger_function('/upgrade_demo_to_enterprise_subscription','error', 'this package not found please check the table ok package','cashier me site')
        return redirect('/pricing'),cleanup(db.session)


#calling this function by paytabs callback function
@app.route('/getResponseForUpgrade_subscription', methods=['POST', 'GET'])
def getResponseForUpgrade_subscription():
    '''very import function its return and calling by payment getway  *paytabs*
    1- get api and check data
    2- check transaction ref from api and search this to order table if exist or Not
    3-if transaction exists send api to get all transaction information
    4-if status == A can be upgrade subscription to enterprise and send email and created qr code for invoice'''
    get_response_data = request.form.to_dict()
    # get_response_data = request.json
    get_logger_function('/getResponseForUpgrade_subscription','info', 'get response >>>>>>'+str(get_response_data),'cashier me site')
    if get_response_data:
        get_transaction_ref = get_response_data['tranRef']
        get_transaction_token = get_response_data['token']
        if get_transaction_ref:
            get_data = Order.query.filter_by(tans_ref = get_transaction_ref).first()
            get_payment_data = Countries.query.filter_by(country_code = get_data.country_code_id).first()
            if get_data:
                get_logger_function('/getResponseForUpgrade_subscription','info', 'get_country>>>>'+str(get_payment_data.payment_merchant_id)+"country"+str(get_data.tans_ref),'cashier me site')
                data = {
                    'profile_id':str(get_payment_data.payment_merchant_id),
                    'tran_ref':str(get_data.tans_ref)
                }
            res = requests.post(str(get_payment_data.payment_query_link), data=json.dumps(data),headers = {'authorization':str(get_payment_data.payment_api_key),'content-type':'https://cashierme.com/getResponseForUpgrade_subscription'})
            result = json.loads(res.content)
            get_logger_function('/getResponseForUpgrade_subscription','info', 'response'+str(result),'cashier me site')

            print(result)
            get_json_transaction_ref = result.get('tran_ref')
            get_json_payment_result = result.get('payment_result')
            get_response_status = get_json_payment_result['response_status']
            get_response_message = get_json_payment_result['response_message']
            if get_data.tans_ref == get_json_transaction_ref:
                get_logger_function('/getResponseForUpgrade_subscription','info', 'get response from payment gateway successfully','cashier me site')
                print('ok check transaction refrence')
                if get_response_status == "A" and get_response_message == "Authorised":
                    get_logger_function('/getResponseForUpgrade_subscription','info', 'payment successfully status "A" ','cashier me site')
                    email = get_data.email
                    if get_data.sub_type == 'yearly':
                        update_time = 366
                    elif get_data.sub_type == 'Monthly':
                        update_time = 31
                    else:
                        update_time = 31
                    expire_db = datetime.now()+ timedelta(update_time)
                    # update subscription table
                    data = Subscription.query.filter(and_(Subscription.email == get_data.email, Subscription.business_name == get_data.business_name)).first()
                    data.name = get_data.name
                    data.stores_number = get_data.stores_number
                    data.best_time_call = get_data.best_time_call
                    data.city = get_data.city
                    data.contact = get_data.contact
                    data.password = get_data.password
                    data.tax_file = get_data.tax_file
                    data.commercial_register = get_data.commercial_register
                    data.expire_db = expire_db
                    data.order_id = get_data.id
                    data.Country = get_data.Country
                    data.subscription_type = 'Enterprise'
                    data.payment_status = 'Payment Successfully'
                    data.street = get_data.street
                    data.postcode = get_data.postcode
                    data.password_hash = get_data.password_hash
                    data.company_string_name = get_data.company_string_name
                    data.plan_type = get_data.sub_type
                    data.price = get_data.amount
                    data.account_type = "Live"
                    db.session.commit()
                    get_data.subscription_id = data.id
                    get_data.auto_payment_status = 'Done'
                    get_data.expire_db = expire_db
                    get_data.customer_token = get_transaction_token
                    get_data.account_type = "Live"
                    db.session.commit()
                    database_name = 'upos_'+data.business_name
                    import mysql.connector
                    try:
                        cnx = mysql.connector.connect(user=SECURE_KEYS.DB_USER, password=SECURE_KEYS.DB_PASSWORD, host='localhost', database=database_name)
                        cursor = cnx.cursor()
                        cursor.execute("UPDATE company_information set name ='"+ str(get_data.name) +"',stores_number='"+ str(get_data.stores_number)+"',best_time_call = '"+str(data.best_time_call) +"',city='"+ str(data.city) +"',contact='"+str(data.contact)+"',password='"+str(data.password)+"',tax_file='"+str(data.tax_file)+"',commercial_register='"+str(data.commercial_register)+"',company_token='"+ str(data.company_token)+"'")
                        cnx.commit()
                    except Exception as error:
                        get_logger_function('/getResponseForUpgrade_subscription','error', 'error for connect to database'+str(database_name) ,'cashier me site')
                        get_logger_function('/getResponseForUpgrade_subscription','error', str(error) + '---> from exption error from  the database----> '+str(database_name) ,'cashier me site')
                        pass
                    try:
                        conMysql = mysql.connector.connect(user=SECURE_KEYS.DB_USER, password=SECURE_KEYS.DB_PASSWORD, host='localhost', database=SECURE_KEYS.CONTROLLER_DB_NAME)
                        url = SECURE_KEYS.DASHBOARD_URL + data.business_name
                        connect = conMysql.cursor()
                        connect.execute("UPDATE  subscriptions set  full_name='"+str(data.name)+"',db_name='"+str(database_name)+
                                        "', url_input='"+str(url)+"',status='"+ str(data.subscription_type)+"',stores_number='"
                                        +str(data.stores_number)+"',contact='"+str(data.contact)+"',time_call='"+str(data.best_time_call)+"',password='"+str(data.password)
                                        +"',password_hash='"+str(data.password_hash)+"',company_string_name='"+str(data.company_string_name)+"',tax_file='"
                                        +str(data.tax_file)+"',commercial_register='"+str(data.commercial_register)+"',expire_db='"+str(data.expire_db)
                                        +"',country='"+str(data.Country)+"',street='"+str(data.street)+"',postcode='"+str(data.postcode)+"',subscription_type='"
                                        +str(get_data.sub_type)+"',created_from='"+str(data.created_from)+"',sub_table_id='"+str(data.id)+"',company_token='"+
                                        str(data.company_token)+"' where db_name='"+str(data.business_name)+"' ")
                        conMysql.commit()
                    except Exception as error:
                        get_logger_function('/getResponseForUpgrade_subscription','error', 'error for update data in upos_controller subscription table'+database_name ,'cashier me site')
                        get_logger_function('/getResponseForUpgrade_subscription','error', str(error) + '---> from exption error from  the database upos_controller----> ' ,'cashier me site')
                        pass
                    #add qr in invoice
                    saller_name = 'Ultimate Solutions'
                    seller_len = len(saller_name)
                    vat_number = '311136332100003'
                    dateandtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                    amount = str(get_data.amount)
                    amounts = get_data.amount
                    get_len = len(amount)
                    tax = round(int(amounts)-(int(amounts) / 1.15), 2)
                    # tax = (15 * int(amounts)) / 100
                    get_tax_len = len(str(tax))
                    company2hex = hexaConvertFunction.string2hex(saller_name)
                    fullCompany2hex = '01' + str(hexaConvertFunction.int2hex(seller_len)) + company2hex
                    vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
                    fullnumber2hex = '020F' + vatnumber2hex
                    datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
                    fulldatetimehex = '0314'+ datetimeInvoicehex
                    amount2hexa = hexaConvertFunction.string2hex(amount)
                    fulamount2hexa = '040'+ str(get_len) + amount2hexa
                    tax2hexa = hexaConvertFunction.string2hex(str(tax))
                    fulltax2hexa = '050' + str(get_tax_len) + tax2hexa
                    get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('hexa code :>>>>>>>>>>>>>>>',fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('base64 code >>>>>>>>>>>>>>',get_qr_base64)
                    get_data.qr_code_base64 = get_qr_base64
                    db.session.commit()
                    get_logger_function('/getResponseForUpgrade_subscription','info', 'invoice (QR) created successfully for>>>>'+str(data.business_name),'cashier me site')
                    try:
                        msg = Message(recipients=[email])
                        msg.html = render_template('invoicess.html',
                                                   password = data.password,
                                                   database_fullname = data.business_name,
                                                   name = get_data.name,
                                                   address = get_data.street,
                                                   city = get_data.city,
                                                   country = get_data.Country,
                                                   zip = get_data.postcode,
                                                   package = get_data.stores_number,
                                                   company = get_data.business_name,
                                                   domain =SECURE_KEYS.DASHBOARD_URL + data.business_name,
                                                   subscription = get_data.sub_type,
                                                   expire = get_data.expire_db,
                                                   price = get_data.amount,
                                                   invoice_num = str(get_data.id ),
                                                   invoice_date = datetime.now(),
                                                   img_data=get_qr_base64)
                        mail.send(msg)
                    except Exception as error:
                        get_logger_function('/getResponseForUpgrade_subscription','error', str(error),'cashier me site')
                        pass
                    get_logger_function('/getResponseForUpgrade_subscription','info', '"subscription has been upgraded ','cashier me site')
                    message = gettext('Congratulations, your subscription has been upgraded')
                    return render_template('enterprise_payment_result.html'
                                           , get_url =SECURE_KEYS.DASHBOARD_URL + data.business_name,
                                           message_sucssess = message,
                                           name = data.name,
                                           address = get_data.street,
                                           city = get_data.city,
                                           country = get_data.Country,
                                           zip = get_data.postcode,
                                           package = get_data.stores_number,
                                           company = get_data.business_name,
                                           domain =SECURE_KEYS.DASHBOARD_URL + data.business_name,
                                           subscription = get_data.sub_type,
                                           expire = get_data.expire_db,
                                           price = get_data.amount,
                                           invoice_num = str(get_data.id ),
                                           invoice_date = datetime.now(),
                                           img_data=get_qr_base64,
                                           email = get_data.email,
                                           password = get_data.password
                                           ),cleanup(db.session)
                else:
                    get_order_id = Order.query.filter_by(id = get_data.id).first()
                    db.session.delete(get_order_id)
                    db.session.commit()
                    message_error = gettext("The process cannot be completed, please try another payment card if you want to back pricing page")
                    return render_template('enterprise_payment_result.html', get_url='https://cashierme.com/pricing',message_error = message_error ),cleanup(db.session)
            else:
                get_logger_function('/getResponseForUpgrade_subscription','error', 'the transaction ref not == tran_ref from response','cashier me site')
                message_error = gettext("cannot process your request now please try again letter")
                return render_template('enterprise_payment_result.html', get_url='https://cashierme.com/pricing',message_error = message_error ),cleanup(db.session)
        else:
            get_logger_function('/getResponseForUpgrade_subscription','error', 'get tran_ref error it none value','cashier me site')
            message_error = gettext("cannot process your request now please try again letter")
            return render_template('enterprise_payment_result.html', get_url='https://cashierme.com/pricing',message_error = message_error ),cleanup(db.session)
    else:
        get_logger_function('/getResponseForUpgrade_subscription','error', 'get tran_ref error it none value check response fro api','cashier me site')
        message_error = gettext("cannot process your request now please try again letter")
        return render_template('enterprise_payment_result.html', get_url='https://cashierme.com/pricing',message_error = message_error ),cleanup(db.session)



@app.route('/india_error_payment_message')
def india_error_payment_message():
    message_error = gettext(
        "The process cannot be completed, please try another payment card if you want to back pricing page")

    return render_template('enterprise_payment_result.html',
                           get_url='https://cashierme.com/pricing',
                           message_error=message_error,active_page='india_error_payment_message'), cleanup(db.session)


@app.route('/delete_failed_payment_order/<string:order_id>', methods=['POST'])
def delete_failed_payment_order(order_id):
    try:
        check_order_id = Order.query.filter_by(razorpay_order_id = order_id).first()
        db.session.delete(check_order_id)
        db.session.commit()
        get_logger_function('/delete_failed_payment_order','info', 'success delete order failed payment for india payment this order is>>'+order_id,'cashier me site')
        return "success"
    except Exception as e:
        return "error"



#check email in database by ajax return 1 or 0
@app.route('/get_email_methods/<string:data>/<string:check_type>', methods=['POST', 'GET'])
def get_email_methods(data,check_type):
    try:
        if check_type == "email":
            check_email = Subscription.query.filter_by(email = data ).first()
            if check_email:
                print(check_email.email)
                return '1'
            else:
                return '0'
        elif check_type == "contact":
            check_contact = Subscription.query.filter_by(contact = data ).first()
            if check_contact:
                print(check_contact.contact)
                return '1'
            else:
                return '0'
    except Exception as error :
        get_logger_function('/get_email_methods','Error', str(error),'cashier me site')
        return "error"



#check price of point of sale by ajax and reurn true or false
@app.route('/get_price_of_package/<string:pos_num>/<string:subtype>', methods=['POST'])
def get_price_of_package(pos_num, subtype):
    try:
        get_price_pos = Countries.query.filter_by(country_code=current_user.country_code_id).first()
        get_pos_now = current_user.stores_number #numbers of pos customer have it
        pos_amount_balance = get_price_pos.monthly_amount
        daily_pos_amount_balance = float(int(pos_amount_balance) / 30)
        get_expire_date_balance = current_user.expire_db  # expire date
        get_date_today_balance = datetime.now()  # date and time now
        calculation_date_balance = get_expire_date_balance-get_date_today_balance
        get_date_object_balance = calculation_date_balance.days  # numbers of days customer have
        amount_of_balance = (int(get_date_object_balance) * int(daily_pos_amount_balance))*int(get_pos_now)
        print(">>>>>>>>>>>>>>>sssssss",amount_of_balance)
        if subtype == 'Monthly':
            current_user_pos = current_user.stores_number #numbers of pos customer have it
            pos_amount = get_price_pos.monthly_amount
            daily_pos_amount = float(int(pos_amount) / 30)
            print(daily_pos_amount)
            pos_selection = pos_num # pos number customer want to add
            get_expire_date = current_user.expire_db #expire date
            get_date_today = datetime.now() #date and time now
            calculation_date = get_expire_date - get_date_today
            get_date_object = calculation_date.days #numbers of days customer have
            print(get_date_object)
            get_pos = int(pos_selection) - int(current_user_pos)
            full_calculation = float(get_date_object * daily_pos_amount)*get_pos
            payment_price = round(full_calculation, 3)
            print(payment_price)
            get_data =  Packages.query.filter(and_(Packages.type == subtype, Packages.pos_no_code == pos_num,Packages.country_code == current_user.country_code_id)).first()
            if get_data:
                return {'price':get_data.price,
                        'fullcal':payment_price}
        if subtype == 'yearly':
            pos_amount = get_price_pos.annually_amount
            daily_pos_amount = float(int(pos_amount) / 365)
            print(">>>>>>>>>>>welcome sameer your is ",daily_pos_amount)
            current_user_pos = current_user.stores_number
            pos_selection = pos_num
            get_expire_date = current_user.expire_db
            get_date_today = datetime.now()
            calculation_date = get_expire_date - get_date_today
            get_date_object = calculation_date.days
            print(get_date_object)
            get_pos = int(pos_selection) - int(current_user_pos)
            full_calculation = float(get_date_object * daily_pos_amount)*get_pos
            print(full_calculation)
            get_amount = float(get_date_object * daily_pos_amount*12)*get_pos
            get_data =  Packages.query.filter(and_(Packages.type == subtype, Packages.pos_no_code == pos_num,Packages.country_code == current_user.country_code_id)).first()
            if get_data:
                print("my price",get_data.price)
                print("my balance", amount_of_balance)
                balance = int(get_data.price) - int(amount_of_balance)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>sdasdad>>>>>>>>>>>>",balance)
                print(get_amount)
                return {'price':get_data.price,
                                'fullcal':full_calculation,
                                'Balance':balance,
                                "get_amount":get_amount}
        else:
            return 'flase',cleanup(db.session)
    except Exception as Error:
        print(Error)
        return {"error": str(Error)}


#check price of poin
# t of sale by ajax and reurn true or false
@app.route('/get_price_of_package_ofUsers/<string:pos_num>/<string:subtype>', methods=['POST'])
def get_price_of_package_ofUsers(pos_num, subtype):
    get_data = Packages.query.filter(and_(Packages.type == subtype, Packages.pos_no_code == pos_num,Packages.country_code == session['country_code'])).first()
    if get_data:
        print("ssssssssssssssssssssssssss")
        return get_data.price
    else:
        return 'flase'


@app.route('/india_upgrade_pos_monthly/<string:price_old>/<string:pos_no_get>/<string:sub_type>', methods=['POST'])
def india_upgrade_pos_monthly(price_old,pos_no_get,sub_type):
    try:
        price = ""
        if sub_type == 'Monthly':
            get_price_monthly = get_price_of_package(pos_no_get, sub_type )
            price = get_price_monthly['fullcal']
        elif sub_type == 'yearly':
            if current_user.plan_type == sub_type:
                get_price_annualy = get_price_of_package(pos_no_get, sub_type )
                get_amount_from_package = get_price_annualy['get_amount']
                price = int(get_amount_from_package)

            else:
                get_price_annualy = get_price_of_package(pos_no_get, sub_type )
                price = get_price_annualy['Balance']
        amount = int(price) * 100
        client = razorpay.Client(
            auth=(SECURE_KEYS.RAZORPAY_ID,
                  SECURE_KEYS.RAZORPAY_SECRET))
        razorpay_data = {"amount" :amount, "currency" :"INR",
                         "receipt" :"order_rcptid_11"}
        payment = client.order.create(data=razorpay_data)
        db.session.commit( )
        print(payment)
        return payment
    except Exception as error:
        get_logger_function('/india_upgrade_pos_monthly','error', str(error),'cashier me site')
        print(error)
        return "Error"




@app.route('/india_success_upgrade_pos/<string:price_old>/<string:pos_no_get>/<string:sub_type>/<string:razorpay_order_id>/<string:razorpay_payment_id>/<string:razorpay_signature>',methods=['POST'])
def india_success_upgrade_pos(price_old, pos_no_get, sub_type,razorpay_order_id,razorpay_payment_id,razorpay_signature) :
    try:
        if sub_type == 'Monthly' :
            get_price_monthly = get_price_of_package(pos_no_get, sub_type)
            price = get_price_monthly['fullcal']
        elif sub_type == 'yearly' :
            if current_user.plan_type == sub_type :
                get_price_annualy = get_price_of_package(pos_no_get, sub_type)
                get_amount_from_package = get_price_annualy['get_amount']
                price = int(get_amount_from_package)
            else :
                get_price_annualy = get_price_of_package(pos_no_get, sub_type)
                price = get_price_annualy['fullcal']
        pos_no = int(pos_no_get)-int(current_user.stores_number)
        get_id = current_user.order_id
        print(get_id)
        get_data = Order.query.filter_by(id=get_id).first( )
        # get_payment_data = Countries.query.filter_by(country_code=current_user.country_code_id).first( )
        name = get_data.name
        email = get_data.email
        stores_number = int(pos_no)
        business_name = get_data.business_name
        best_time_call = get_data.best_time_call
        street = get_data.street
        country = get_data.Country
        postcode = get_data.postcode
        contact = get_data.contact
        password = get_data.password
        tax_file = get_data.tax_file
        commercial_register = get_data.commercial_register
        sub_id = get_data.subscription_id
        order_date = datetime.now( )
        status_order = 'Done'
        order_code = razorpay_order_id
        amount = price
        city = get_data.city
        expire_db = get_data.expire_db
        auto_payment = 'Done'
        password_hash = get_data.password_hash
        company_string_name = get_data.company_string_name
        create_order = Order(name, email, stores_number, business_name, city,
                             contact, password, tax_file, commercial_register,
                             order_date, street, country, postcode,
                             status_order, order_code, amount, sub_type,
                             expire_db, password_hash, '', company_string_name)
        db.session.add(create_order)
        db.session.commit( )
        create_order.best_time_call = best_time_call
        create_order.subscription_id = sub_id
        create_order.razorpay_order_id = razorpay_order_id
        create_order.razorpay_payment_id = razorpay_payment_id
        create_order.razorpay_signature = razorpay_signature
        create_order.payment_getway = "razorpay"
        create_order.auto_payment_status = auto_payment
        create_order.country_code_id = current_user.country_code_id
        create_order.account_type = "Live"
        db.session.commit( )
        try :
            saller_name = 'Ultimate Solutions'
            seller_len = len(saller_name)
            vat_number = '311136332100003'
            dateandtime = datetime.now( ).strftime('%Y-%m-%dT%H:%M:%SZ')
            amount = str(price)
            amounts = price
            get_len = len(amount)
            tax = round(int(amounts)-(int(amounts) / 1.15), 2)
            # tax = (15 * int(amounts)) / 100
            get_tax_len = len(str(tax))
            company2hex = hexaConvertFunction.string2hex(saller_name)
            fullCompany2hex = '01'+str(
                hexaConvertFunction.int2hex(seller_len))+company2hex
            vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
            fullnumber2hex = '020F'+vatnumber2hex
            datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
            fulldatetimehex = '0314'+datetimeInvoicehex
            amount2hexa = hexaConvertFunction.string2hex(amount)
            fulamount2hexa = '040'+str(get_len)+amount2hexa
            tax2hexa = hexaConvertFunction.string2hex(str(tax))
            fulltax2hexa = '050'+str(get_tax_len)+tax2hexa
            get_qr_base64 = hexa2base64.hex2funbase64(
                fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
            print('hexa code :>>>>>>>>>>>>>>>',
                  fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
            print('base64 code >>>>>>>>>>>>>>', get_qr_base64)
            create_order.qr_code_base64 = get_qr_base64
            db.session.commit( )
            get_logger_function('/confirm_upgrade_posNo_subscription_monthly',
                                'info',
                                'invoice (QR) created successfully for>>>>'+get_data.business_name,
                                'cashier me site')
            try :
                msg = Message(recipients=[email])
                msg.body = gettext('User No :') +'1' +'\n' + gettext(
                    'password :') + get_data.password +'\n' + gettext(
                    'Registration Code For Application:') +'\n' + get_data.business_name +'\n' + gettext(
                    'Update Subscription in:') + get_data.expire_db.strftime(
                    "%b %d %Y") +'\n' + SECURE_KEYS.DASHBOARD_URL + get_data.business_name
                msg.html = render_template('invoicess.html',
                                           password=get_data.password,
                                           database_fullname=get_data.business_name,
                                           name=get_data.name,
                                           address=get_data.street,
                                           city=get_data.city,
                                           country=get_data.Country,
                                           zip=get_data.postcode,
                                           package=pos_no,
                                           company=get_data.business_name,
                                           domain=SECURE_KEYS.DASHBOARD_URL + get_data.business_name,
                                           subscription=get_data.sub_type,
                                           expire=get_data.expire_db,
                                           price=price,
                                           invoice_num=str(create_order.id),
                                           invoice_date=datetime.now( ),
                                           img_data=get_qr_base64)
                mail.send(msg)
            except Exception as error :
                get_logger_function(
                    '/confirm_upgrade_posNo_subscription_monthly', 'error',
                    str(error), 'cashier me site')
                print(error)
                pass
        except Exception as error :
            get_logger_function('/confirm_upgrade_posNo_subscription_monthly',
                                'error', str(error), 'cashier me site')
            print(error)
            pass
        try :
            sub_data = Subscription.query.filter_by(
                id=create_order.subscription_id).first( )
            print(sub_data)
            get_pos_number = str(int(sub_data.stores_number)+int(pos_no))
            print(get_pos_number)
            get_price = Packages.query.filter(
                and_(Packages.type == sub_data.plan_type,
                     Packages.pos_no_code == get_pos_number,
                     Packages.country_code == session['country_code'])).first( )
            get_amount = get_price.price
            sub_data.stores_number = str(
                int(sub_data.stores_number)+int(create_order.stores_number))
            sub_data.price = get_amount
            sub_data.order_id = create_order.id
            db.session.commit( )
            create_order.sub_type_toUpdate = sub_data.plan_type
            create_order.pos_no_toUpdate = get_pos_number
            create_order.price_toUpdate = sub_data.price
            db.session.commit( )
            get_logger_function('/confirm_upgrade_posNo_subscription_monthly',
                                'info',
                                'update pos no has been successfully updated in subscription table'+get_data.business_name,
                                'cashier me site')
            return jsonify({"status" :"success",
                            "value" :create_order.id})
        except Exception as error :
            get_logger_function('/confirm_upgrade_posNo_subscription_monthly',
                                'error', str(error), 'cashier me site')
            print(error)
            return "Failed_update"
        pass
    except Exception as Error:
        print(Error)
        pass
    return "Error"


#upgrade pos number in subscription monthly or Annualy
@app.route('/confirm_upgrade_posNo_subscription_monthly/<string:price_old>/<string:pos_no_get>/<string:sub_type>', methods=['POST'])
@check_coutry
def confirm_upgrade_posNo_subscription_monthly(price_old,pos_no_get,sub_type):
    try:
        if sub_type == 'Monthly':
            get_price_monthly = get_price_of_package(pos_no_get, sub_type )
            price = get_price_monthly['fullcal']
        elif sub_type == 'yearly':
            if current_user.plan_type == sub_type:
                get_price_annualy = get_price_of_package(pos_no_get, sub_type )
                get_amount_from_package = get_price_annualy['get_amount']
                price = float("{:.2f}".format(get_amount_from_package))

            else:
                get_price_annualy = get_price_of_package(pos_no_get, sub_type )
                price = get_price_annualy['fullcal']

        pos_no = int(pos_no_get) - int(current_user.stores_number)
        get_id = current_user.order_id
        print(get_id)
        get_data = Order.query.filter_by(id = get_id).first()
        get_payment_data = Countries.query.filter_by(country_code =current_user.country_code_id).first()
        get_transaction_ref = get_data.tans_ref
        get_customer_token = get_data.customer_token
        random_code1 = random.randint(1, 100000)
        random_code2 = random.randint(1, 100000)
        order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
        print(order_code)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>> welcome samir mostafa your price is ',price)
        payment_request = {
            "profile_id":str(get_payment_data.payment_merchant_id) ,
            "tran_type":"sale" ,
            "tran_class":"recurring" ,
            "cart_id": str(order_code) ,
            "cart_currency":str(get_payment_data.payment_currency) ,
            "cart_amount":str(price) ,
            "cart_description":"test for toffffken customer" ,
            "token": str(get_customer_token) ,
            "tran_ref":str(get_transaction_ref)
        }
        print(payment_request)
        response = requests.post(str(get_payment_data.payment_request_api_url), data = json.dumps(payment_request), headers = {'authorization':str(get_payment_data.payment_api_key),'content-type':'application/json'})
        try:
            print("ddddddddddddddddd")
            get_logger_function('confirm_upgrade_posNo_subscription_monthly','info', 'check data and expiration date and send request to paytabs  is successfully' ,'cashier me site')
            result = json.loads(response.content)
            print(result)
            get_json_transaction_ref = result.get('tran_ref')
            get_json_payment_result = result.get('payment_result')
            get_response_status = get_json_payment_result['response_status']
            get_response_message = get_json_payment_result['response_message']
            get_data.tans_ref = get_json_transaction_ref
            db.session.commit()
            print(get_json_transaction_ref,get_json_payment_result)
            if get_response_status == 'A' and get_response_message == "Authorised":
                name = get_data.name
                email = get_data.email
                stores_number = int(pos_no)
                business_name = get_data.business_name
                best_time_call = get_data.best_time_call
                street = get_data.street
                country = get_data.Country
                postcode = get_data.postcode
                contact = get_data.contact
                password = get_data.password
                tax_file = get_data.tax_file
                commercial_register = get_data.commercial_register
                sub_id = get_data.subscription_id
                order_date = datetime.now()
                status_order = 'Done'
                order_code = order_code
                trans_ref = get_json_transaction_ref
                amount = price
                customer_token = get_data.customer_token
                city = get_data.city
                # sub_type = 'Monthly'
                expire_db = get_data.expire_db
                auto_payment = 'Done'
                password_hash = get_data.password_hash
                company_string_name = get_data.company_string_name
                create_order = Order(name, email, stores_number, business_name, city, contact, password, tax_file, commercial_register, order_date, street, country, postcode, status_order, order_code, amount, sub_type,expire_db,password_hash,'',company_string_name)
                db.session.add(create_order)
                db.session.commit()
                create_order.best_time_call = best_time_call
                create_order.subscription_id = sub_id
                create_order.tans_ref = trans_ref
                create_order.customer_token = customer_token
                create_order.auto_payment_status = auto_payment
                create_order.country_code_id = current_user.country_code_id
                create_order.account_type = "Live"
                db.session.commit()
                try:
                    saller_name = 'Ultimate Solutions'
                    seller_len = len(saller_name)
                    vat_number = '311136332100003'
                    dateandtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                    amount = str(price)
                    amounts = price
                    get_len = len(amount)
                    tax = round(int(amounts)-(int(amounts) / 1.15), 2)
                    # tax = (15 * int(amounts)) / 100
                    get_tax_len = len(str(tax))
                    company2hex = hexaConvertFunction.string2hex(saller_name)
                    fullCompany2hex = '01' + str(hexaConvertFunction.int2hex(seller_len)) + company2hex
                    vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
                    fullnumber2hex = '020F' + vatnumber2hex
                    datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
                    fulldatetimehex = '0314'+ datetimeInvoicehex
                    amount2hexa = hexaConvertFunction.string2hex(amount)
                    fulamount2hexa = '040'+ str(get_len) + amount2hexa
                    tax2hexa = hexaConvertFunction.string2hex(str(tax))
                    fulltax2hexa = '050' + str(get_tax_len) + tax2hexa
                    get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('hexa code :>>>>>>>>>>>>>>>',fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('base64 code >>>>>>>>>>>>>>',get_qr_base64)
                    create_order.qr_code_base64 = get_qr_base64
                    db.session.commit()
                    get_logger_function('/confirm_upgrade_posNo_subscription_monthly','info', 'invoice (QR) created successfully for>>>>'+get_data.business_name,'cashier me site')
                    try:
                        msg = Message(recipients=[email])
                        msg.body = gettext('User No :') + '1' +  '\n' + gettext('password :') + get_data.password + '\n' + gettext('Registration Code For Application:') + '\n' + get_data.business_name + '\n' + gettext('Update Subscription in:') + get_data.expire_db.strftime("%b %d %Y") +'\n' + SECURE_KEYS.DASHBOARD_URL + get_data.business_name
                        msg.html = render_template('invoicess.html',
                                                   password = get_data.password,
                                                   database_fullname = get_data.business_name,
                                                   name = get_data.name,
                                                   address = get_data.street,
                                                   city = get_data.city,
                                                   country = get_data.Country,
                                                   zip = get_data.postcode,
                                                   package = pos_no,
                                                   company = get_data.business_name,
                                                   domain =SECURE_KEYS.DASHBOARD_URL + get_data.business_name,
                                                   subscription = get_data.sub_type,
                                                   expire = get_data.expire_db,
                                                   price = price,
                                                   invoice_num = str(create_order.id),
                                                   invoice_date = datetime.now(),
                                                   img_data=get_qr_base64)
                        mail.send(msg)
                    except Exception as error:
                        get_logger_function('/confirm_upgrade_posNo_subscription_monthly','error', str(error),'cashier me site')
                        print(error)
                        pass
                except Exception as error:
                    get_logger_function('/confirm_upgrade_posNo_subscription_monthly','error', str(error),'cashier me site')
                    print(error)
                    pass
                try:
                    sub_data = Subscription.query.filter_by(id = create_order.subscription_id).first()
                    print(sub_data)
                    get_pos_number = str(int(sub_data.stores_number) + int(pos_no))
                    print(get_pos_number)
                    get_price = Packages.query.filter(and_(Packages.type == sub_data.plan_type, Packages.pos_no_code == get_pos_number,Packages.country_code == session['country_code'])).first()
                    get_amount = get_price.price
                    sub_data.stores_number = str(int(sub_data.stores_number) + int(create_order.stores_number))
                    sub_data.price = get_amount
                    sub_data.order_id = create_order.id
                    db.session.commit()
                    create_order.sub_type_toUpdate = sub_data.plan_type
                    create_order.pos_no_toUpdate = get_pos_number
                    create_order.price_toUpdate = sub_data.price
                    db.session.commit()
                    get_logger_function('/confirm_upgrade_posNo_subscription_monthly','info', 'update pos no has been successfully updated in subscription table'+get_data.business_name,'cashier me site')
                    return jsonify({"status":"success",
                                    "value":create_order.id})
                except Exception as error:
                    get_logger_function('/confirm_upgrade_posNo_subscription_monthly','error', str(error),'cashier me site')
                    print(error)
                    return "Failed_update"
            elif get_response_status == 'E':
                get_logger_function('/confirm_upgrade_posNo_subscription_monthly','info', 'customer not have money in cared to update point of sale'+get_data.business_name,'cashier me site')
                return "customer_havenot_money"
            elif get_response_status == 'D':
                get_logger_function('/confirm_upgrade_posNo_subscription_monthly','info', 'paytabs not proccess this transaction please try again'+get_data.business_name,'cashier me site')
                print("D")
                return "Cant_process_now"
            else:
                get_logger_function('/confirm_upgrade_posNo_subscription_monthly','info', 'you have response code not add in system please fixed this code and search in paytabs to fixed it'+get_data.business_name,'cashier me site')
                return "get_code_error"
        except Exception as error:
            get_logger_function('/confirm_upgrade_posNo_subscription_monthly','error', str(error),'cashier me site')
            print(error)
            return "error_for_request"
    except Exception as error:
        get_logger_function('/confirm_upgrade_posNo_subscription_monthly','error', str(error),'cashier me site')
        print(error)
        return "Error"


#remove pos no
@app.route('/upgrade_pos_confirm_order_remove/<string:pos_no>/<string:type>', methods=['POST'])
@check_coutry
def upgrade_pos_confirm_order_remove(pos_no, type):
    get_pos_no = int(current_user.stores_number) - int(pos_no)
    try:
       get_data_package = Packages.query.filter(and_(Packages.type == type, Packages.pos_no_code == str(get_pos_no),Packages.country_code == session['country_code'])).first()
       get_price = get_data_package.price
       get_order_id = current_user.order_id
       get_order = Order.query.filter_by(id = get_order_id).first()
       get_order.sub_type_toUpdate = type
       get_order.pos_no_toUpdate = str(get_pos_no)
       get_order.price_toUpdate = get_price
       db.session.commit()
       return "success"
    except Exception as error:
        get_logger_function('/upgrade_pos_confirm_order_remove','error', str(error),'cashier me site')
        print(error)
        return "Failed"

@app.route('/india_upgrade_demo_to_enterprise/<string:razorpay_payment_id>/<string:razorpay_order_id>/<string:razorpay_signature>', methods=['POST', 'GET'])
def india_upgrade_demo_to_enterprise(razorpay_payment_id,razorpay_order_id,razorpay_signature):
    try:
        get_data = Order.query.filter(and_(Order.razorpay_order_id == razorpay_order_id ,Order.razorpay_payment_id == None,Order.razorpay_signature == None,Order.payment_getway == "razorpay")).first()
        email = get_data.email
        if get_data.sub_type == 'yearly' :
            update_time = 366
        elif get_data.sub_type == 'Monthly' :
            update_time = 31
        else :
            update_time = 31
        expire_db = datetime.now( )+timedelta(update_time)
        # update subscription table
        data = Subscription.query.filter(and_(Subscription.email == get_data.email,Subscription.business_name == get_data.business_name)).first( )
        data.name = get_data.name
        data.stores_number = get_data.stores_number
        data.best_time_call = get_data.best_time_call
        data.city = get_data.city
        data.contact = get_data.contact
        data.password = get_data.password
        data.tax_file = get_data.tax_file
        data.commercial_register = get_data.commercial_register
        data.expire_db = expire_db
        data.order_id = get_data.id
        data.Country = get_data.Country
        data.subscription_type = 'Enterprise'
        data.payment_status = 'Payment Successfully'
        data.street = get_data.street
        data.postcode = get_data.postcode
        data.password_hash = get_data.password_hash
        data.company_string_name = get_data.company_string_name
        data.plan_type = get_data.sub_type
        data.price = get_data.amount
        data.account_type = "Live"
        db.session.commit( )
        get_data.subscription_id = data.id
        get_data.auto_payment_status = 'Done'
        get_data.expire_db = expire_db
        get_data.razorpay_payment_id = razorpay_payment_id
        get_data.razorpay_signature = razorpay_signature
        get_data.account_type = "Live"
        db.session.commit( )
        database_name = 'upos_'+data.business_name
        import mysql.connector
        try :
            conMysql = mysql.connector.connect(user=SECURE_KEYS.DB_USER,
                                               password=SECURE_KEYS.DB_PASSWORD,
                                               host='localhost',
                                               database=SECURE_KEYS.CONTROLLER_DB_NAME)
            url = SECURE_KEYS.DASHBOARD_URL + data.business_name
            connect = conMysql.cursor( )
            connect.execute("UPDATE  subscriptions set  full_name='"+str(
                data.name)+"',db_name='"+str(database_name)+
                            "', url_input='"+str(url)+"',status='"+str(
                data.subscription_type)+"',stores_number='"
                            +str(data.stores_number)+"',contact='"+str(
                data.contact)+"',time_call='"+str(
                data.best_time_call)+"',password='"+str(data.password)
                            +"',password_hash='"+str(
                data.password_hash)+"',company_string_name='"+str(
                data.company_string_name)+"',tax_file='"
                            +str(data.tax_file)+"',commercial_register='"+str(
                data.commercial_register)+"',expire_db='"+str(data.expire_db)
                            +"',country='"+str(data.Country)+"',street='"+str(
                data.street)+"',postcode='"+str(
                data.postcode)+"',subscription_type='"
                            +str(get_data.sub_type)+"',created_from='"+str(
                data.created_from)+"',sub_table_id='"+str(
                data.id)+"',company_token='"+
                            str(data.company_token)+"' where db_name='"+str(
                data.business_name)+"' ")
            conMysql.commit( )
        except Exception as error :
            get_logger_function('/getResponseForUpgrade_subscription', 'error',
                                'error for update data in upos_controller subscription table'+database_name,
                                'cashier me site')
            get_logger_function('/getResponseForUpgrade_subscription', 'error',
                                str(error)+'---> from exption error from  the database upos_controller----> ',
                                'cashier me site')
            pass
        # add qr in invoice
        saller_name = 'Ultimate Solutions'
        seller_len = len(saller_name)
        vat_number = '311136332100003'
        dateandtime = datetime.now( ).strftime('%Y-%m-%dT%H:%M:%SZ')
        amount = str(get_data.amount)
        amounts = get_data.amount
        get_len = len(amount)
        tax = round(int(amounts)-(int(amounts) / 1.15), 2)
        # tax = (15 * int(amounts)) / 100
        get_tax_len = len(str(tax))
        company2hex = hexaConvertFunction.string2hex(saller_name)
        fullCompany2hex = '01'+str(
            hexaConvertFunction.int2hex(seller_len))+company2hex
        vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
        fullnumber2hex = '020F'+vatnumber2hex
        datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
        fulldatetimehex = '0314'+datetimeInvoicehex
        amount2hexa = hexaConvertFunction.string2hex(amount)
        fulamount2hexa = '040'+str(get_len)+amount2hexa
        tax2hexa = hexaConvertFunction.string2hex(str(tax))
        fulltax2hexa = '050'+str(get_tax_len)+tax2hexa
        get_qr_base64 = hexa2base64.hex2funbase64(
            fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
        print('hexa code :>>>>>>>>>>>>>>>',
              fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
        print('base64 code >>>>>>>>>>>>>>', get_qr_base64)
        get_data.qr_code_base64 = get_qr_base64
        db.session.commit( )
        get_logger_function('/getResponseForUpgrade_subscription', 'info',
                            'invoice (QR) created successfully for>>>>'+str(
                                data.business_name), 'cashier me site')
        try :
            msg = Message(recipients=[email])
            msg.html = render_template('invoicess.html',
                                       password=data.password,
                                       database_fullname=data.business_name,
                                       name=get_data.name,
                                       address=get_data.street,
                                       city=get_data.city,
                                       country=get_data.Country,
                                       zip=get_data.postcode,
                                       package=get_data.stores_number,
                                       company=get_data.business_name,
                                       domain=SECURE_KEYS.DASHBOARD_URL + data.business_name,
                                       subscription=get_data.sub_type,
                                       expire=get_data.expire_db,
                                       price=get_data.amount,
                                       invoice_num=str(get_data.id),
                                       invoice_date=datetime.now( ),
                                       img_data=get_qr_base64)
            mail.send(msg)
        except Exception as error :
            get_logger_function('/getResponseForUpgrade_subscription', 'error',
                                str(error), 'cashier me site')
            pass
        get_logger_function('/getResponseForUpgrade_subscription', 'info',
                            '"subscription has been upgraded ',
                            'cashier me site')
        message = gettext(
            'Congratulations, your subscription has been upgraded')
        return render_template('enterprise_payment_result.html',
                               get_url=SECURE_KEYS.DASHBOARD_URL + data.business_name,
                               message_sucssess=message,
                               name=data.name,
                               address=get_data.street,
                               city=get_data.city,
                               country=get_data.Country,
                               zip=get_data.postcode,
                               package=get_data.stores_number,
                               company=get_data.business_name,
                               domain=SECURE_KEYS.DASHBOARD_URL + data.business_name,
                               subscription=get_data.sub_type,
                               expire=get_data.expire_db,
                               price=get_data.amount,
                               invoice_num=str(get_data.id),
                               invoice_date=datetime.now( ),
                               img_data=get_qr_base64,
                               email=get_data.email,
                               password=get_data.password
                               ), cleanup(db.session)
    except Exception as Error:
        print(">>>>>>>>>>>>>>>>>>>>>> 16-7-2022",Error)
        return redirect('/')
    return redirect('/')


@app.route('/india_enterprise_subscription/<string:razorpay_payment_id>/<string:razorpay_order_id>/<string:razorpay_signature>', methods=['POST', 'GET'])
def india_enterprise_subscription(razorpay_payment_id,razorpay_order_id,razorpay_signature):
    try:
        check_order_id = Order.query.filter_by(razorpay_order_id = razorpay_order_id).first()
        if check_order_id:
            get_name = check_order_id.name
            name = get_name.replace(".", "_")
            email = check_order_id.email
            stores_number = check_order_id.stores_number
            bs_name = check_order_id.business_name
            company_string_name = check_order_id.company_string_name
            business_name = bs_name.replace(".", "_")
            password = check_order_id.password
            password_bcrypt = check_order_id.password_hash
            file_taxess = check_order_id.tax_file
            commercial_register = check_order_id.commercial_register
            if check_order_id.sub_type == 'yearly' :
                update_time = 366
            elif check_order_id.sub_type == 'Monthly' :
                update_time = 31
            else :
                update_time = 31
            database_create_dt = datetime.now( )
            expire_db = datetime.now( )+timedelta(update_time)
            database_create_name = business_name.replace(" ", "")
            random_name = random.randint(1, 1000000)
            database_fullname = str(
                check_order_id.country_code_id)+"_"+database_create_name+'_'+str(
                random_name)
            best_time_call = '10am'
            city = check_order_id.city
            country = check_order_id.Country
            contact = check_order_id.contact
            created_from = 'From_site'
            company_token = random.randint(1, 100000000000000000)
            data = Subscription(name, email, stores_number, database_fullname,
                                best_time_call, city, contact,
                                database_create_dt, password,
                                file_taxess, commercial_register, expire_db,
                                database_create_dt,
                                country, 'Enterprise', check_order_id.street,
                                check_order_id.postcode,
                                password_bcrypt, company_string_name,
                                created_from, company_token,"","","","","")
            db.session.add(data)
            db.session.commit( )
            data.db_status = "pending"
            data.order_id = check_order_id.id
            data.payment_status = 'Payment Successfully'
            data.plan_type = check_order_id.sub_type
            data.price = check_order_id.amount
            data.country_code_id = check_order_id.country_code_id
            data.payment_getway = "razorpay"
            data.account_type = "Live"
            db.session.commit()
            check_order_id.subscription_id = data.id
            check_order_id.auto_payment_status = 'Done'
            check_order_id.expire_db = expire_db
            check_order_id.razorpay_order_id = razorpay_order_id
            check_order_id.razorpay_payment_id = razorpay_payment_id
            check_order_id.razorpay_signature = razorpay_signature
            check_order_id.account_type = "Live"
            db.session.commit( )
            import mysql.connector
            try :
                conMysql = mysql.connector.connect(user=SECURE_KEYS.DB_USER,
                                                   password=SECURE_KEYS.DB_PASSWORD,
                                                   host='localhost',
                                                   database=SECURE_KEYS.CONTROLLER_DB_NAME)
                if conMysql :
                    status = 'Enterprise'
                    url = SECURE_KEYS.DASHBOARD_URL + database_fullname
                    connect = conMysql.cursor( )
                    connect.execute(
                        "INSERT INTO  subscriptions (full_name,company_name,url_unique_name,"
                        "email,db_name, url_input,status,db_create_date,stores_number,contact,"
                        "time_call,password,password_hash,company_string_name,tax_file,commercial_register,"
                        "check_email_time,expire_db,country,street,postcode,subscription_type,created_from,sub_table_id,company_token )"
                        " VALUES (%s, %s, %s,%s, %s, %s, %s, %s,%s,%s,%s, %s, %s,%s, %s, %s, %s, %s,%s,%s, %s,%s,%s,%s,%s)"
                        , (name, business_name, database_fullname, email,
                           database_fullname, url, status, database_create_dt,
                           stores_number, contact,
                           best_time_call, password, password_bcrypt,
                           company_string_name, file_taxess,
                           commercial_register,
                           database_create_dt, expire_db, country,
                           check_order_id.street, check_order_id.postcode,
                           check_order_id.sub_type, created_from, data.id,
                           company_token))
                    conMysql.commit( )
                else :
                    return redirect('/')
            except Exception as error :
                get_logger_function('/get_transaction', 'error',
                                    'error for create in db controller'+str(
                                        error),
                                    'cashier me site')

            saller_name = 'Ultimate Solutions'
            seller_len = len(saller_name)
            vat_number = '311136332100003'
            dateandtime = datetime.now( ).strftime('%Y-%m-%dT%H:%M:%SZ')
            amount = str(check_order_id.amount)
            amounts = check_order_id.amount
            get_len = len(amount)
            tax = round(int(amounts)-(int(amounts) / 1.15), 2)
            # tax = (15 * int(amounts)) / 100
            get_tax_len = len(str(tax))
            company2hex = hexaConvertFunction.string2hex(saller_name)
            fullCompany2hex = '01'+str(
                hexaConvertFunction.int2hex(seller_len))+company2hex
            vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
            fullnumber2hex = '020F'+vatnumber2hex
            datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
            fulldatetimehex = '0314'+datetimeInvoicehex
            amount2hexa = hexaConvertFunction.string2hex(amount)
            fulamount2hexa = '040'+str(get_len)+amount2hexa
            tax2hexa = hexaConvertFunction.string2hex(str(tax))
            fulltax2hexa = '050'+str(get_tax_len)+tax2hexa
            get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
            print('hexa code :>>>>>>>>>>>>>>>',fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
            print('base64 code >>>>>>>>>>>>>>', get_qr_base64)
            check_order_id.qr_code_base64 = get_qr_base64
            db.session.commit( )
            get_logger_function('/get_transaction', 'info',
                                'invoice (QR) created successfully for>>>>'+database_fullname,
                                'cashier me site')
            get_logger_function('/get_transaction', 'info',
                                'success add data in company_information table in database >>>>'+database_fullname,
                                'cashier me site')
            message = gettext(
                'The process has been completed successfully. Please check your email for registration information. ')
            return render_template('enterprise_payment_result.html',
                                   get_url=SECURE_KEYS.DASHBOARD_URL + database_fullname,
                                   message_sucssess=message,
                                   name=name,
                                   address=check_order_id.street,
                                   city=check_order_id.city,
                                   country=check_order_id.Country,
                                   zip=check_order_id.postcode,
                                   package=check_order_id.stores_number,
                                   company=check_order_id.business_name,
                                   domain=SECURE_KEYS.DASHBOARD_URL + database_fullname,
                                   subscription=check_order_id.sub_type,
                                   expire=check_order_id.expire_db,
                                   price=check_order_id.amount,
                                   invoice_num=str(check_order_id.order_id),
                                   invoice_date=datetime.now( ),
                                   img_data=get_qr_base64,
                                   email=check_order_id.email,
                                   password=check_order_id.password
                                   ), cleanup(db.session)
        pass
    except Exception as error:
        print(error)
        return('/')
        pass
    return ('/')


#calling this function by paytabs callback function
@app.route('/get_transaction', methods=['POST','GET'])
def get_tran_ref():
    '''very import function its return and calling by payment getway  *paytabs*
    1- get api and check data
    2- check transaction ref from api and search this to order table if exist or Not
    3-if transaction exists send api to get all transaction information
    4-if status == A can be created database and send email and created qr code for invoice'''
    get_response_data = request.form.to_dict()
    # get_response_data = request.json
    get_logger_function('/get_transaction','info', 'get response >>>>>>'+str(get_response_data),'cashier me site')
    if get_response_data:
        get_transaction_ref = get_response_data['tranRef']
        get_transaction_token = get_response_data['token']
        if get_transaction_ref:
            get_data = Order.query.filter_by(tans_ref = get_transaction_ref).first()
            get_payment_data = Countries.query.filter_by(country_code = get_data.country_code_id).first()
            if get_data:
                data = {
                    'profile_id': str(get_payment_data.payment_merchant_id),
                    'tran_ref':str(get_data.tans_ref)
                }
            res = requests.post(str(get_payment_data.payment_query_link), data=json.dumps(data),headers = {'authorization':get_payment_data.payment_api_key,'content-type':'https://cashierme.com/get_transaction'})
            result = json.loads(res.content)
            print(result)
            get_json_transaction_ref = result.get('tran_ref')
            get_json_payment_result = result.get('payment_result')
            get_response_status = get_json_payment_result['response_status']
            get_response_message = get_json_payment_result['response_message']
            if  get_data.tans_ref == get_json_transaction_ref:
                get_logger_function('/get_transaction','info', 'get response from payment getway successfully','cashier me site')
                print('ok')
                if get_response_status == "A" and get_response_message == "Authorised":
                    get_logger_function('/get_transaction','info', 'payment successfully status "A" ','cashier me site')
                    get_name = get_data.name
                    name = get_name.replace(".", "_")
                    email = get_data.email
                    stores_number = get_data.stores_number
                    bs_name = get_data.business_name
                    company_string_name= get_data.company_string_name
                    business_name = bs_name.replace(".", "_")
                    password = get_data.password
                    password_bcrypt = get_data.password_hash
                    file_taxess = get_data.tax_file
                    commercial_register = get_data.commercial_register
                    if get_data.sub_type == 'yearly':
                        update_time = 366
                    elif get_data.sub_type == 'Monthly':
                        update_time = 31
                    else:
                        update_time = 31
                    database_create_dt = datetime.now()
                    expire_db = datetime.now()+ timedelta(update_time)
                    database_create_name = business_name.replace(" ", "")
                    random_name = random.randint(1,1000000)
                    database_fullname = str(get_data.country_code_id)+"_"+ database_create_name +'_'+str(random_name)
                    best_time_call = '10am'
                    city = get_data.city
                    country = get_data.Country
                    contact = get_data.contact
                    db_add = 'upos_' + database_fullname
                    created_from = 'From_site'
                    company_token = random.randint(1,100000000000000000)
                    data = Subscription(name, email ,stores_number, database_fullname,
                                        best_time_call, city, contact,database_create_dt,password,
                                        file_taxess,commercial_register,expire_db,database_create_dt,
                                        country,'Enterprise',get_data.street,get_data.postcode,
                                        password_bcrypt,company_string_name,created_from,company_token,"","","","")
                    db.session.add(data)
                    db.session.commit()
                    data.db_status = "pending"
                    data.order_id = get_data.id
                    data.payment_status = 'Payment Successfully'
                    data.plan_type = get_data.sub_type
                    data.price = get_data.amount
                    data.country_code_id = get_data.country_code_id
                    data.payment_getway = "paytabs"
                    data.account_type = "Live"
                    db.session.commit()
                    get_data.subscription_id = data.id
                    get_data.auto_payment_status = 'Done'
                    get_data.expire_db = expire_db
                    get_data.customer_token = get_transaction_token
                    get_data.account_type = "Live"
                    db.session.commit()
                    import mysql.connector
                    try:
                        conMysql = mysql.connector.connect(user=SECURE_KEYS.DB_USER, password=SECURE_KEYS.DB_PASSWORD, host='localhost', database=SECURE_KEYS.CONTROLLER_DB_NAME)
                        if conMysql:
                            status = 'Enterprise'
                            url = SECURE_KEYS.DASHBOARD_URL + database_fullname
                            connect = conMysql.cursor()
                            connect.execute("INSERT INTO  subscriptions (full_name,company_name,url_unique_name,"
                                            "email,db_name, url_input,status,db_create_date,stores_number,contact,"
                                            "time_call,password,password_hash,company_string_name,tax_file,commercial_register,"
                                            "check_email_time,expire_db,country,street,postcode,subscription_type,created_from,sub_table_id,company_token )"
                                            " VALUES (%s, %s, %s,%s, %s, %s, %s, %s,%s,%s,%s, %s, %s,%s, %s, %s, %s, %s,%s,%s, %s,%s,%s,%s,%s)"
                                            ,(name, business_name, database_fullname, email,database_fullname, url, status, database_create_dt,stores_number,contact ,
                                              best_time_call,password,password_bcrypt,company_string_name,file_taxess,commercial_register,
                                              database_create_dt,expire_db,country,get_data.street,get_data.postcode,get_data.sub_type,created_from,data.id,company_token ))
                            conMysql.commit()
                        else:
                            return redirect('/')
                    except Exception as error:
                        get_logger_function ('/get_transaction', 'error',
                                             'error for create in db controller' +str(error),
                                             'cashier me site')

                    saller_name = 'Ultimate Solutions'
                    seller_len = len(saller_name)
                    vat_number = '311136332100003'
                    dateandtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                    amount = str(get_data.amount)
                    amounts = get_data.amount
                    get_len = len(amount)
                    tax = round(int(amounts)-(int(amounts) / 1.15), 2)
                    # tax = (15 * int(amounts)) / 100
                    get_tax_len = len(str(tax))
                    company2hex = hexaConvertFunction.string2hex(saller_name)
                    fullCompany2hex = '01' + str(hexaConvertFunction.int2hex(seller_len)) + company2hex
                    vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
                    fullnumber2hex = '020F' + vatnumber2hex
                    datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
                    fulldatetimehex = '0314'+ datetimeInvoicehex
                    amount2hexa = hexaConvertFunction.string2hex(amount)
                    fulamount2hexa = '040'+ str(get_len) + amount2hexa
                    tax2hexa = hexaConvertFunction.string2hex(str(tax))
                    fulltax2hexa = '050' + str(get_tax_len) + tax2hexa
                    get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('hexa code :>>>>>>>>>>>>>>>',fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('base64 code >>>>>>>>>>>>>>',get_qr_base64)
                    get_data.qr_code_base64 = get_qr_base64
                    db.session.commit()
                    get_logger_function('/get_transaction','info', 'invoice (QR) created successfully for>>>>'+database_fullname,'cashier me site')
                    get_logger_function('/get_transaction','info', 'success add data in company_information table in database >>>>'+database_fullname,'cashier me site')
                    message = gettext('The process has been completed successfully. Please check your email for registration information. ')
                    return render_template('enterprise_payment_result.html'
                                           , get_url =SECURE_KEYS.DASHBOARD_URL + database_fullname,
                                           message_sucssess = message,
                                           name = name,
                                           address = get_data.street,
                                           city = get_data.city,
                                           country = get_data.Country,
                                           zip = get_data.postcode,
                                           package = get_data.stores_number,
                                           company = get_data.business_name,
                                           domain =SECURE_KEYS.DASHBOARD_URL + database_fullname,
                                           subscription = get_data.sub_type,
                                           expire = get_data.expire_db,
                                           price = get_data.amount,
                                           invoice_num = str(get_data.order_id ),
                                           invoice_date = datetime.now(),
                                           img_data=get_qr_base64,
                                           email = get_data.email,
                                           password = get_data.password
                                           ),cleanup(db.session)

                else:
                    get_logger_function('/get_transaction','info', '"The process cannot be completed, please try another payment card if you want to back pricing page','cashier me site')
                    message_error = gettext("The process cannot be completed, please try another payment card if you want to back pricing page")
                    return render_template('enterprise_payment_result.html', get_url='https://cashierme.com/pricing',message_error = message_error ),cleanup(db.session)
            else:
                get_logger_function('/get_transaction','error', 'get response from payment getway error please check url and param to fixed issues','cashier me site')
                return redirect('/'),cleanup(db.session)
        else:
            get_logger_function('/get_transaction','error', 'get tran_ref error it none value','cashier me site')
            return redirect('/'),cleanup(db.session)
    else:
        get_logger_function('/get_transaction','error', 'get tran_ref error it none value check response fro api','cashier me site')
        return redirect('/'),cleanup(db.session)


@app.route('/about_us')
@check_coutry
def about_us():
    return render_template('about_page.html',active_page='about_us')

@app.route('/terms_conditions')
@check_coutry
def terms_conditions():
    return render_template('terms_conditions.html',active_page='terms_conditions')


@app.route('/privacy_policy')
@check_coutry
def privacy_policy():
    return render_template('privacy_ policy.html',active_page='privacy_policy')

@app.route('/return_policy')
@check_coutry
def return_policy():
    return render_template('return_policy.html',active_page='return_policy')

@app.route('/samer')
@check_coutry
def testtststst():
    return render_template('enterprise_payment_result.html',active_page='samer')

@app.route('/forget_password_email')
@check_coutry
def forget_password_email():
    return render_template('sendEmail_forgetPassword.html',active_page='forget_password_email')

#>>>>>>>>>>>>>>>>>>>  create token and send it to email if email exists <<<<<<<
@app.route('/checkEmail_forgetPassword', methods=['POST'])
def checkEmail_forgetPassword():
    email = request.form['email']
    check_email = Subscription.query.filter_by(email = email).first()
    if check_email:
        random_code = random.randint(1,1000000000000)
        data = jwt.encode({
            'email': email,
            'code': random_code
        },app.config['SECRET_KEY'],algorithm="HS256")
        token_code = data
        check_email.random_code = random_code
        db.session.commit()
        expire_time = datetime.now()+timedelta(minutes=4)
        status = 'active'
        customer_id = check_email.id
        tem_token = TemporaryTokens(email,customer_id,token_code,random_code,expire_time,status)
        db.session.add(tem_token)
        db.session.commit()
        try:
            with app.test_request_context():
                if check_email.country_code_id == "TUR":
                    smtp = 2
                    message = "şifreyi değiştirmek için lütfen"
                    subject = "şifre değiştir"
                else:
                    message = "To change password please"
                    subject = "Change Password"

                smtp = 1
                select_mail_config = smtp_config(SECURE_KEYS.MAIL_CONFIG, smtp=smtp)
                app.config.update(dict(
                    MAIL_SERVER=select_mail_config[2],
                    MAIL_PORT=select_mail_config[3],
                    MAIL_USERNAME=select_mail_config[0],
                    MAIL_PASSWORD=select_mail_config[1],
                ))
                mail.init_app(app)
                msg = Message(recipients=[email], sender=select_mail_config[0],subject=subject)
                links = SECURE_KEYS.CALL_BACK_URL + '/token/{}'.format(token_code)
                msg.body = 'To Change Password Please click this link' + links
                msg.html = render_template('reset_password_mail.html', links=links, message = message)
                mail.send(msg)
        except Exception as error:
            get_logger_function('/checkEmail_forgetPassword','error', str(error),'cashier me site')
            pass
        message_success =gettext("Please Check your email to change password you have ")
        get_logger_function('/checkEmail_forgetPassword','info', 'success send code for change password by token to emai>>>'+str(email),'cashier me site')
        return render_template('sendEmail_forgetPassword.html',message_success = message_success),cleanup(db.session)
    else:
        flash(gettext("invalid email !!!!"))
        get_logger_function('/checkEmail_forgetPassword','info', 'invalid email for cheange password email is >>>'+str(email),'cashier me site')
        return redirect('/forget_password_email'),cleanup(db.session)


#>>>>>>>>>>>>>>>>>>>> check token expire or active to redirect change password<<<<<<<<<<<
@app.route('/token/<string:token>',methods=['GET', 'POST'] )
def get_token_auth(token):
    data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
    email = data.get('email')
    code = data.get('code')
    check_time = datetime.now()
    get_data = TemporaryTokens.query.filter_by(active_code = code).first()
    if get_data:
        if get_data.email == email and check_time < get_data.expiration and get_data.status == 'active' :
            get_data.status = 'used'
            db.session.commit()
            get_logger_function('/token/{gettoken}','info', 'success check token is active','cashier me site')
            return render_template('reset_password.html',customer_code = get_data.subscription_id, code = code ),cleanup(db.session)
        else:
            get_data.status = 'expired'
            db.session.commit()
            get_logger_function('/token/{gettoken}','info', 'token expire to change password','cashier me site')
            flash(gettext("Your Token is Expired Please Try again !!!!!"))
            return redirect('/forget_password_email'),cleanup(db.session)
    else:
        return redirect('/login'),cleanup(db.session)


#>>>>>>>>>>>>>>>>>> submit change password <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
@app.route('/submit_reset_password', methods=['POST','GET'])
@check_coutry
def submit_reset_password():
    try:
        code = request.form['code']
        customer_code = request.form['customer_code']
        new_password = request.form['new_password']
        retry_password = request.form['retry_password']
        check_id = Subscription.query.get_or_404(customer_code)
        print(customer_code)
        if check_id:
            if check_id.random_code == code:
                if new_password == retry_password:
                    check_id.password = new_password
                    check_id.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
                    db.session.commit()
                    try:
                        if check_id.order_id:
                            check_order_data = Order.query.filter_by(id = check_id.order_id).first()
                            check_order_data.password = new_password
                            check_order_data.password_hash =bcrypt.generate_password_hash(new_password).decode("utf-8")
                            db.session.commit()
                    except:
                        pass
                    check_id.random_code = random.randint(1,1000000000000000000000000000)
                    db.session.commit()
                    get_logger_function('submit_reset_password','info', 'successfully change password to >>>>>>'+new_password,'cashier me site')
                    return render_template('login.html'),cleanup(db.session)
                else:
                    flash(gettext("Password not Matched"))
                    return render_template('reset_password.html',customer_code = check_id.id, code = code),cleanup(db.session)
            else:
                flash(gettext("invalid Code !!!!!"))
                get_logger_function('submit_reset_password','info', 'invalid code!!!!!!','cashier me site')
                return render_template('reset_password.html',customer_code = check_id.id),cleanup(db.session)
        else:
            return redirect('/login')
    except Exception as Error:
        print(Error)
        get_logger_function('submit_reset_password','info', 'error>>'+str(Error),'cashier me site')
    return redirect('/login')


@app.route('/login')
def login():
    if "email" in session:
        return redirect('/dashboard')
    else:
        account_cookies = request.cookies.get('get_cookies_account')
        return render_template('login.html',account_cookies = account_cookies, active_page='login')


@app.route('/submit_login', methods=['POST'])
@check_coutry
def submit_login():
    email = request.form['email']
    password = request.form['password']
    check_account = Subscription.query.filter_by(email= email).first()
    if check_account and bcrypt.check_password_hash(check_account.password_hash, password) and check_account_status.check_account_status(check_account.subscription_status, check_account.expire_db) :
          login_user(check_account)
          session['email'] = email
          resp = make_response(redirect('/invoices'))
          if request.form.get('check_cookies'):
              resp.set_cookie('get_cookies_account', email, max_age=COOKIE_TIME_OUT)
          get_logger_function('submit_login','info', 'successfully login from email >>>> '+email,'cashier me site')
          return resp
    else:
        flash(gettext("Invalid Email Or Password"))
        get_logger_function('submit_login','info', 'invalid>>>'+email+'<<<< or password to login','cashier me site')
        return redirect('/login')


# @app.route('/submit_login_subscription', methods=['POST'])
def submit_login_subscription(email, password):
    email = email
    password = password
    check_account = Subscription.query.filter_by(email= email).first()
    if check_account and bcrypt.check_password_hash(check_account.password_hash, password):
        login_user(check_account)
        session['email'] = email
        resp = make_response(redirect('/dashboard'))
        if request.form.get('check_cookies'):
            resp.set_cookie('get_cookies_account', email, max_age=COOKIE_TIME_OUT)
        get_logger_function('submit_login','info', 'successfully login from email >>>> '+email,'cashier me site')
        return resp
    else:
        flash(gettext("Invalid Email Or Password"))
        get_logger_function('submit_login','info', 'invalid>>>'+email+'<<<< or password to login','cashier me site')
        return redirect('/login')


@app.route('/logout')
def logout():
    logout_user()
    if 'email' in session:
        session.pop('email', None)
    return redirect('/login')


@app.route('/dashboard')
@login_required
@check_coutry
def dashboard():
    get_id = current_user.id
    get_dashboard_data = Subscription.query.filter_by(id= get_id).first()
    name = get_dashboard_data.name
    email = get_dashboard_data.email
    url = SECURE_KEYS.DASHBOARD_URL + get_dashboard_data.business_name
    package = get_dashboard_data.stores_number
    get_time = get_dashboard_data.expire_db
    calculation_time = get_time - datetime.now()
    month = 0
    print(calculation_time.days)
    return render_template('dashboard.html',name=name, email=email,url = url,package=package ,get_days =calculation_time.days, get_month=month,expire_date =get_time.strftime("%b %d %Y") ,active_page='dashboard' ),cleanup(db.session)


@app.route('/profile')
@login_required
@check_coutry
def profile():
    get_profile_data = Subscription.query.filter_by(id=current_user.id).first()
    name = get_profile_data.name
    email = get_profile_data.email
    tax_number = get_profile_data.tax_file
    commercial_register = get_profile_data.commercial_register
    phone = get_profile_data.contact
    country = get_profile_data.Country
    city = get_profile_data.city
    best_time_call = get_profile_data.best_time_call
    street = get_profile_data.street
    postcode = get_profile_data.postcode
    return render_template('profile.html',name=name,
                                          email=email,
                                          phone=phone,
                                          city=city,
                                          best_time_call=best_time_call,
                                          street = street,
                                          postcode = postcode,
                                          country=country,active_page='profile'),cleanup(db.session,)


@app.route('/profile_submit', methods=['POST'])
@login_required
@check_coutry
def profile_submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    country = request.form['country']
    city = request.form['city']
    street = request.form['street']
    postcode = request.form['postcode']
    best_time_call = request.form['best_time_call']
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    retry_password = request.form['retry_password']
    get_id = current_user.id
    update_data = Subscription.query.filter_by(id = get_id).first()
    if update_data:
        update_data.name = name
        # update_data.email = email
        # update_data.contact = phone
        update_data.Country = country
        update_data.city = city
        update_data.street = street
        update_data.postcode = postcode
        update_data.best_time_call = best_time_call
        db.session.commit()
        get_logger_function('profile_submit','info', 'successfully update profile from user'+name+'--'+email,'cashier me site')
        if old_password and new_password and retry_password:
            if bcrypt.check_password_hash(update_data.password_hash, old_password):
                if new_password ==retry_password:
                    update_data.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
                    update_data.password = new_password
                    db.session.commit()
                    get_logger_function('profile_submit','info', 'successfully change password from email >>>>'+email,'cashier me site')
                    return redirect('/logout'),cleanup(db.session)
                else:
                    flash(gettext("password not Matched"))
                    get_logger_function('profile_submit','info', 'password not matched from email >>>>'+email,'cashier me site')
                    return redirect('/profile'),cleanup(db.session)
            else:
                flash(gettext("Invalid Old Password"))
                get_logger_function('profile_submit','info', 'invalid old password from email >>>>'+email,'cashier me site')
                return redirect('/profile'),cleanup(db.session)
        else:
            get_logger_function('profile_submit','info', 'error for current user not exists','cashier me site')
            return redirect('/profile'),cleanup(db.session)

@app.route('/GetCompanyInfo', methods=['POST'])
def get_company_token():
    get_post_data = request.json
    data_convert = get_post_data['c_token']
    if data_convert:
        check_data = Subscription.query.filter_by(company_token = str(data_convert)).first()
        if check_data:
            data = {
                'name': check_data.name,
                'email': check_data.email,
                'pos_no': check_data.stores_number,
                'business_name': check_data.business_name,
                'city': check_data.city,
                'contact': check_data.contact,
                'db_created_date': str(check_data.db_create_date),
                'tax_file':check_data.tax_file,
                'commercial_register':check_data.commercial_register,
                'expire_db': str(check_data.expire_db),
                'country': check_data.Country,
                'subscription_type': check_data.subscription_type,
                'payment_status': check_data.payment_status,
                'street': check_data.street,
                'postcode':check_data.postcode,
                'company_string_name': check_data.company_string_name,
                'is_active':check_data.is_active,
                "status": check_account_status.check_account_status_for_company_api(check_data.subscription_status, check_data.expire_db)

            }
            get_logger_function('GetCompanyInfo','info', 'success check '+ data_convert,'cashier me site')
            return jsonify({'c_token':data}),cleanup(db.session)
        else:
            get_logger_function('GetCompanyInfo','info', data_convert+'this token invalid' ,'cashier me site')
            return jsonify({'error':'Request must be made using POST'}),cleanup(db.session)

@app.route('/invoices')
@app.route('/invoices/')
def invoices():
    try:
        if current_user.is_authenticated:
            get_id = current_user.id
            get_invoices_data = Subscription.query.filter_by(id = get_id).first()
            get_invoices = Order.query.filter(and_(Order.subscription_id == get_invoices_data.id, Order.account_type != "Test")).all()
            get_dashboard_data = Subscription.query.filter_by(id= get_id).first()
            package = get_dashboard_data.stores_number
            get_time = get_dashboard_data.expire_db
            get_order_id = current_user.order_id
            get_invoices_notification = Order.query.filter_by(id = get_order_id).first()
            get_one_pos_price = Countries.query.filter_by(country_code = get_dashboard_data.country_code_id).first()
            monthly_price = get_one_pos_price.monthly_amount
            annually_price = get_one_pos_price.annually_amount
            notification_no = 0
            if current_user.subscription_type == "Enterprise":
                if get_invoices_data.plan_type != get_invoices_notification.sub_type_toUpdate and get_invoices_notification.sub_type_toUpdate != None :
                    data = True
                    notification_no +=1
                else:
                    data = False
                print(data)
                if get_invoices_data.plan_type == get_invoices_notification.sub_type_toUpdate and get_invoices_data.stores_number != get_invoices_notification.pos_no_toUpdate:
                    remove_pos = True
                    notification_no +=1
                else:
                    remove_pos = False
                print(remove_pos)
                calculation_time = get_time - datetime.now()
                month = 0
                get_package_toupgrade_monthly = Packages.query.filter(and_(Packages.type == 'Monthly',Packages.pos_no >  int(current_user.stores_number),Packages.country_code == session['country_code'] )).all()
                get_package_toupgrade_annualy = Packages.query.filter(and_(Packages.type == 'yearly',Packages.pos_no >  int(current_user.stores_number),Packages.country_code == session['country_code'] )).all()
                get_package_removePOS_monthly = Packages.query.filter(and_(Packages.type == 'Monthly', Packages.pos_no < int(current_user.stores_number)-1, Packages.country_code == session['country_code'])).all()
                get_package_removePOS_annualy = Packages.query.filter(and_(Packages.type == 'yearly', Packages.pos_no < int(current_user.stores_number)-1,Packages.country_code == session['country_code'])).all()
                get_all_pos_no_monthly = Packages.query.filter(and_(Packages.type == 'Monthly',Packages.country_code == session['country_code'])).all()
                get_all_pos_no_yearly = Packages.query.filter(and_(Packages.type == 'yearly',Packages.country_code == session['country_code'])).all()
                return render_template('invoices.html',get_invoice_data=get_invoices,package=package ,
                                       get_days =calculation_time.days, get_month=month,
                                       expire_date =get_time.strftime("%b %d %Y"), data = data,
                                       remove_pos = remove_pos, notification_no = notification_no,
                                       get_package_toupgrade_monthly = get_package_toupgrade_monthly,
                                       get_package_removePOS_monthly = get_package_removePOS_monthly,
                                       get_package_toupgrade_annualy=get_package_toupgrade_annualy,
                                       get_package_removePOS_annualy=get_package_removePOS_annualy,
                                       get_all_pos_no_monthly = get_all_pos_no_monthly,
                                       get_all_pos_no_yearly = get_all_pos_no_yearly,
                                       monthly_price = monthly_price,
                                       annually_price = annually_price,active_page='invoices'
                                       ),cleanup(db.session)
            else:
                month = 0
                calculation_time = get_time - datetime.now()
                return render_template('invoices.html',get_invoice_data=get_invoices,package=package ,
                                       get_days =calculation_time.days, get_month=month,
                                       expire_date =get_time.strftime("%b %d %Y"),active_page='invoices'),cleanup(db.session)
        else:
            get_data = request.args.get('ct')
            check_data = Subscription.query.filter_by(company_token = get_data).first()
            if check_data:
                session['country_code'] = check_data.country_code_id
                login_user(check_data)
                return redirect('/invoices')

            else:
                return redirect('/login')
    except Exception as Error:
        get_logger_function('invoices','error', 'Error in invoices page the error is '+ str(Error),'cashier me site')
        print(Error)
        return redirect('/login')



# @app.route('/invoices')
# @login_required
# @check_coutry
# def invoices():
#     get_id = current_user.id
#     get_invoices_data = Subscription.query.filter_by(id = get_id).first()
#     get_invoices = Order.query.filter(and_(Order.subscription_id == get_invoices_data.id, Order.account_type != "Test")).all()
#     get_dashboard_data = Subscription.query.filter_by(id= get_id).first()
#     package = get_dashboard_data.stores_number
#     get_time = get_dashboard_data.expire_db
#     get_order_id = current_user.order_id
#     get_invoices_notification = Order.query.filter_by(id = get_order_id).first()
#     get_one_pos_price = Countries.query.filter_by(country_code = get_dashboard_data.country_code_id).first()
#     monthly_price = get_one_pos_price.monthly_amount
#     annually_price = get_one_pos_price.annually_amount
#     notification_no = 0
#     if current_user.subscription_type == "Enterprise":
#         if get_invoices_data.plan_type != get_invoices_notification.sub_type_toUpdate and get_invoices_notification.sub_type_toUpdate != None :
#             data = True
#             notification_no +=1
#         else:
#             data = False
#         print(data)
#         if get_invoices_data.plan_type == get_invoices_notification.sub_type_toUpdate and get_invoices_data.stores_number != get_invoices_notification.pos_no_toUpdate:
#             remove_pos = True
#             notification_no +=1
#         else:
#             remove_pos = False
#         print(remove_pos)
#         calculation_time = get_time - datetime.now()
#         month = 0
#         get_package_toupgrade_monthly = Packages.query.filter(and_(Packages.type == 'Monthly',Packages.pos_no >  int(current_user.stores_number),Packages.country_code == session['country_code'] )).all()
#         get_package_toupgrade_annualy = Packages.query.filter(and_(Packages.type == 'yearly',Packages.pos_no >  int(current_user.stores_number),Packages.country_code == session['country_code'] )).all()
#         get_package_removePOS_monthly = Packages.query.filter(and_(Packages.type == 'Monthly', Packages.pos_no < int(current_user.stores_number)-1, Packages.country_code == session['country_code'])).all()
#         get_package_removePOS_annualy = Packages.query.filter(and_(Packages.type == 'yearly', Packages.pos_no < int(current_user.stores_number)-1,Packages.country_code == session['country_code'])).all()
#         get_all_pos_no_monthly = Packages.query.filter(and_(Packages.type == 'Monthly',Packages.country_code == session['country_code'])).all()
#         get_all_pos_no_yearly = Packages.query.filter(and_(Packages.type == 'yearly',Packages.country_code == session['country_code'])).all()
#         return render_template('invoices.html',get_invoice_data=get_invoices,package=package ,
#                                get_days =calculation_time.days, get_month=month,
#                                expire_date =get_time.strftime("%b %d %Y"), data = data,
#                                remove_pos = remove_pos, notification_no = notification_no,
#                                get_package_toupgrade_monthly = get_package_toupgrade_monthly,
#                                get_package_removePOS_monthly = get_package_removePOS_monthly,
#                                get_package_toupgrade_annualy=get_package_toupgrade_annualy,
#                                get_package_removePOS_annualy=get_package_removePOS_annualy,
#                                get_all_pos_no_monthly = get_all_pos_no_monthly,
#                                get_all_pos_no_yearly = get_all_pos_no_yearly,
#                                monthly_price = monthly_price,
#                                annually_price = annually_price,active_page='invoices'
#                                ),cleanup(db.session)
#     else:
#         month = 0
#         calculation_time = get_time - datetime.now()
#         return render_template('invoices.html',get_invoice_data=get_invoices,package=package ,
#                                    get_days =calculation_time.days, get_month=month,
#                                    expire_date =get_time.strftime("%b %d %Y"),active_page='invoices'),cleanup(db.session)

# cancel subscription Annualy
@app.route('/cancel_subscription_annualy', methods=['POST'])
@check_coutry
def cancel_subscription_annualy():
    get_user_id = current_user.order_id
    check_order = Order.query.filter_by(id = get_user_id).first()
    try:
        check_order.sub_type_toUpdate = current_user.plan_type
        check_order.pos_no_toUpdate = current_user.stores_number
        check_order.price_toUpdate = current_user.price
        db.session.commit()
        return "ok"
    except Exception as error:
        print(error)
        return redirect('/invoices')



@app.route('/run_payment_sa1831992', methods=['POST', 'GET'])
def run_payment_manual():
    get_payment_data = Countries.query.filter_by(country_code = "SAU").first()
    data = {
        'profile_id':str(85045),
        'tran_ref':str('PTS2310224001938')
    }
    res = requests.post(str(get_payment_data.payment_query_link), data=json.dumps(data),headers = {'authorization':str(get_payment_data.payment_api_key),'content-type':'https://cashierme.com/getResponseForUpgrade_subscription'})
    result = json.loads(res.content)

    print(result)
    return result
    # check_payment = check_payment_update()
    # return str(check_payment)

@app.route('/update_subscription_form_user_dashboard', methods=['POST', 'GET'])
def update_subscription_form_user_dashboard():
    try:
        get_user_id = current_user.order_id
        data = Order.query.filter_by(id = get_user_id).first()
        if data.auto_payment_status != 'payment_last':
            data.auto_payment_status = 'payment_last'
            db.session.commit()
            transaction_ref = data.tans_ref
            customer_token = data.customer_token
            if data.price_toUpdate:
                amount = data.price_toUpdate
            else:
                amount = data.amount
            random_code1 = random.randint(1, 100000)
            random_code2 = random.randint(1, 100000)
            order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
            get_payment_data = Countries.query.filter_by(country_code = data.country_code_id).first()

            payment_request = {
                "profile_id":str(get_payment_data.payment_merchant_id) ,
                "tran_type":"sale" ,
                "tran_class":"recurring" ,
                "cart_id": str(order_code) ,
                "cart_currency":str(get_payment_data.payment_currency) ,
                "cart_amount":str(amount) ,
                "cart_description":"test for toffffken customer" ,
                "token": str(customer_token) ,
                "tran_ref":str(transaction_ref)
            }
            response = requests.post(str(get_payment_data.payment_request_api_url), data = json.dumps(payment_request), headers = {'authorization':str(get_payment_data.payment_api_key),'content-type':'application/json'})
            if response :
                get_logger_function('check_payment_update','info', 'check data and expiration date and send request to paytabs  is successfully' ,'cashier me site')
                result = json.loads(response.content)
                print(result)
                get_json_transaction_ref = result.get('tran_ref')
                get_json_payment_result = result.get('payment_result')
                get_response_status = get_json_payment_result['response_status']
                get_response_message = get_json_payment_result['response_message']
                print(get_json_transaction_ref,get_json_payment_result)
                if data.sub_type_toUpdate == 'yearly':
                    update_time = 366
                if data.sub_type_toUpdate is None and data.sub_type == 'yearly':
                    update_time = 366
                if data.sub_type_toUpdate == 'Monthly':
                    update_time = 31
                if data.sub_type_toUpdate is None and  data.sub_type == 'Monthly':
                    update_time = 31
                if get_response_status == 'A' and get_response_message == "Authorised":
                    if data.sub_type_toUpdate:
                        add_subtype = data.sub_type_toUpdate
                    else:
                        add_subtype = data.sub_type
                    if data.price_toUpdate:
                        add_price = data.price_toUpdate
                    else:
                        add_price = data.amount
                    if data.pos_no_toUpdate:
                        add_pos_no = data.pos_no_toUpdate
                    else:
                        add_pos_no = data.stores_number
                    order_data = Order(data.name, data.email,add_pos_no , data.business_name, data.city, data.contact ,data.password, data.tax_file, data.commercial_register, datetime.now(),data.street,data.Country,data.postcode,'Done',order_code,add_price,add_subtype
                                       ,datetime.now()+ timedelta(update_time),data.password_hash,data.package_id,data.company_string_name)
                    db.session.add(order_data)
                    db.session.commit()
                    order_data.order_id = order_data.id
                    order_data.tans_ref = get_json_transaction_ref
                    order_data.subscription_id = data.subscription_id
                    order_data.auto_payment_status = 'Done'
                    order_data.country_code_id = data.country_code_id
                    order_data.expire_db = datetime.now()+ timedelta(update_time)
                    order_data.customer_token = customer_token
                    order_data.account_type = "Live"
                    db.session.commit()
                    data.auto_payment_status = 'payment_last'
                    db.session.commit( )
                    sub_data = Subscription.query.filter_by(id = data.subscription_id).first()
                    sub_data.order_id = order_data.id
                    sub_data.stores_number = order_data.stores_number
                    sub_data.plan_type = order_data.sub_type
                    sub_data.price = order_data.amount
                    sub_data.expire_db = datetime.now()+ timedelta(update_time)
                    sub_data.payment_status = 'Payment Successfully'
                    sub_data.account_type = "Live"
                    db.session.commit()
                    try:
                        saller_name = 'Ultimate Solutions'
                        seller_len = len(saller_name)
                        vat_number = '311136332100003'
                        dateandtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                        amount = str(order_data.amount)
                        amounts = order_data.amount
                        get_len = len(amount)
                        tax = round(int(amounts)-(int(amounts) / 1.15), 2)
                        # tax = (15 * int(amounts)) / 100
                        get_tax_len = len(str(tax))
                        company2hex = hexaConvertFunction.string2hex(saller_name)
                        fullCompany2hex = '01' + str(hexaConvertFunction.int2hex(seller_len)) + company2hex
                        vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
                        fullnumber2hex = '020F' + vatnumber2hex
                        datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
                        fulldatetimehex = '0314'+ datetimeInvoicehex
                        amount2hexa = hexaConvertFunction.string2hex(amount)
                        fulamount2hexa = '040'+ str(get_len) + amount2hexa
                        tax2hexa = hexaConvertFunction.string2hex(str(tax))
                        fulltax2hexa = '050' + str(get_tax_len) + tax2hexa
                        get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                        print('hexa code :>>>>>>>>>>>>>>>',fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                        print('base64 code >>>>>>>>>>>>>>',get_qr_base64)
                        order_data.qr_code_base64 = get_qr_base64
                        db.session.commit()
                        get_logger_function('/check_payment_update','info', 'invoice (QR) created successfully for>>>>'+order_data.business_name,'cashier me site')
                    except Exception as error:
                        get_logger_function('/check_payment_update','error', str(error),'cashier me site')
                        print(error)
                        pass
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Payment Successful")
                    get_logger_function('check_payment_update','info', 'update payment is successfully created the tran_ref is>>>'+ str(get_json_transaction_ref) +'and order table id is >>> '+str(order_data.id) ,'cashier me site')
                    return {"status": "success", "msg":str("success payment") ,"order_id": order_data.id }
                else:
                    order_data = Order(data.name, data.email, data.stores_number, data.business_name, data.city, data.contact ,data.password, data.tax_file, data.commercial_register, datetime.now(),data.street,data.Country,data.postcode,'Failed',order_code,data.amount,data.sub_type,datetime.now(),data.password_hash,data.package_id,data.company_string_name)
                    db.session.add(order_data)
                    db.session.commit()
                    order_data.order_id = order_data.id
                    order_data.tans_ref = get_json_transaction_ref
                    order_data.subscription_id = data.subscription_id
                    order_data.customer_token = data.customer_token
                    order_data.auto_payment_status = 'Failed'
                    order_data.country_code_id = data.country_code_id
                    db.session.commit()
                    sub_data = Subscription.query.filter_by(id = data.subscription_id).first()
                    sub_data.order_id = order_data.id
                    sub_data.expire_db = datetime.now()
                    sub_data.plan_type = data.sub_type
                    sub_data.price = data.amount
                    sub_data.payment_status = 'Payment Failed'
                    db.session.commit()
                    get_logger_function('check_payment_update','info', 'update payment is failed created the tran_ref is>>>'+ str(get_json_transaction_ref) +'and order table id is >>> '+str(order_data.id) ,'cashier me site')
                    return {"status": "invalid", "msg":str(get_response_message),"order_id": "" }
            else:
                data.auto_payment_status = 'invalid_process'
                db.session.commit()
                get_logger_function('check_payment_update','error', 'error for send request to paytabs the tran_ref is >>> '+str(transaction_ref),'cashier me site')
                return {"status": "error", "msg":str('cannot process your request please contact with us ') }

    except Exception as Error:
        print(Error)
        get_logger_function('check_payment_update', 'error','error in check payment upgrade scheduler function please check this and the error is >>>>>'+str(Error),'cashier me site')
        return {"status": "error", "msg":str(Error), "date": str(datetime.now()) }



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> automatic Payment Scheduler >>>>>>>>>>>>>>>>>>
@scheduler.task('interval', id='do_jo125222',seconds=84400)
def check_payment_update():
    try:
        print("start job")
        get_data = Order.query.filter(and_(Order.expire_db < datetime.now(), Order.auto_payment_status != 'Failed',Order.auto_payment_status != 'invalid_process', Order.auto_payment_status != 'Canceled',Order.auto_payment_status != 'payment_last')).all()
        for data in get_data:
            if data.auto_payment_status != 'payment_last':
                data.auto_payment_status = 'payment_last'
                db.session.commit()
                transaction_ref = data.tans_ref
                customer_token = data.customer_token
                if data.price_toUpdate:
                    amount = data.price_toUpdate
                else:
                    amount = data.amount
                random_code1 = random.randint(1, 100000)
                random_code2 = random.randint(1, 100000)
                order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
                get_payment_data = Countries.query.filter_by(country_code = data.country_code_id).first()
                payment_request = {
                    "profile_id":str(get_payment_data.payment_merchant_id) ,
                    "tran_type":"sale" ,
                    "tran_class":"recurring" ,
                    "cart_id": str(order_code) ,
                    "cart_currency":str(get_payment_data.payment_currency) ,
                    "cart_amount":str(amount) ,
                    "cart_description":"test for toffffken customer" ,
                    "token": str(customer_token) ,
                    "tran_ref":str(transaction_ref)
                }
                response = requests.post(str(get_payment_data.payment_request_api_url), data = json.dumps(payment_request), headers = {'authorization':str(get_payment_data.payment_api_key),'content-type':'application/json'})
                if response :
                    get_logger_function('check_payment_update','info', 'check data and expiration date and send request to paytabs  is successfully' ,'cashier me site')
                    result = json.loads(response.content)
                    print(result)
                    get_json_transaction_ref = result.get('tran_ref')
                    get_json_payment_result = result.get('payment_result')
                    get_response_status = get_json_payment_result['response_status']
                    get_response_message = get_json_payment_result['response_message']
                    print(get_json_transaction_ref,get_json_payment_result)
                    if data.sub_type_toUpdate == 'yearly':
                        update_time = 366
                    if data.sub_type_toUpdate is None and data.sub_type == 'yearly':
                        update_time = 366
                    if data.sub_type_toUpdate == 'Monthly':
                        update_time = 31
                    if data.sub_type_toUpdate is None and  data.sub_type == 'Monthly':
                        update_time = 31
                    if get_response_status == 'A' and get_response_message == "Authorised":
                        if data.sub_type_toUpdate:
                            add_subtype = data.sub_type_toUpdate
                        else:
                            add_subtype = data.sub_type
                        if data.price_toUpdate:
                            add_price = data.price_toUpdate
                        else:
                            add_price = data.amount
                        if data.pos_no_toUpdate:
                            add_pos_no = data.pos_no_toUpdate
                        else:
                            add_pos_no = data.stores_number
                        order_data = Order(data.name, data.email,add_pos_no , data.business_name, data.city, data.contact ,data.password, data.tax_file, data.commercial_register, datetime.now(),data.street,data.Country,data.postcode,'Done',order_code,add_price,add_subtype
                                           ,datetime.now()+ timedelta(update_time),data.password_hash,data.package_id,data.company_string_name)
                        db.session.add(order_data)
                        db.session.commit()
                        order_data.order_id = order_data.id
                        order_data.tans_ref = get_json_transaction_ref
                        order_data.subscription_id = data.subscription_id
                        order_data.auto_payment_status = 'Done'
                        order_data.country_code_id = data.country_code_id
                        order_data.expire_db = datetime.now()+ timedelta(update_time)
                        order_data.customer_token = customer_token
                        order_data.account_type = "Live"
                        db.session.commit()
                        data.auto_payment_status = 'payment_last'
                        db.session.commit( )
                        sub_data = Subscription.query.filter_by(id = data.subscription_id).first()
                        sub_data.order_id = order_data.id
                        sub_data.stores_number = order_data.stores_number
                        sub_data.plan_type = order_data.sub_type
                        sub_data.price = order_data.amount
                        sub_data.expire_db = datetime.now()+ timedelta(update_time)
                        sub_data.payment_status = 'Payment Successfully'
                        sub_data.account_type = "Live"
                        db.session.commit()
                        try:
                            saller_name = 'Ultimate Solutions'
                            seller_len = len(saller_name)
                            vat_number = '311136332100003'
                            dateandtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                            amount = str(order_data.amount)
                            amounts = order_data.amount
                            get_len = len(amount)
                            tax = round(int(amounts)-(int(amounts) / 1.15), 2)
                            # tax = (15 * int(amounts)) / 100
                            get_tax_len = len(str(tax))
                            company2hex = hexaConvertFunction.string2hex(saller_name)
                            fullCompany2hex = '01' + str(hexaConvertFunction.int2hex(seller_len)) + company2hex
                            vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
                            fullnumber2hex = '020F' + vatnumber2hex
                            datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
                            fulldatetimehex = '0314'+ datetimeInvoicehex
                            amount2hexa = hexaConvertFunction.string2hex(amount)
                            fulamount2hexa = '040'+ str(get_len) + amount2hexa
                            tax2hexa = hexaConvertFunction.string2hex(str(tax))
                            fulltax2hexa = '050' + str(get_tax_len) + tax2hexa
                            get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                            print('hexa code :>>>>>>>>>>>>>>>',fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                            print('base64 code >>>>>>>>>>>>>>',get_qr_base64)
                            order_data.qr_code_base64 = get_qr_base64
                            db.session.commit()
                            get_logger_function('/check_payment_update','info', 'invoice (QR) created successfully for>>>>'+order_data.business_name,'cashier me site')
                        except Exception as error:
                                get_logger_function('/check_payment_update','error', str(error),'cashier me site')
                                print(error)
                                pass
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Payment Successful")
                        get_logger_function('check_payment_update','info', 'update payment is successfully created the tran_ref is>>>'+ str(get_json_transaction_ref) +'and order table id is >>> '+str(order_data.id) ,'cashier me site')
                    else:
                        order_data = Order(data.name, data.email, data.stores_number, data.business_name, data.city, data.contact ,data.password, data.tax_file, data.commercial_register, datetime.now(),data.street,data.Country,data.postcode,'Failed',order_code,data.amount,data.sub_type,datetime.now(),data.password_hash,data.package_id,data.company_string_name)
                        db.session.add(order_data)
                        db.session.commit()
                        order_data.order_id = order_data.id
                        order_data.tans_ref = get_json_transaction_ref
                        order_data.subscription_id = data.subscription_id
                        order_data.customer_token = data.customer_token
                        order_data.auto_payment_status = 'Failed'
                        order_data.country_code_id = data.country_code_id
                        db.session.commit()
                        sub_data = Subscription.query.filter_by(id = data.subscription_id).first()
                        sub_data.order_id = order_data.id
                        sub_data.expire_db = datetime.now()
                        sub_data.plan_type = data.sub_type
                        sub_data.price = data.amount
                        sub_data.payment_status = 'Payment Failed'
                        db.session.commit()
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Payment Failed")
                        get_logger_function('check_payment_update','info', 'update payment is failed created the tran_ref is>>>'+ get_json_transaction_ref +'and order table id is >>> '+order_data.id ,'cashier me site')
                        return get_json_transaction_ref
                else:
                    data.auto_payment_status = 'invalid_process'
                    db.session.commit()
                    get_logger_function('check_payment_update','error', 'error for send request to paytabs the tran_ref is >>> '+transaction_ref,'cashier me site')
                    print("error response   >>>>>>>>>> for >>>>>",transaction_ref,response.content)
                    return 'invalid_process'
    except Exception as Error:
        print(Error)
        get_logger_function('check_payment_update', 'error','error in check payment upgrade scheduler function please check this and the error is >>>>>'+str(Error),'cashier me site')
        return str(Error)




# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> automatic Payment Scheduler >>>>>>>>>>>>>>>>>>
@scheduler.task('interval', id='do_jo12522dsdsdsdsddd2', seconds=80000)
def check_payment_update_for_turkish () :
    try :
        get_data = Order.query.filter(and_(Order.expire_db < datetime.now( ),
                                           Order.auto_payment_status != 'Failed',
                                           Order.auto_payment_status != 'invalid_process',
                                           Order.auto_payment_status != 'Canceled')).all( )
        for data in get_data :
            if data.auto_payment_status != 'payment_last' :
                data.auto_payment_status = 'payment_last'
                db.session.commit( )
                customer_token = data.customer_token
                if data.price_toUpdate :
                    amount = data.price_toUpdate
                else :
                    amount = data.amount
                random_code1 = random.randint(1, 100000)
                random_code2 = random.randint(1, 100000)
                add_ref_number = "REF_"+str(random.randint(1, 100000000))
                order_code = str(random_code1)+'-'+str(random_code2)+'-'+str(
                    datetime.now().date())
                get_payment_data = Countries.query.filter_by(country_code="TUR").first( )

                payment_request = payment_3d_turkish_request(
                    get_payment_data.turkish_merchant_id,
                    get_payment_data.turkish_merchant_key,
                    "https://cashierme.com/testrevpay",
                    add_ref_number, amount,
                    customer_token, data.name,
                    data.email,
                    data.street,2)
                if payment_request :
                    get_logger_function('turkisg_check_payment_update', 'info',
                                       str(payment_request),
                                        'cashier me site')
                    if data.sub_type_toUpdate == 'yearly' :
                        update_time = 366
                    if data.sub_type_toUpdate is None and data.sub_type == 'yearly' :
                        update_time = 366
                    if data.sub_type_toUpdate == 'Monthly' :
                        update_time = 31
                    if data.sub_type_toUpdate is None and data.sub_type == 'Monthly' :
                        update_time = 31
                    if payment_request["STATUS"] == "SUCCESS" :
                        if data.sub_type_toUpdate :
                            add_subtype = data.sub_type_toUpdate
                        else :
                            add_subtype = data.sub_type
                        if data.price_toUpdate :
                            add_price = data.price_toUpdate
                        else :
                            add_price = data.amount
                        if data.pos_no_toUpdate :
                            add_pos_no = data.pos_no_toUpdate
                        else :
                            add_pos_no = data.stores_number
                        order_data = Order(data.name, data.email, add_pos_no,
                                           data.business_name, data.city,
                                           data.contact, data.password,
                                           data.tax_file,
                                           data.commercial_register,
                                           datetime.now( ), data.street,
                                           data.Country, data.postcode, 'Done',
                                           order_code, add_price, add_subtype
                                           , datetime.now( )+timedelta(
                                update_time), data.password_hash,
                                           data.package_id,
                                           data.company_string_name)
                        db.session.add(order_data)
                        db.session.commit( )
                        order_data.order_id = order_data.id
                        order_data.tans_ref = add_ref_number
                        order_data.subscription_id = data.subscription_id
                        order_data.auto_payment_status = 'Done'
                        order_data.country_code_id = data.country_code_id
                        order_data.expire_db = datetime.now( )+timedelta(
                            update_time)
                        order_data.customer_token = customer_token
                        order_data.account_type = "Live"
                        db.session.commit( )
                        data.auto_payment_status = 'payment_last'
                        db.session.commit( )
                        sub_data = Subscription.query.filter_by(
                            id=data.subscription_id).first( )
                        sub_data.order_id = order_data.id
                        sub_data.stores_number = order_data.stores_number
                        sub_data.plan_type = order_data.sub_type
                        sub_data.price = order_data.amount
                        sub_data.expire_db = datetime.now( )+timedelta(
                            update_time)
                        sub_data.payment_status = 'Payment Successfully'
                        sub_data.account_type = "Live"
                        db.session.commit( )
                        try :
                            get_qr_code = generate_normal_qr_code(
                                order_data.amount)
                            order_data.qr_code_base64 = get_qr_code["qr_code"]
                            db.session.commit( )

                            get_logger_function('/check_payment_update', 'info',
                                                'invoice (QR) created successfully for>>>>'+order_data.business_name,
                                                'cashier me site')
                        except Exception as error :
                            get_logger_function('/check_payment_update',
                                                'error', str(error),
                                                'cashier me site')
                            print(error)
                            pass
                        print(
                            ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Payment Successful")
                        get_logger_function('check_payment_update', 'info',
                                            'update payment is successfully created the tran_ref is>>>'+str(
                                                add_ref_number)+'and order table id is >>> '+str(
                                                order_data.id),
                                            'cashier me site')
                    else :
                        order_data = Order(data.name, data.email,
                                           data.stores_number,
                                           data.business_name, data.city,
                                           data.contact, data.password,
                                           data.tax_file,
                                           data.commercial_register,
                                           datetime.now( ), data.street,
                                           data.Country, data.postcode,
                                           'Failed', order_code, data.amount,
                                           data.sub_type, datetime.now( ),
                                           data.password_hash, data.package_id,
                                           data.company_string_name)
                        db.session.add(order_data)
                        db.session.commit( )
                        order_data.order_id = order_data.id
                        order_data.tans_ref = add_ref_number
                        order_data.subscription_id = data.subscription_id
                        order_data.customer_token = get_data.customer_token
                        order_data.auto_payment_status = 'Failed'
                        order_data.country_code_id= "TUR"
                        db.session.commit( )
                        sub_data = Subscription.query.filter_by(
                            id=data.subscription_id).first( )
                        sub_data.order_id = order_data.id
                        sub_data.expire_db = datetime.now( )
                        sub_data.plan_type = get_data.sub_type
                        sub_data.price = get_data.amount
                        sub_data.payment_status = 'Payment Failed'
                        db.session.commit( )
                        print(
                            ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Payment Failed")
                        get_logger_function('check_payment_update', 'info',
                                            'update payment is failed created the tran_ref is>>>'+add_ref_number+'and order table id is >>> '+order_data.id,
                                            'cashier me site')
                else :
                    data.auto_payment_status = 'invalid_process'
                    db.session.commit( )
                    print(">>>>>>>>>>>>>>>>>not request")
                    get_logger_function('check_payment_update', 'error',
                                        'error for send request to paytabs the tran_ref is >>> '+add_ref_number,
                                        'cashier me site')
    except Exception as Error :
        print(Error)
        get_logger_function('turkish_check_payment_update', 'error',
                            'error in check payment upgrade scheduler function please check this and the error is >>>>>'+str(
                                Error), 'cashier me site')






@app.route('/view_invoice/<string:get_id>',methods=['POST','GET'])
@login_required
@check_coutry
def view_invoice(get_id):
    get_data = Order.query.get_or_404(get_id)
    get_user_id = get_data.subscription_id
    print(get_user_id)
    print(current_user.id)
    if str(get_user_id) == str(current_user.id):
        return  render_template('view_invoice.html'
                                , get_url =SECURE_KEYS.DASHBOARD_URL + get_data.business_name,
                                name = get_data.name,
                                address = get_data.street,
                                city = get_data.city,
                                country = get_data.Country,
                                zip = get_data.postcode,
                                package = get_data.stores_number,
                                company = get_data.business_name,
                                domain =SECURE_KEYS.DASHBOARD_URL + get_data.business_name,
                                subscription = get_data.sub_type,
                                expire = get_data.expire_db,
                                price = get_data.amount,
                                invoice_num = str(get_data.id ),
                                invoice_date = datetime.now(),
                                img_data=get_data.qr_code_base64,
                                active_page='invoices'
                                ),cleanup(db.session)

    else:
        return redirect('/invoices'),cleanup(db.session)

@app.route('/report_pdf_customers/<string:get_id>',methods=['POST','GET'])
@login_required
@check_coutry
def report_pdf_customers(get_id):
    get_data = Order.query.get_or_404(get_id)
    print(get_data)
    render = render_template('pdf_report.html'
                             , get_url =SECURE_KEYS.DASHBOARD_URL + get_data.business_name,
                             name = get_data.name,
                             address = get_data.street,
                             city = get_data.city,
                             country = get_data.Country,
                             zip = get_data.postcode,
                             package = get_data.stores_number,
                             company = get_data.business_name,
                             domain =SECURE_KEYS.DASHBOARD_URL + get_data.business_name,
                             subscription = get_data.sub_type,
                             expire = get_data.expire_db,
                             price = get_data.amount,
                             invoice_num = str(get_data.id ),
                             invoice_date = datetime.now(),
                             img_data=get_data.qr_code_base64,
                             )
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(render, False,configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=invoice'+str(get_data.id )+'.pdf'
    if str(current_user.id) == str(get_data.subscription_id):
        return response,cleanup(db.session)
    else:
        return redirect('/'),cleanup(db.session)


@app.route('/report_pdf_customers_from_page/<string:business_name>/'
           '<string:name>/<string:street>/<string:city>/<string:country>/<string:zip>'
           '/<string:stores_no>/<string:sub_type>/<string:expire_date>/<string:amount>/<string:invoice_num>/<string:qr_code>',methods=['POST','GET'])
def report_pdf_customers_from_page(business_name,name,street,city,country,zip,stores_no,sub_type,expire_date,amount,invoice_num,qr_code):
    render = render_template('pdf_report.html'
                             , get_url =SECURE_KEYS.DASHBOARD_URL + business_name,
                             name = name,
                             address = street,
                             city = city,
                             country = country,
                             zip = zip,
                             package = stores_no,
                             company = business_name,
                             domain =SECURE_KEYS.DASHBOARD_URL + business_name,
                             subscription = sub_type,
                             expire = expire_date,
                             price = amount,
                             invoice_num = invoice_num,
                             invoice_date = datetime.now(),
                             img_data=qr_code,
                             )

    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(render, False,configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=invoice'+str(invoice_num )+'.pdf'
    return response,cleanup(db.session)





@app.route('/get_customer_token/<string:tran_ref>',methods=['POST', 'GET'])
def get_customer_token(tran_ref):
    data = {
        'profile_id': merchant_saudi_id,
        'tran_ref':tran_ref
    }
    res = requests.post(url_query, data=json.dumps(data),headers = {'authorization':paytabs_saudi_api_key,'content-type':'https://cashierme.com/get_transaction'})
    result = json.loads(res.content)
    return result


scheduler.start()

@app.route('/add_custom_token')
def add_custom_token():
    data = Subscription.query.filter_by(company_token = None).all()
    if data:
        for res in data:
            company_token = random.randint(1,100000000000000000)
            res.company_token = company_token
            db.session.commit()
            db_name = res.business_name
            full_db_name = 'upos_'+db_name
            import mysql.connector
            rec = mysql.connector.connect(user=SECURE_KEYS.DB_USER, password=SECURE_KEYS.DB_PASSWORD, host='localhost', database=full_db_name)
            try:
                if rec:
                    connect_db = rec.cursor()
                    connect_db.execute("update company_information set company_token = '" + str(company_token) +"' ")
                    get_logger_function('/add_custom_token','info', 'custom token created successfully database name >>>>> '+full_db_name+ '----->custom token is--->'+str(company_token),'cashier me site')
                    print(res.name, 'ok created')
                    rec.commit()
                else:
                    get_logger_function('/add_custom_token','error', 'cannot be connect to this datbase >>>>> '+full_db_name+ '----->custom token is--->'+str(company_token),'cashier me site')
                    return "error for connect database >>>>{}".format(full_db_name)
            except Exception as error:
                print(error)
                get_logger_function('/add_custom_token','error', 'exption error  >>>>> '+str(error)+ '----->custom token is--->'+str(company_token),'cashier me site')
        return "created Successfully"
    else:
        return "company token not null in your application"


@app.route('/view_db_customToken_null')
def view_db_customToken_null():
    data = Subscription.query.filter_by(company_token = None).all()
    if data:
        for res in data:
            datas = res.business_name
            get_logger_function('/view_db_customToken_null','info', 'database name >>>>> '+datas,'cashier me site')
        return 'all databases'
    else:
        return "company token not null in your application"


@app.route('/india_update_subscription_to_annually/<string:pos_num>/<string:raz_order_id>/<string:raz_payment_id>/<string:rez_signuture>', methods=['POST'])
def india_update_subscription_to_annually(pos_num,raz_order_id,raz_payment_id,rez_signuture):
    try:
        get_price_annualy = get_price_of_package(pos_num, 'yearly')
        total = get_price_annualy['price']
        Balance = get_price_annualy['Balance']
        to_payment_price = Balance
        print('>>>>>>>>>>>>>>>>>>>>', to_payment_price)
        get_order_id = current_user.order_id
        check_data = Order.query.filter_by(id=get_order_id).first( )
        check_package = Packages.query.filter(and_(Packages.type == 'yearly', Packages.pos_no_code == pos_num,Packages.country_code == session['country_code'])).first( )
        order_code = raz_order_id
        update_time = 366
        order_data = Order(check_data.name,
                           check_data.email,
                           pos_num,
                           check_data.business_name,
                           check_data.city,
                           check_data.contact,
                           check_data.password,
                           check_data.tax_file,
                           check_data.commercial_register,
                           datetime.now( ),
                           check_data.street,
                           check_data.Country,
                           check_data.postcode,
                           '',
                           order_code,
                           to_payment_price,
                           'yearly'
                           , datetime.now( )+timedelta(update_time),
                           check_data.password_hash,
                           check_package.id,
                           check_data.company_string_name)
        db.session.add(order_data)
        db.session.commit( )
        order_data.order_id = order_data.id
        order_data.razorpay_order_id = raz_order_id
        order_data.subscription_id = check_data.subscription_id
        order_data.auto_payment_status = ' '
        order_data.expire_db = datetime.now( )+timedelta(update_time)
        order_data.razorpay_payment_id = raz_payment_id
        order_data.sub_type_toUpdate = 'yearly'
        order_data.pos_no_toUpdate = pos_num
        order_data.price_toUpdate = total
        order_data.razorpay_signature = rez_signuture
        order_data.payment_getway = "razorpay"
        order_data.account_type = "Live"
        order_data.country_code_id = current_user.country_code_id
        db.session.commit( )
        sub_data = Subscription.query.filter_by(
            id=order_data.subscription_id).first( )
        sub_data.order_id = order_data.id
        sub_data.stores_number = pos_num
        sub_data.plan_type = 'yearly'
        sub_data.price = total
        sub_data.expire_db = datetime.now( )+timedelta(update_time)
        sub_data.payment_status = 'Payment Successfully'
        sub_data.account_type = "Live"
        db.session.commit( )
        try :
            saller_name = 'Ultimate Solutions'
            seller_len = len(saller_name)
            vat_number = '311136332100003'
            dateandtime = datetime.now( ).strftime('%Y-%m-%dT%H:%M:%SZ')
            amount = str(order_data.amount)
            amounts = order_data.amount
            get_len = len(amount)
            tax = round(int(amounts)-(int(amounts) / 1.15), 2)
            # tax = (15 * int(amounts)) / 100
            get_tax_len = len(str(tax))
            company2hex = hexaConvertFunction.string2hex(saller_name)
            fullCompany2hex = '01'+str(
                hexaConvertFunction.int2hex(seller_len))+company2hex
            vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
            fullnumber2hex = '020F'+vatnumber2hex
            datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
            fulldatetimehex = '0314'+datetimeInvoicehex
            amount2hexa = hexaConvertFunction.string2hex(amount)
            fulamount2hexa = '040'+str(get_len)+amount2hexa
            tax2hexa = hexaConvertFunction.string2hex(str(tax))
            fulltax2hexa = '050'+str(get_tax_len)+tax2hexa
            get_qr_base64 = hexa2base64.hex2funbase64(
                fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
            print('hexa code :>>>>>>>>>>>>>>>',
                  fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
            print('base64 code >>>>>>>>>>>>>>', get_qr_base64)
            order_data.qr_code_base64 = get_qr_base64
            db.session.commit( )
            get_logger_function('/india_update_subscription_to_annually', 'info',
                                'invoice (QR) created successfully for>>>>'+order_data.business_name,
                                'cashier me site')
            try :
                msg = Message(recipients=[email])
                msg.html = render_template('invoicess.html',
                                           password=order_data.password,
                                           database_fullname=order_data.business_name,
                                           name=order_data.name,
                                           address=order_data.street,
                                           city=order_data.city,
                                           country=order_data.Country,
                                           zip=order_data.postcode,
                                           package=pos_num,
                                           company=order_data.business_name,
                                           domain=SECURE_KEYS.DASHBOARD_URL + order_data.business_name,
                                           subscription=order_data.sub_type,
                                           expire=order_data.expire_db,
                                           price=order_data.amount,
                                           invoice_num=str(order_data.order_id),
                                           invoice_date=datetime.now( ),
                                           img_data=get_qr_base64)
                mail.send(msg)
            except Exception as error :
                get_logger_function('/india_update_subscription_to_annually', 'error',
                                    str(error), 'cashier me site')
                pass
        except Exception as error :
            get_logger_function('/india_update_subscription_to_annually', 'error',
                                str(error), 'cashier me site')
            print(error)
            pass
        print(
            ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Payment Successful")
        get_logger_function('india_update_subscription_to_annually', 'info',
                            'update payment is successfully created the tran_ref is>>>'+str(
                                raz_payment_id)+'and order table id is >>> '+str(
                                order_data.id), 'cashier me site')
        return jsonify({"status" :"success",
                        "value" :order_data.id})

    except Exception as error:
        print(error)
        return "Error"
    return "Error"





#>>>>>>>>>>>>>>>>> upgrade to Annualy ajax <<<<<<<<<<<<
@app.route('/update_subscription_to_yearly/<string:pos_num>', methods=['POST'])
@check_coutry
def update_subscription_to_yearly(pos_num):
    get_price_annualy = get_price_of_package(pos_num, 'yearly' )
    total = get_price_annualy['price']
    Balance = get_price_annualy['Balance']
    to_payment_price =  int(Balance)
    print('>>>>>>>>>>>>>>>>>>>>',to_payment_price)
    get_order_id = current_user.order_id
    check_data = Order.query.filter_by(id = get_order_id).first()
    get_payment_data = Countries.query.filter_by(country_code = check_data.country_code_id).first()
    transaction_ref = check_data.tans_ref
    customer_token = check_data.customer_token
    check_package = Packages.query.filter(and_(Packages.type == 'yearly', Packages.pos_no_code == pos_num,Packages.country_code == session['country_code'])).first()
    random_code1 = random.randint(1, 100000)
    random_code2 = random.randint(1, 100000)
    order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
    payment_request = {
        "profile_id":str(get_payment_data.payment_merchant_id) ,
        "tran_type":"sale" ,
        "tran_class":"recurring" ,
        "cart_id": str(order_code) ,
        "cart_currency":str(get_payment_data.payment_currency) ,
        "cart_amount":str(to_payment_price) ,
        "cart_description":"test for token customer" ,
        "token": str(customer_token) ,
        "tran_ref":str(transaction_ref)
    }
    response = requests.post(str(get_payment_data.payment_request_api_url), data = json.dumps(payment_request), headers = {'authorization':str(get_payment_data.payment_api_key),'content-type':'application/json'})
    if response :
        get_logger_function('update_subscription_to_yearly','info', 'check data and expiration date and send request to paytabs  is successfully' ,'cashier me site')
        result = json.loads(response.content)
        print(result)
        get_json_transaction_ref = result.get('tran_ref')
        get_json_payment_result = result.get('payment_result')
        get_response_status = get_json_payment_result['response_status']
        get_response_message = get_json_payment_result['response_message']
        check_data.tans_ref = get_json_transaction_ref
        db.session.commit()
        update_time = 366
        try:
            if get_response_status == 'A' and get_response_message == "Authorised":
                order_data = Order(check_data.name,
                                   check_data.email,
                                   pos_num ,
                                   check_data.business_name,
                                   check_data.city,
                                   check_data.contact ,
                                   check_data.password,
                                   check_data.tax_file,
                                   check_data.commercial_register,
                                   datetime.now(),
                                   check_data.street,
                                   check_data.Country,
                                   check_data.postcode,
                                   '',
                                   order_code,
                                   to_payment_price,
                                   'yearly'
                                   ,datetime.now()+ timedelta(update_time),
                                   check_data.password_hash,
                                   check_package.id,
                                   check_data.company_string_name)
                db.session.add(order_data)
                db.session.commit()
                order_data.order_id = order_data.id
                order_data.tans_ref = get_json_transaction_ref
                order_data.subscription_id = check_data.subscription_id
                order_data.auto_payment_status = ' '
                order_data.expire_db = datetime.now()+ timedelta(update_time)
                order_data.customer_token = customer_token
                order_data.sub_type_toUpdate = 'yearly'
                order_data.pos_no_toUpdate = pos_num
                order_data.price_toUpdate = total
                order_data.account_type = "Live"
                db.session.commit()
                sub_data = Subscription.query.filter_by(id = order_data.subscription_id).first()
                sub_data.order_id = order_data.id
                sub_data.stores_number = pos_num
                sub_data.plan_type = 'yearly'
                sub_data.price = total
                sub_data.expire_db = datetime.now()+ timedelta(update_time)
                sub_data.payment_status = 'Payment Successfully'
                sub_data.account_type = "Live"
                db.session.commit()
                try:
                    saller_name = 'Ultimate Solutions'
                    seller_len = len(saller_name)
                    vat_number = '311136332100003'
                    dateandtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                    amount = str(order_data.amount)
                    amounts = order_data.amount
                    get_len = len(amount)
                    tax = round(int(amounts)-(int(amounts) / 1.15), 2)
                    # tax = (15 * int(amounts)) / 100
                    get_tax_len = len(str(tax))
                    company2hex = hexaConvertFunction.string2hex(saller_name)
                    fullCompany2hex = '01' + str(hexaConvertFunction.int2hex(seller_len)) + company2hex
                    vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
                    fullnumber2hex = '020F' + vatnumber2hex
                    datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
                    fulldatetimehex = '0314'+ datetimeInvoicehex
                    amount2hexa = hexaConvertFunction.string2hex(amount)
                    fulamount2hexa = '040'+ str(get_len) + amount2hexa
                    tax2hexa = hexaConvertFunction.string2hex(str(tax))
                    fulltax2hexa = '050' + str(get_tax_len) + tax2hexa
                    get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('hexa code :>>>>>>>>>>>>>>>',fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('base64 code >>>>>>>>>>>>>>',get_qr_base64)
                    order_data.qr_code_base64 = get_qr_base64
                    db.session.commit()
                    get_logger_function('/update_subscription_to_yearly','info', 'invoice (QR) created successfully for>>>>'+order_data.business_name,'cashier me site')
                    try:
                        msg = Message(recipients=[email])
                        msg.html = render_template('invoicess.html',
                                                   password = order_data.password,
                                                   database_fullname = order_data.business_name,
                                                   name = order_data.name,
                                                   address = order_data.street,
                                                   city = order_data.city,
                                                   country = order_data.Country,
                                                   zip = order_data.postcode,
                                                   package = pos_num,
                                                   company = order_data.business_name,
                                                   domain =SECURE_KEYS.DASHBOARD_URL + order_data.business_name,
                                                   subscription = order_data.sub_type,
                                                   expire = order_data.expire_db,
                                                   price = order_data.amount,
                                                   invoice_num = str(order_data.order_id ),
                                                   invoice_date = datetime.now(),
                                                   img_data=get_qr_base64)
                        mail.send(msg)
                    except Exception as error:
                        get_logger_function('/update_subscription_to_yearly','error', str(error),'cashier me site')
                        pass
                except Exception as error:
                    get_logger_function('/update_subscription_to_yearly','error', str(error),'cashier me site')
                    print(error)
                    pass
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Payment Successful")
                get_logger_function('update_subscription_to_yearly','info', 'update payment is successfully created the tran_ref is>>>'+ str(get_json_transaction_ref) +'and order table id is >>> '+str(order_data.id) ,'cashier me site')
                return jsonify({"status":"success",
                                "value":order_data.id})
            elif get_response_status == 'E':
                get_logger_function('/update_subscription_to_yearly','info', 'customer not have money in cared to update point of sale'+current_user.business_name,'cashier me site')
                return "customer_havenot_money"
            elif get_response_status == 'D':
                get_logger_function('/update_subscription_to_yearly','info', 'paytabs not proccess this transaction please try again'+current_user.business_name,'cashier me site')
                print("D")
                return "Cant_process_now"
            else:
                get_logger_function('/update_subscription_to_yearly','info', 'you have response code not add in system please fixed this code and search in paytabs to fixed it'+get_data.business_name,'cashier me site')
                return "get_code_error"
        except Exception as error:
            get_logger_function('/update_subscription_to_yearly','error', str(error) +'error for this'+current_user.business_name,'cashier me site')
            print(error)
            return "Error"
    else:
        get_logger_function('/update_subscription_to_yearly','info', 'you have response code not add in system please fixed this code and search in paytabs to fixed it'+current_user.business_name,'cashier me site')
        return "get_code_error"




@app.route('/Login_to_account/<string:email>/<string:password>', methods=['POST', 'GET'])
def Login_to_account(email, password):
    return submit_login_subscription(email,password)

@app.route('/update_subscription_to_monthly/<string:pos_num>', methods=['POST'])
@check_coutry
def update_subscription_to_monthly(pos_num):
    get_order_id = current_user.order_id
    check_data = Order.query.filter_by(id = get_order_id).first()
    check_package = Packages.query.filter(and_(Packages.type == 'Monthly', Packages.pos_no_code == pos_num,Packages.country_code == session['country_code'])).first()
    print(check_package.price)
    try:
        check_data.pos_no_toUpdate= pos_num
        check_data.sub_type_toUpdate = 'Monthly'
        check_data.price_toUpdate = check_package.price
        db.session.commit()
        get_logger_function('/update_subscription_to_yearly','info', 'update subscription successfully'+current_user.business_name,'cashier me site')
        cleanup(db.session)
        return "ok"
    except Exception as error:
        get_logger_function('/update_subscription_to_yearly','error', str(error) +'error for this'+current_user.business_name,'cashier me site')
        print(error)
        cleanup(db.session)
        return "no"

# @app.route('/confirm_cancel_subscription', methods=['POST'])
# @check_coutry
# def confirm_cancel_subscription():
#     get_id = current_user.id
#     check_sub_data = Subscription.query.filter_by(id = get_id).first()
#     try:
#         check_order_data = Order.query.filter_by(id= check_sub_data.order_id).first()
#         check_sub_data.subscription_status = 'Canceled'
#         check_order_data.auto_payment_status = 'Canceled'
#         db.session.commit()
#         get_logger_function('/confirm_cancel_subscription','info', 'Canceled subscription successfully'+current_user.business_name,'cashier me site')
#         cleanup(db.session)
#         return "success"
#     except Exception as error:
#         get_logger_function('/confirm_cancel_subscription','error', str(error) +'error for cancel subscription for this'+current_user.business_name,'cashier me site')
#         cleanup(db.session)
#         return "Failed"

# @app.route('/reactive_subscription', methods=['POST'])
# @check_coutry
# def reactive_subscription():
#     get_id = current_user.id
#     check_sub_data = Subscription.query.filter_by(id = get_id).first()
#     try:
#         check_order_data = Order.query.filter_by(id= check_sub_data.order_id).first()
#         check_sub_data.subscription_status = ''
#         check_order_data.auto_payment_status = ''
#         db.session.commit()
#         get_logger_function('/confirm_cancel_subscription','info', 'reactive  subscription successfully'+current_user.business_name,'cashier me site')
#         return redirect('/invoices'),cleanup(db.session)
#     except Exception as error:
#         get_logger_function('/confirm_cancel_subscription','error', str(error) +'error for reactive subscription for this'+current_user.business_name,'cashier me site')
#         return redirect('/invoices'),cleanup(db.session)



@app.route('/create_package_record_saudi/<string:code>/<int:pos_no>', methods=['POST', 'GET'])
def create_package_record_saudi(code, pos_no):
    if code == '^^^UltimateSolutions>>Packages=1000^^^':
        packages_delete = Packages.query.all()
        print("ok")
        for data in packages_delete:
            db.session.delete(data)
            db.session.commit()
        print("ok")
        month = 'Monthly'
        year = 'yearly'
        price_month = 30
        price_year = 300
        en_string = 'Point Of Sale'
        ar_string = 'نقطة بيع'
        currency_en = 'SAR'
        currency_ar = '.ر.س'
        for data in range(pos_no):
            get_code = data
            get_price_month = price_month * data
            get_price_year = price_year * data
            add_packages_month = Packages(str(get_price_month),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,month,currency_en,currency_ar,str(get_code),get_code, "SAU" )
            add_packages_year = Packages(str(get_price_year),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,year,currency_en,currency_ar,str(get_code),get_code ,"SAU")
            db.session.add(add_packages_month)
            db.session.commit()
            db.session.add(add_packages_year)
            db.session.commit()
        return "ok add column"
    else:
        return "error"


@app.route('/create_package_record_global/<string:code>/<int:pos_no>', methods=['POST', 'GET'])
def create_package_record_global(code, pos_no):
    if code == '^^^UltimateSolutions>>Packages=1000^^^':
        month = 'Monthly'
        year = 'yearly'
        price_month = 8
        price_year = 80
        en_string = 'POS'
        ar_string = 'POS'
        currency_en = 'USD'
        currency_ar = "USD"
        for data in range(pos_no):
            get_code = data
            get_price_month = price_month * data
            get_price_year = price_year * data
            add_packages_month = Packages(str(get_price_month),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,month,currency_en,currency_ar,str(get_code),get_code,"GLB" )
            add_packages_year = Packages(str(get_price_year),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,year,currency_en,currency_ar,str(get_code),get_code, "GLB" )
            db.session.add(add_packages_month)
            db.session.commit()
            db.session.add(add_packages_year)
            db.session.commit()
        return "ok add column"
    else:
        return "error"
#tttttt
@app.route('/create_package_record_egyptian/<string:code>/<int:pos_no>', methods=['POST', 'GET'])
def create_package_record_egyptian(code, pos_no):
    if code == '^^^UltimateSolutions>>Packages=1000^^^':
        month = 'Monthly'
        year = 'yearly'
        price_month = 250
        price_year = 2400
        en_string = 'Point Of Sale'
        ar_string = 'نقطة بيع'
        currency_en = 'EGP'
        currency_ar = '.ج'
        for data in range(pos_no):
            get_code = data
            get_price_month = price_month * data
            get_price_year = price_year * data
            add_packages_month = Packages(str(get_price_month),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,month,currency_en,currency_ar,str(get_code),get_code,"EGY" )
            add_packages_year = Packages(str(get_price_year),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,year,currency_en,currency_ar,str(get_code),get_code, "EGY" )
            db.session.add(add_packages_month)
            db.session.commit()
            db.session.add(add_packages_year)
            db.session.commit()
        return "ok add column"
    else:
        return "error"

@app.route('/create_package_record_malysia/<string:code>/<int:pos_no>', methods=['POST', 'GET'])
def create_package_record_malysia(code, pos_no):
    if code == '^^^UltimateSolutions>>Packages=1000^^^':
        month = 'Monthly'
        year = 'yearly'
        price_month = 35
        price_year = 353
        en_string = 'PoS'
        ar_string = 'PoS'
        currency_en = 'MYR'
        currency_ar = 'MYR'
        for data in range(pos_no):
            get_code = data
            get_price_month = price_month * data
            get_price_year = price_year * data
            add_packages_month = Packages(str(get_price_month),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,month,currency_en,currency_ar,str(get_code),get_code, "MYS" )
            add_packages_year = Packages(str(get_price_year),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,year,currency_en,currency_ar,str(get_code),get_code , "MYS")
            db.session.add(add_packages_month)
            db.session.commit()
            db.session.add(add_packages_year)
            db.session.commit()
        return "ok add column"
    else:
        return "error"

@app.route('/create_package_record_turkish/<string:code>/<int:pos_no>', methods=['POST', 'GET'])
def create_package_record_turkish(code, pos_no):
    if code == '^^^UltimateSolutions>>Packages=1000^^^':
        month = 'Monthly'
        year = 'yearly'
        price_month = 59
        price_year = 588
        en_string = 'PoS'
        ar_string = 'PoS'
        currency_en = 'TRY'
        currency_ar = 'TRY'
        for data in range(pos_no):
            get_code = data
            get_price_month = price_month * data
            get_price_year = price_year * data
            add_packages_month = Packages(str(get_price_month),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,month,currency_en,currency_ar,str(get_code),get_code, "TUR" )
            add_packages_year = Packages(str(get_price_year),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,year,currency_en,currency_ar,str(get_code),get_code,"TUR" )
            db.session.add(add_packages_month)
            db.session.commit()
            db.session.add(add_packages_year)
            db.session.commit()
        return "ok add column"
    else:
        return "error"


@app.route('/create_package_record_india/<string:code>/<int:pos_no>', methods=['POST','GET'])
def create_package_record_india(code, pos_no):
    if code == '^^^UltimateSolutions>>Packages=1000^^^':
        month = 'Monthly'
        year = 'yearly'
        price_month = 240
        price_year = 2400
        en_string = 'PoS '
        ar_string = 'PoS'
        currency_en = 'INR'
        currency_ar = 'INR'
        for data in range(pos_no):
            get_code = data
            get_price_month = price_month * data
            get_price_year = price_year * data
            add_packages_month = Packages(str(get_price_month),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,month,currency_en,currency_ar,str(get_code),get_code, "IND" )
            add_packages_year = Packages(str(get_price_year),str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,year,currency_en,currency_ar,str(get_code),get_code,"IND" )
            db.session.add(add_packages_month)
            db.session.commit()
            db.session.add(add_packages_year)
            db.session.commit()
        return "ok add column"
    else:
        return "error"

@app.route('/add_coutry_none')
def add_custom_country():
    data = Subscription.query.filter_by(country_code_id = None).all()
    for res in data:
        res.country_code_id = "SAU"
        db.session.commit()
    datas = Order.query.filter_by (country_code_id=None).all()
    for rec in datas:
        rec.country_code_id = "SAU"
        db.session.commit()
    print("success")
    return "success"

@app.route('/test_payment')
def test_payment():
    return render_template('test_paytabs_payment.html')
#test usd payment
@app.route('/test_payment_usd',methods=['POST'])
def test_payment_usd():
    try:
        get_payment_data = Countries.query.filter_by(country_code = "GLB").first()
        create_json={'profile_id':str(
            get_payment_data.payment_merchant_id),
            'tran_type':str('sale'),
            'tran_class':str('ecom'),
            "tokenise":"2",
            'cart_description':str("525552332"),
            'cart_id':str('order_code12345222'),
            'cart_currency':str(get_payment_data.payment_currency),
            'cart_amount':"1",
            'callback':str(SECURE_KEYS.CALL_BACK_URL + '/paytabs_response_for_test_usd'),
            'return':str(SECURE_KEYS.CALL_BACK_URL + '/paytabs_response_for_test_usd'),
            "hide_shipping":True,
            'customer_details':{
                'name':str('sameer mostafa fathey'),
                'email':str('samerfathey2002@gmail.com'),
                'city':str('istanbul'),
                'phone':str('01558414779'),
                'street1':str('16test istanbul'),
                'country':"TR",
                'state':"istanbul"
            }}
        response = requests.post(str(get_payment_data.payment_request_api_url), data = json.dumps(create_json), headers = {'authorization':str(get_payment_data.payment_api_key) ,'content-type':'https://cashierme.com/json'})
        print(response.content)
        datas = json.loads(response.content)
        print(datas.get('redirect_url'))
        get_url_response = datas.get('redirect_url')
        # transaction_ref = datas.get('tran_ref')
        return redirect(get_url_response)
    except:
        return redirect('/test_payment')

@app.route('/paytabs_response_for_test_usd', methods=['POST', 'GET'])
def paytabs_response_for_test_usd():
    get_data = request.form.to_dict()
    return render_template('test_paytabs_payment.html', response = str(get_data) )


@app.errorhandler(401)
def page_authorized(error):
    return redirect('/login')


@app.errorhandler(404)
def page_not_found(error):
    return redirect('/contact')


@app.errorhandler(500)
def error_page(error):
    return redirect('/contact')

from ultimate_saas_functions.esnekpos_requests import create_esnekpos_requests




@app.route('/upgrade_subscription_turkish_renew', methods=['POST', 'GET'])
def upgrade_subscription_turkish_renew():
    try:
        if current_user.country_code_id == "TUR" and current_user.account_type == "Test":
            print("iman access>>>>>>>>>>>>>>>>>>>>>>>>")
            calculation_payment_amount = current_user.price
            get_transaction_ref = create_esnekpos_requests(calculation_payment_amount,current_user.name,current_user.email,current_user.city,current_user.contact,current_user.street,"testrevpay")
            if get_transaction_ref['STATUS'] == "SUCCESS":
                RETURN_CODE = get_transaction_ref['RETURN_CODE']
                STATUS = get_transaction_ref['STATUS']
                URL_3DS = get_transaction_ref['URL_3DS']
                REFNO = get_transaction_ref['REFNO']
                HASH = get_transaction_ref['HASH']
                ORDER_REF_NUMBER = get_transaction_ref['ORDER_REF_NUMBER']

                return redirect(URL_3DS)


        #     add_order_record = add_order_record_from_current_user(current_user.id)
        #     update_order_record = update_order_record_from_current_user_turkish(add_order_record['order_id'], get_transaction_ref['token'],get_transaction_ref['merchant_oid'])
        #     if update_order_record["status"] == "Success":
        #         resp = make_response(render_template('turkish_payment.html', response = get_transaction_ref['token']))
        #         resp.set_cookie("MOD", get_transaction_ref['merchant_oid'])
        #         return resp
        #     else:
        #         delete_order_record_from_current_user(add_order_record['order_id'])
        #         return redirect('/invoices')
        # elif current_user.country_code_id == "TUR" and current_user.account_type == "Live" :
        #     get_amount = get_amount_for_renew(current_user.id)
        #     if get_amount["status"] == "Success":
        #         amount = get_amount["amount"]
        #         get_transaction_ref = paytr_requests(amount,
        #                                              current_user.name,
        #                                              current_user.email,
        #                                              current_user.city,
        #                                              current_user.contact,
        #                                              current_user.street,
        #                                              "get_turkish_payment_response_manual_renew")
        #         add_order_record = add_order_record_from_current_user(current_user.id)
        #
        #     pass
        # else:
        #     return redirect("/")
    except Exception as Error:
        print(Error)
        return redirect("/")
    return redirect("/")



def cleanup(session):
    """
    This method cleans up the session object and also closes the connection pool using the dispose method.
    """
    session.close()
    engine_container.dispose()


from renew_subscription.renew_saudi_turkiy_subscription import renew
from renew_subscription.renew_india_subscription import renew
from payment_card.payment_card import card
from turkish_subscription import DemoToEnterprise
from request_api import req_api
from sqs_system import sqsRoute
from malaysia_subscription import malaysia_sub
from ChangeCard import changeCard
from admin_panel import admin_panel
from cancel_delete_subscription import cs





app.register_blueprint(renew)
app.register_blueprint(card)
app.register_blueprint(DemoToEnterprise)
app.register_blueprint(req_api)
app.register_blueprint(sqsRoute)
app.register_blueprint(malaysia_sub)
app.register_blueprint(changeCard)
app.register_blueprint(admin_panel)
app.register_blueprint(cs)






@app.route('/test_payment_myr')
def test_payment_myr():
    return render_template('payment_test.html')


# @app.route('/change_country_development/<string:get_ip>', methods=['POST', 'GET'])
# def change_country_development(get_ip):
#     try:
#         country_session = ""
#         if 1 > 0:
#             print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ call database ^^^^^^^^^^^^^^^^^^^^^^^^^^")
#             #ip_address = request.remote_addr
#             ip_address = get_ip
#             get_country_code = get_country_code_function(ip_address)
#             print(get_country_code)
#             if get_country_code == "SA":
#                 country_session = "SAU"
#             elif get_country_code == "IN":
#                 country_session = "IND"
#             elif get_country_code == "MY":
#                 country_session = "MYS"
#             elif get_country_code == "TR":
#                 country_session = "TUR"
#             elif get_country_code == "GE":
#                 country_session = "GEO"
#             elif get_country_code == "EG":
#                 country_session = "EGY"
#             elif get_country_code == "Error":
#                 return redirect('/error')
#             else:
#                 country_session = "GLB"
#         else:
#             country_session = session['country_code']
#         session['country_code'] =  country_session
#         get_google_script = Countries.query.filter_by(
#             country_code=session['country_code']).first()
#         default_lang = get_google_script.default_language
#         languages = get_google_script.language
#         languages_list = json.loads(languages)
#         session['language']= default_lang
#         if session['language'] in languages_list:
#             try:
#                 session['language'] = session['second_lang']
#             except:
#                 session["language"] = default_lang
#         else:
#             session["language"] = default_lang
#         print(type(languages_list))
#         google_script_id = get_google_script.google_script.find("id=")
#         final_get_google_script = get_google_script.google_script[google_script_id:google_script_id+17]
#         final_script = final_get_google_script.replace('"', '').replace("id=", '').replace(">", '')
#         print(session['country_code'])
#         return redirect('/')
#     except Exception as Error:
#         print(Error)
#         return redirect('/error')



#---->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> -------------------<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<---------------
#|                                                                                                                                                 |
#|                                                               Admin panel code for vue                                                           |                                                        |
#--------------------------------------------------------------------------------------------------------------------------------------------------|
#
# #generate token
# def generateTokenCustom(name, email):
#     '''generate token by jwt and bcrypt '''
#     try:
#         #        create custom random code
#         random_code = random.randint(1,10000000000000000000000000000000000)
#         #       hashing random code by bcrypt password hash
#         random_code_hash = bcrypt.generate_password_hash(str(random_code)).decode("utf-8")
#         #       create jwt token
#         data = jwt.encode({
#             'name':name ,
#             'email':email,
#             'code': random_code_hash
#         },app.config['SECRET_KEY'],algorithm="HS256")
#         return data
#     except Exception as error:
#         print(error)
#         return {"status":"FAILED"}
#
#
# def generateTokenCustomForSessions(name, email):
#     '''generate token for session by jwt and bcrypt '''
#     try:
#         #        create custom random code
#         random_code = random.randint(1,10000000000000000000000000000000000000)
#         #       hashing random code by bcrypt password hash
#         random_code_hash = bcrypt.generate_password_hash(str(random_code)).decode("utf-8")
#         #       create jwt token
#         data = jwt.encode({
#             'name':name ,
#             'email':email,
#             'code': random_code_hash
#         },app.config['SECRET_KEY'],algorithm="HS256")
#         return data
#     except Exception as error:
#         print(error)
#         return {"status":"FAILED"}
#
# #---------------------------------------------------------------------------------------------------------------------------
# @app.route('/checkAuthentication', methods=['POST'])
# def checkAuthentication(access_token, session_token):
#     try:
#         get_access_token = access_token
#         get_session_token = session_token
#         check_user = Sessions.query.filter_by(access_token=get_access_token).first()
#         if check_user:
#             check_session = Sessions.query.filter_by(session_token=get_session_token).first()
#             if check_session:
#                 return {"status":"success",
#                         "user_id":check_session.subscription_id}
#             else:
#                 return {"status":"invalid session"}
#         else:
#             return {"status": "invalid_user_authentication"}
#     except Exception as error:
#         print(error)
#         return {"status":"Failed"}
#
#
#
# @app.route('/checkAuthentication', methods=['POST'])
# def checkAuthenticationForadmin(access_token, session_token):
#     try:
#         get_access_token = access_token
#         get_session_token = session_token
#         check_user = Sessions.query.filter_by(access_token=get_access_token).first()
#         if check_user:
#             check_session = Sessions.query.filter_by(session_token=get_session_token).first()
#             if check_session:
#                 return {"status":"success",
#                         "user_id":check_session.user_id}
#             else:
#                 return {"status":"invalid session"}
#         else:
#             return {"status": "invalid_user_authentication"}
#     except Exception as error:
#         print(error)
#         return {"status":"Failed"}
#
#
# @app.route('/checkAuthenticationforJsonApi', methods=['POST'])
# def checkAuthenticationforJsonApi():
#     try:
#         get_data = request.json
#         get_access_token = get_data['access_token']
#         get_session_token = get_data['access_session']
#         check_user = Sessions.query.filter_by(access_token=get_access_token).first()
#         if check_user:
#             check_session = Sessions.query.filter_by(session_token=get_session_token).first()
#             get_user_permission = Users.query.filter_by(id=check_session.user_id).first()
#             if check_session and  get_user_permission:
#                 print(get_user_permission.permission)
#                 return {"status":"success", "permission": get_user_permission.permission}
#             else:
#                 print("invalid session")
#                 return {"status":"invalid session"}
#         else:
#             print("invalid invalid_user_authentication")
#
#             return {"status": "invalid_user_authentication"}
#     except Exception as error:
#         print(error)
#         return {"status":"Failed"}
#
#
# @app.route('/checkAuthenticationForSite', methods=['POST'])
# def checkAuthenticationForSite():
#     try:
#         get_data = request.json
#         get_access_token = get_data['access_token']
#         get_session_token = get_data['access_session']
#         check_user = Sessions.query.filter_by(access_token=get_access_token).first()
#         if check_user:
#             check_session = Sessions.query.filter_by(session_token=get_session_token).first()
#             if check_session:
#                 return {"status":"success",
#                         "user_id":check_session.subscription_id}
#             else:
#                 return {"status":"invalid session"}
#         else:
#             return {"status": "invalid_user_authentication"}
#     except Exception as error:
#         print(error)
#         return {"status":"Failed"}
#
#     #----------------------------------------------------------------------------------------------------------------
#
# # customers
#
# def check_country_available_for_user(user_id):
#     '''this function to return list country available for user or admin. for example ["SAU","TUR","MYS"]'''
#     try:
#         check_data = Users.query.filter_by(id = user_id).first()
#         if check_data:
#             is_saudi = check_data.is_saudi
#             is_turkey = check_data.is_turkey
#             is_india = check_data.is_india
#             is_malaysia = check_data.is_malaysia
#             is_global = check_data.is_global
#             is_egypt = check_data.is_egypt
#             is_georgia = check_data.is_georgia
#             if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
#                 countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
#             elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
#                 countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
#             elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
#                 countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
#             elif is_saudi and is_turkey and is_india and is_malaysia:
#                 countries = ["SAU", "TUR", "IND", "MYS"]
#             elif is_saudi and is_turkey and is_india:
#                 countries = ["SAU", "TUR", "IND"]
#             elif is_saudi and is_turkey:
#                 countries = ["SAU", "TUR"]
#             elif is_saudi:
#                 countries = ["SAU"]
#             elif is_turkey:
#                 countries = ["TUR"]
#             elif is_india:
#                 countries = ["IND"]
#             elif is_malaysia:
#                 countries = ["MYS"]
#             elif is_egypt:
#                 countries = ["EGY"]
#             elif is_global:
#                 countries = ["GLB"]
#             elif is_georgia:
#                 countries = ["GEO"]
#             else:
#                 countries = []
#             return countries
#     except Exception as Error:
#         pass
#
# def check_reg_code(country):
#     if country == "Saudi Arabia":
#         return {"country_code_3d": "SAU", "country_code_2d": "SA" }
#     elif country == "India":
#         return {"country_code_3d": "IND", "country_code_2d": "IN" }
#     elif country == "Turkey":
#         return {"country_code_3d": "TUR", "country_code_2d": "TR" }
#     elif country == "Malaysia":
#         return {"country_code_3d": "MYS", "country_code_2d": "MY" }
#     elif country == "Egypt":
#         return {"country_code_3d": "EGY", "country_code_2d": "EG" }
#     elif country == "Georgia":
#         return {"country_code_3d": "GEO", "country_code_2d": "GO" }
#     else:
#         return {"country_code_3d": "GLB", "country_code_2d": "GL" }
#
#
# @app.route('/create_new_subscription_from_admin', methods=['POST', 'GET'])
# def create_new_subscription_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", get_data)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 name = get_data['name']
#                 email = get_data['email']
#                 if Subscription.query.filter_by(email = email).first():
#                     print("emil exists")
#                     return {"status": "emailAlreadyExist"}
#                 else:
#                     stores_number = get_data['stores_number']
#                     reg_code = get_data['reg_code']
#                     city = get_data['city']
#                     contact = get_data['contact']
#                     password = get_data['password']
#                     file_taxes = get_data['file_taxes']
#                     commercial_register = get_data['commercial_register']
#                     country = get_data['country']
#                     sub_type = get_data['sub_type']
#                     street = get_data['street']
#                     postcode = get_data['postcode']
#                     company_string_name = get_data['company_string_name']
#                     country_code = check_reg_code(country)
#                     database_random_code = random.randint(1,1000000)
#                     company_token = str(random.randint(1,100000000000000000000))
#                     reg_code_full = str(country_code['country_code_3d']) + '_'+str(reg_code)+'_'+str(database_random_code)
#                     password_hash = bcrypt.generate_password_hash(password)
#                     plan_type = ""
#                     price = ""
#                     if get_data['sub_type'] == "Enterprise":
#                         get_package_price = Packages.query.filter(and_(Packages.country_code == country_code['country_code_3d'], Packages.pos_no == stores_number, Packages.type == get_data['subscription'])).first()
#                         plan_type = get_data['subscription']
#                         price = get_package_price.price
#                     else:
#                         plan_type = ""
#                     data = Subscription(name,email,
#                                         stores_number,reg_code_full,'10',
#                                         city,contact,datetime.now(),password,
#                                         file_taxes,commercial_register,
#                                         datetime.now()+timedelta(30),datetime.now(),
#                                         country,sub_type,street,postcode,password_hash,
#                                         company_string_name,"Admin_panel",company_token,"","","","")
#                     db.session.add(data)
#                     db.session.commit()
#                     data.db_status = "Activated"
#                     data.account_type = "live"
#                     data.country_code_id = country_code['country_code_3d']
#                     data.subscription_type = sub_type
#                     data.plan_type = plan_type
#                     data.price = price
#                     data.subscription_created_from = "Admin_panel"
#                     db.session.commit()
#                     print("success33333333333333333333333")
#                     return {"status":"Success"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status":"unauth"}
#
#
# @app.route('/get_subscription_data_from_admin', methods=['POST', 'GET'])
# def get_subscription_data_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", get_data)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success':
#                 get_subscription_data = Subscription.query.filter_by(id= get_data['subscription_id']).first()
#                 get_subscription_orders = Order.query.filter_by(subscription_id = get_data['subscription_id']).all()
#                 if get_subscription_data and get_subscription_data.country_code_id in check_country_available_for_user(get_admin_data.id):
#                     all_orders = []
#                     for rec in get_subscription_orders:
#                         all_orders.append({"name": rec.name,
#                                            "email": rec.email,
#                                            "order_date": rec.order_date,
#                                            "expire_date": rec.expire_db,
#                                            "trans_ref":rec.tans_ref,
#                                            "status": rec.auto_payment_status,
#                                            "amount": rec.amount})
#                     print(all_orders)
#                     return {"status": "Success",
#                             "name" : get_subscription_data.name,
#                             "email" : get_subscription_data.email,
#                             "subscription_type" : get_subscription_data.subscription_type,
#                             "stores_number" : get_subscription_data.stores_number,
#                             "reg_code" : get_subscription_data.business_name,
#                             "best_time_call" :get_subscription_data.best_time_call,
#                             "city" : get_subscription_data.city,
#                             "contact" : get_subscription_data.contact,
#                             "company_string_name" : get_subscription_data.company_string_name,
#                             "commercial_register" : get_subscription_data.commercial_register,
#                             "country" : get_subscription_data.Country,
#                             "street" : get_subscription_data.street,
#                             "postcode" : get_subscription_data.postcode,
#                             "tax_file" : get_subscription_data.tax_file,
#                             "password" : get_subscription_data.password,
#                             "subscription" : get_subscription_data.plan_type,
#                             "price":get_subscription_data.price,
#                             "sub_date": get_subscription_data.db_create_date.strftime("%m/%d/%Y"),
#                             "expire_date": str(get_subscription_data.expire_db.strftime("%Y-%m-%d")),
#                             "Orders":all_orders
#                             }
#                 else:
#                     return {"status": "Invalid"}
#             else:
#                 return {"status": "unAuth"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#
#     else:
#         return {"status": "Error"}
#
#
#
# @app.route('/get_price_of_package_admin', methods=['POST'])
# def get_price_of_package_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", get_data)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success' and get_admin_data.permission != "user":
#                 get_country_code = check_reg_code(get_data['country'])
#                 get_package = Packages.query.filter(and_(Packages.country_code == get_country_code['country_code_3d'], Packages.pos_no == get_data['pos_no'], Packages.type == get_data['subscription'])).first()
#                 print("ok")
#                 return {"status": "Success" , "price": get_package.price, "currency": get_package.currency_en}
#             else:
#                 return {"status":"Error"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "Error"}
#
#
# @app.route('/update_subscription_data_from_admin', methods=['POST', 'GET'])
# def update_subscription_data_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", get_data)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 get_subscription_object = Subscription.query.filter_by(id = get_data['subscription_id']).first()
#                 if get_subscription_object:
#                     get_subscription_object.name = get_data['name']
#                     get_subscription_object.email = get_data['email']
#                     get_subscription_object.best_time_call = get_data['best_time_call']
#                     get_subscription_object.city = get_data['city']
#                     get_subscription_object.contact = get_data['contact']
#                     get_subscription_object.company_string_name = get_data['company_string_name']
#                     get_subscription_object.commercial_register = get_data['commercial_register']
#                     get_subscription_object.street = get_data['street']
#                     get_subscription_object.postcode = get_data['postcode']
#                     get_subscription_object.tax_file = get_data['tax_file']
#                     get_subscription_object.password = get_data['password']
#                     get_subscription_object.password_hash = bcrypt.generate_password_hash(get_data['password'])
#                     db.session.commit()
#                     return {"status": "Success"}
#                 else:
#                     return {"status": "Error", "message":"the subscription id not found in cashierme"}
#             else:
#                 return {"status": "Invalid", "message":"you dont have permission to update subscription information. please contact with administrator "}
#         except Exception as Error:
#             return {"status": "Exception_error", "message": str(Error)}
#     else:
#         return {"status": "unAuth", "message": "unAuthorized"}
#
#
#
#
#
#
# @app.route('/delete_customer_from_admin', methods=['POST', 'GET'])
# def delete_customer_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 get_user_data = Subscription.query.filter_by(id = get_data['customer_id']).first()
#                 db.session.delete(get_user_data)
#                 db.session.commit()
#                 return {"status": "Success"}
#             else:
#                 return {"status": "Error"}
#
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "Error"}
#
#
#
# def check_user_email_exist(email):
#     try:
#         get_data = Users.query.filter_by(email = email).first()
#         if get_data:
#             return {"status": "Exist"}
#         else:
#             return {"status": "dontExist"}
#
#     except Exception as Error:
#         print(Error)
#         return {"status", str(Error)}
#
# def generateTokenCustomForUsers(name, email):
#     '''generate token by jwt and bcrypt '''
#     try:
#         #        create custom random code
#         random_code = random.randint(1,10000000000000000000000000000000000)
#         #       hashing random code by bcrypt password hash
#         random_code_hash = bcrypt.generate_password_hash(str(random_code)).decode("utf-8")
#         #       create jwt token
#         data = jwt.encode({
#             'name':name ,
#             'email':email,
#             'code': random_code_hash
#         },app.config['SECRET_KEY'],algorithm="HS256")
#         return data
#     except Exception as error:
#         print(error)
#         return {"status":"FAILED"}
#
#
#
# @app.route('/add_new_user_admin', methods=['POST', 'GET'])
# def add_new_user_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         try:
#             get_data = request.json
#             get_name = get_data['name']
#             name = get_name.replace(".", "_")
#             email = get_data['email']
#             password = get_data['password']
#             gender = get_data['gender']
#             job_grade = get_data['job_grade']
#             mobile = get_data['mobile']
#             country = get_data['country']
#             address = get_data['address']
#             permisions = get_data['permisions']
#             saudi = get_data['saudi']
#             turkish = get_data['turkish']
#             india = get_data['india']
#             malysia = get_data['malaysia']
#             is_global = get_data['global']
#             egypt = get_data['egypt']
#             georgia = get_data['georgia']
#             activity = get_data['activity']
#             checkEmail = check_user_email_exist(email)
#             if checkEmail['status'] == "Exist":
#                 print("email Exists")
#                 return {"status": "EmailExit"}
#             elif checkEmail['status'] == "dontExist":
#                 try:
#                     add_data = Users(name,email,bcrypt.generate_password_hash(password).decode('utf-8'),country,address,mobile,gender,job_grade,activity)
#                     db.session.add(add_data)
#                     db.session.commit()
#                     add_data.is_georgia = georgia
#                     add_data.is_egypt = egypt
#                     add_data.is_global = is_global
#                     add_data.is_malaysia = malysia
#                     add_data.is_india = india
#                     add_data.is_turkey = turkish
#                     add_data.is_saudi = saudi
#                     add_data.permission = permisions
#                     db.session.commit()
#                     session_token = generateTokenCustomForUsers(str(name), str(email))
#                     access_token = generateTokenCustomForUsers(str(name), str(email))
#                     add_session = Sessions(add_data.id, None, name,access_token,session_token,datetime.now(),'Admin')
#                     db.session.add(add_session)
#                     db.session.commit()
#                     return {"status": "Success"}
#                 except Exception as Error:
#                     print(Error)
#             else:
#                 return {"status": "Error"}
#         except Exception as Error:
#             print(Error)
#     else:
#         return {"status": "Error"}
#     return {"status": "Error"}
#
#
#
# @app.route('/SubmitAdminLogin', methods=['POST', 'GET'])
# def SubmitLoginAdmin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print ("auth")
#         try:
#             get_data = request.json
#             get_email = get_data['email']
#             get_password = get_data['password']
#             print(get_data)
#             check_data = Users.query.filter_by(email = str(get_email)).first()
#             if check_data and bcrypt.check_password_hash(check_data.password, get_password):
#                 get_logger_function('SubmitAdminLogin', 'info',
#                                     'success check data',
#                                     'cashier me site')
#                 print("ok")
#                 get_tokens = Sessions.query.filter(and_(Sessions.user_id == check_data.id, Sessions.account_type == "Admin")).first()
#                 print("get_token",get_tokens)
#                 create_new_session = generateTokenCustomForUsers(check_data.user_name, check_data.email)
#                 get_tokens.session_token = create_new_session
#                 get_tokens.update_date = datetime.now()
#                 db.session.commit()
#                 access_token = get_tokens.access_token
#                 session_token = get_tokens.session_token
#                 return {"status":"success",
#                         "access_token":access_token,
#                         "session_token": session_token,
#                         "activity": check_data.activate
#                         }
#             else:
#                 print({"status":"invalid"})
#                 return {"status":"invalid"}
#         except Exception as Error:
#             get_logger_function('SubmitAdminLogin', 'error',
#                                 'success check data'+str(Error),
#                                 'cashier me site')
#
#             print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>',Error)
#             return {"status":"Faield"}
#     else:
#         print({"status":"Faield"}, "Error")
#         return {"status": "Faield"}
#
#
#
# def check_country_available_for_user(user_id):
#     '''this function to return list country available for user or admin. for example ["SAU","TUR","MYS"]'''
#     try:
#         check_data = Users.query.filter_by(id = user_id).first()
#         if check_data:
#             is_saudi = check_data.is_saudi
#             is_turkey = check_data.is_turkey
#             is_india = check_data.is_india
#             is_malaysia = check_data.is_malaysia
#             is_global = check_data.is_global
#             is_egypt = check_data.is_egypt
#             is_georgia = check_data.is_georgia
#             if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
#                 countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
#             elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
#                 countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
#             elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
#                 countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
#             elif is_saudi and is_turkey and is_india and is_malaysia:
#                 countries = ["SAU", "TUR", "IND", "MYS"]
#             elif is_saudi and is_turkey and is_india:
#                 countries = ["SAU", "TUR", "IND"]
#             elif is_saudi and is_turkey:
#                 countries = ["SAU", "TUR"]
#             elif is_saudi:
#                 countries = ["SAU"]
#             elif is_turkey:
#                 countries = ["TUR"]
#             elif is_india:
#                 countries = ["IND"]
#             elif is_malaysia:
#                 countries = ["MYS"]
#             elif is_egypt:
#                 countries = ["EGY"]
#             elif is_global:
#                 countries = ["GLB"]
#             elif is_georgia:
#                 countries = ["GEO"]
#             else:
#                 countries = []
#             return countries
#     except Exception as Error:
#         pass
#
#
#
#
#
#
#
# @app.route('/get_all_countries', methods=['POST', 'GET'])
# def get_all_countries():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success' :
#                 is_saudi = get_admin_data.is_saudi
#                 is_turkey = get_admin_data.is_turkey
#                 is_india = get_admin_data.is_india
#                 is_malaysia = get_admin_data.is_malaysia
#                 is_global = get_admin_data.is_global
#                 is_egypt = get_admin_data.is_egypt
#                 is_georgia = get_admin_data.is_georgia
#                 if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
#                     countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
#                 elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
#                     countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
#                 elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
#                     countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
#                 elif is_saudi and is_turkey and is_india and is_malaysia:
#                     countries = ["SAU", "TUR", "IND", "MYS"]
#                 elif is_saudi and is_turkey and is_india:
#                     countries = ["SAU", "TUR", "IND"]
#                 elif is_saudi and is_turkey:
#                     countries = ["SAU", "TUR"]
#                 elif is_saudi:
#                     countries = ["SAU"]
#                 elif is_turkey:
#                     countries = ["TUR"]
#                 elif is_india:
#                     countries = ["IND"]
#                 elif is_malaysia:
#                     countries = ["MYS"]
#                 elif is_egypt:
#                     countries = ["EGY"]
#                 elif is_global:
#                     countries = ["GLB"]
#                 elif is_georgia:
#                     countries = ["GEO"]
#                 else:
#                     countries = []
#                 get_all_countries = Countries.query.filter(Countries.country_code.in_(countries)).all()
#                 all_countries = []
#                 for data in get_all_countries:
#                     print(data.country_name)
#                     all_countries.append({"id":data.id,"country_name": data.country_name,"code_3d": data.country_code,
#                                           "code_2d": data.country_code, "currency":data.currency,
#                                           "language": data.language,"default_language":data.default_language,
#                                           "monthly_amount":data.monthly_amount,"annually_amount":data.annually_amount,"payment_getway":data.payment_getway})
#                 return {"status": "Success","data": all_countries}
#
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "Error"}
#
#
# def create_package_record_from_admin(pos_no,monthly_price,annually_price,en_string,ar_string,currency_en,currency_ar,country_code):
#     packages_delete = Packages.query.filter_by(country_code = country_code).all()
#     print("ok")
#     for data in packages_delete:
#         db.session.delete(data)
#         db.session.commit()
#     print("ok")
#     month = 'Monthly'
#     year = 'yearly'
#     monthly_price = monthly_price
#     annually_price = annually_price
#     en_string = en_string
#     ar_string = ar_string
#     currency_en = currency_en
#     currency_ar = currency_ar
#     country_code = country_code
#     for data in range(pos_no):
#         get_code = data
#         get_price_month = int(monthly_price) * int(data)
#         get_price_year = int((int(annually_price) * int(data))*12)
#         add_packages_month = Packages(get_price_month,str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,month,currency_en,currency_ar,str(get_code),get_code, country_code)
#         add_packages_year = Packages(get_price_year,str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,year,currency_en,currency_ar,str(get_code),get_code ,country_code)
#         db.session.add(add_packages_month)
#         db.session.commit()
#         db.session.add(add_packages_year)
#         db.session.commit()
#     return {"status": "Success"}
#
#
# @app.route('/add_new_country_from_admin', methods=['POST'])
# def add_new_country_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin ()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             print (check_auth)
#             if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 print("developer auth>>>>>>>>>>>>>>>>")
#                 country_name = get_data['country_name']
#                 currency = get_data['currency']
#                 monthly_amount = get_data['monthly_amount']
#                 annually_amount = get_data['annually_amount']
#                 country_3d_code = get_data['country_3d_code']
#                 country_2d_code = get_data['country_2d_code']
#                 default_language = get_data['default_language']
#                 payment_getway = get_data['payment_getway']
#                 all_language = get_data['all_language']
#                 payment_merchant_id = get_data['payment_merchant_id']
#                 payment_currency = get_data['payment_currency']
#                 payment_api_url = get_data['payment_api_url']
#                 payment_api_key = get_data['payment_api_key']
#                 payment_query_url = get_data['payment_query_url']
#                 usd_convert = get_data['usd_convert']
#                 data = Countries(country_3d_code,country_2d_code,
#                                  country_name,all_language,
#                                  default_language,currency,
#                                  monthly_amount,annually_amount,payment_getway,
#                                  payment_merchant_id,payment_currency,payment_api_url,
#                                  payment_api_key,payment_query_url)
#                 db.session.add(data)
#                 db.session.commit()
#                 create_package_record_from_admin(100,monthly_amount,annually_amount,"POS","",currency,currency,country_2d_code)
#                 print("Success add country record")
#                 return {"status": "Success"}
#             else:
#                 return {"status": "notHavePermission"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "unAuth"}
#
#
# @app.route('/delete_country_from_admin', methods=['POST', 'GET'])
# def delete_country_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 get_country_data = Countries.query.filter_by(id = get_data['country_id']).first()
#                 delete_packages = Packages.query.filter_by(country_code = get_country_data.country_code_2d).all()
#                 for data in delete_packages:
#                     db.session.delete(data)
#                     db.session.commit()
#                 db.session.delete(get_country_data)
#                 db.session.commit()
#
#                 return {"status": "Success"}
#             else:
#                 return {"status": "Error", "message": "You don,t have permission to do that please contact with administrator"}
#
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error", "message": str(Error)}
#     else:
#         return {"status": "Error", "message": "cannot process your request now please contact with administrator"}
#
#
# @app.route('/get_country_data_from_admin', methods=['POST', 'GET'])
# def get_country_data_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success':
#                 get_country_available = check_country_available_for_user(get_admin_data.id)
#                 get_countries = Countries.query.filter_by(id = get_data['country_code']).first()
#                 if get_countries.country_code in get_country_available:
#                     country_name  = get_countries.country_name
#                     currency  = get_countries.currency
#                     monthly_amount  = get_countries.monthly_amount
#                     annually_amount  = get_countries.annually_amount
#                     country_3d_code  = get_countries.country_code
#                     country_2d_code  = get_countries.country_code_2d
#                     default_language  = get_countries.default_language
#                     payment_getway  = get_countries.payment_getway
#                     all_language  = get_countries.language
#                     payment_merchant_id  = get_countries.payment_merchant_id
#                     payment_currency  = get_countries.payment_currency
#                     payment_api_url  = get_countries.payment_request_api_url
#                     payment_api_key  = get_countries.payment_api_key
#                     payment_query_url  = get_countries.payment_query_link
#                     usd_convert  = get_countries.usd_convert
#                     print("Success", get_countries.country_name,
#                           )
#                     return {"status": "Success",
#                             "country_name": country_name,
#                             "currency": currency,
#                             "monthly_amount": monthly_amount,
#                             "annually_amount": annually_amount,
#                             "country_3d_code": country_3d_code,
#                             "country_2d_code": country_2d_code,
#                             "default_language": default_language,
#                             "payment_getway": payment_getway,
#                             "all_language": all_language,
#                             "payment_merchant_id": payment_merchant_id,
#                             "payment_currency": payment_currency,
#                             "payment_api_url": payment_api_url,
#                             "payment_api_key": payment_api_key,
#                             "payment_query_url": payment_query_url,
#                             "usd_convert": usd_convert,}
#                 else:
#                     return {"status": "unAuthCountry"}
#             else:
#                 return {"status": "unAuth"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "Error"}
#
#
# @app.route('/update_country_data_from_admin', methods=['POST', 'GET'])
# def update_country_data_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             get_country_data = Countries.query.filter_by(id = get_data['country_code']).first()
#             if check_auth['status'] == 'success' and get_admin_data.permission == "manager":
#                 get_country_data.monthly_amount = get_data['monthly_amount']
#                 get_country_data.annually_amount = get_data['annually_amount']
#                 db.session.commit()
#                 create_package_record_from_admin(100,get_data['monthly_amount'],get_data['annually_amount'],"POS","",get_data['payment_currency'],get_data['payment_currency'],get_data['country_2d_code'])
#                 return {"status": "Success"}
#             elif check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 get_country_data.country_name = get_data['country_name']
#                 get_country_data.currency = get_data['currency']
#                 get_country_data.monthly_amount = get_data['monthly_amount']
#                 get_country_data.annually_amount = get_data['annually_amount']
#                 get_country_data.country_code = get_data['country_3d_code']
#                 get_country_data.country_code_2d = get_data['country_2d_code']
#                 get_country_data.default_language = get_data['default_language']
#                 get_country_data.payment_getway = get_data['payment_getway']
#                 get_country_data.language = get_data['all_language']
#                 get_country_data.payment_merchant_id = get_data['payment_merchant_id']
#                 get_country_data.payment_currency = get_data['payment_currency']
#                 get_country_data.payment_request_api_url = get_data['payment_api_url']
#                 get_country_data.payment_api_key = get_data['payment_api_key']
#                 get_country_data.payment_query_link = get_data['payment_query_url']
#                 get_country_data.usd_convert = get_data['usd_convert']
#                 db.session.commit()
#                 create_package_record_from_admin(100,get_data['monthly_amount'],get_data['annually_amount'],"POS","",get_data['payment_currency'],get_data['payment_currency'],get_data['country_2d_code'])
#
#                 return {"status": "Success"}
#             else:
#                 return {"status": "Error", "message": "You don,t have permission to do that please contact with administrator"}
#
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error", "message": str(Error)}
#     else:
#         return {"status": "Error", "message": "cannot process your request now please contact with administrator"}
#
#
#
#
#
# @app.route('/getAllSubscription', methods=['POST'])
# def getAllSubscription():
#     check_auth_value = verify_auth_api.check_header_auth_admin ()
#     if check_auth_value == "Auth":
#         print ("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             print (check_auth)
#             if check_auth['status'] == 'success':
#                 countries = None
#                 permission = get_user_data.permission
#                 account_status = get_user_data.activate
#                 is_saudi = get_user_data.is_saudi
#                 is_turkey = get_user_data.is_turkey
#                 is_india = get_user_data.is_india
#                 is_malaysia = get_user_data.is_malaysia
#                 is_global = get_user_data.is_global
#                 is_egypt = get_user_data.is_egypt
#                 is_georgia = get_user_data.is_georgia
#
#                 if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
#                     countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
#                 elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
#                     countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
#                 elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
#                     countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
#                 elif is_saudi and is_turkey and is_india and is_malaysia:
#                     countries = ["SAU", "TUR", "IND", "MYS"]
#                 elif is_saudi and is_turkey and is_india:
#                     countries = ["SAU", "TUR", "IND"]
#                 elif is_saudi and is_turkey:
#                     countries = ["SAU", "TUR"]
#                 elif is_saudi:
#                     countries = ["SAU"]
#                 elif is_turkey:
#                     countries = ["TUR"]
#                 elif is_india:
#                     countries = ["IND"]
#                 elif is_malaysia:
#                     countries = ["MYS"]
#                 elif is_egypt:
#                     countries = ["EGY"]
#                 elif is_global:
#                     countries = ["GLB"]
#                 elif is_georgia:
#                     countries = ["GEO"]
#                 else:
#                     countries = []
#                 print(countries)
#                 user_name = get_user_data
#                 if account_status:
#                     all_subscription = []
#                     get_subscription_record = Subscription.query.filter(Subscription.country_code_id.in_(countries)).all()
#                     get_len_demo = len(Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_type == "Demo")).all())
#                     get_len_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_type == "Enterprise")).all())
#                     get_len_cancel = len(Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_status == "Cancel")).all())
#                     get_len_all = len(get_subscription_record)
#                     len_saudi_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "SAU", Subscription.subscription_type =="Demo" )).all())
#                     len_saudi_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "SAU", Subscription.subscription_type =="Enterprise" )).all())
#                     len_egypt_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "EGY", Subscription.subscription_type =="Demo" )).all())
#                     len_egypt_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "EGY", Subscription.subscription_type =="Enterprise" )).all())
#                     len_global_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "GLB", Subscription.subscription_type =="Demo" )).all())
#                     len_global_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "GLB", Subscription.subscription_type =="Enterprise" )).all())
#                     len_turkey_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "TUR", Subscription.subscription_type =="Demo" )).all())
#                     len_turkey_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "TUR", Subscription.subscription_type =="Enterprise" )).all())
#                     len_india_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "IND", Subscription.subscription_type =="Demo" )).all())
#                     len_india_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "IND", Subscription.subscription_type =="Enterprise" )).all())
#                     len_malaysia_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "MYS", Subscription.subscription_type =="Demo" )).all())
#                     len_malaysia_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "MYS", Subscription.subscription_type =="Enterprise" )).all())
#                     len_georgia_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "GEO", Subscription.subscription_type =="Demo" )).all())
#                     len_georgia_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "GEO", Subscription.subscription_type =="Enterprise" )).all())
#                     for data in get_subscription_record:
#                         cs_name = data.name
#                         cs_email = data.email
#                         cs_company_name = data.company_string_name
#                         cs_contact = data.contact
#                         cs_pos_no = data.stores_number
#                         cs_reg_code = data.business_name
#                         cs_sub_type = data.subscription_type
#                         cs_sub_status = data.db_status
#                         cs_creation_date = data.db_create_date.strftime("%b %d %Y"),
#                         cs_city = data.city
#                         cs_street = data.street
#                         cs_country = data.Country
#                         cs_tax_file = data.tax_file
#                         cs_commercial_reg = data.commercial_register
#                         cs_expire_db = data.expire_db.strftime("%b %d %Y"),
#                         cs_order_id = data.order_id
#                         cs_postcode = data.postcode
#                         cs_plan_type = data.plan_type
#                         cs_subscription_status = data.subscription_status
#                         cs_country_code = data.country_code_id
#                         cs_activity = data.is_active
#                         all_subscription.append({"id":data.id,"cs_name":cs_name,
#                                                  "cs_email": cs_email,
#                                                  "cs_company_name": cs_company_name,
#                                                  "cs_contact": cs_contact,
#                                                  "cs_pos_no":cs_pos_no,
#                                                  "cs_reg_code": cs_reg_code,
#                                                  "cs_sub_type": cs_sub_type,
#                                                  "cs_sub_status": cs_sub_status,
#                                                  "cs_creation_date": cs_creation_date,
#                                                  "cs_city": cs_city,
#                                                  "cs_street": cs_street,
#                                                  "cs_country":cs_country,
#                                                  "cs_tax_file": cs_tax_file,
#                                                  "cs_commercial_reg": cs_commercial_reg,
#                                                  "cs_expire_db": cs_expire_db,
#                                                  "cs_order_id": cs_order_id,
#                                                  "cs_postcode": cs_postcode,
#                                                  "cs_plan_type": cs_plan_type,
#                                                  "cs_subscription_status": cs_subscription_status,
#                                                  "cs_country_code": cs_country_code,
#                                                  "cs_activity": cs_activity,
#                                                  })
#                     return {"all_sub":get_len_all,
#                             "demo_sub":get_len_demo,
#                             "enterprise_sub":get_len_enterprise,
#                             "cancel_sub": get_len_cancel,
#                             "data":all_subscription,
#                             "user_name": get_user_data.user_name,
#                             "saudi_demo_len": len_saudi_demo,
#                             "saudi_enterprise_len": len_saudi_enterprise,
#                             "egypt_demo_len":len_egypt_demo,
#                             "egypt_enterprise_len":len_egypt_enterprise,
#                             "global_demo_len": len_global_demo,
#                             "global_enterprise_len": len_global_enterprise,
#                             "turkey_demo_len": len_turkey_demo,
#                             "turkey_enterprise_len": len_turkey_enterprise,
#                             "india_demo_len":len_india_demo,
#                             "india_enterprise_len":len_india_enterprise,
#                             "malaysia_demo_len": len_malaysia_demo,
#                             "malaysia_enterprise_len": len_malaysia_enterprise,
#                             "georgia_demo_len": len_georgia_demo,
#                             "georgia_enterprise_len": len_georgia_enterprise,
#                             }
#         except Exception as Error:
#             print(Error)
#     return {"samer": 5}
#
#
# @app.route('/delete_user_from_admin', methods=['POST', 'GET'])
# def delete_user_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 get_user_data = Users.query.filter_by(id = get_data['user_id']).first()
#                 db.session.delete(get_user_data)
#                 db.session.commit()
#                 return {"status": "Success"}
#             else:
#                 return {"status": "Error"}
#
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "Error"}
#
#
# @app.route('/forgot_password_check_email_exist', methods=['POST'])
# def forgot_password_check():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print ("auth")
#         try:
#             get_data = request.json
#             email = get_data['email']
#             data = Users.query.filter_by(email = email).first()
#             if data:
#                 data.forgot_password_code = random.randint(1, 1000000)
#                 auth_code = random.randint(1, 10000000000000000000000000000000000000000000000000)
#                 data.auth_code = auth_code
#                 data.update_date = datetime.now()+timedelta(minutes=10)
#                 db.session.commit()
#                 print("ok send auth code")
#                 return {"status": "Success", "authCode": str(auth_code)}
#                 # msg = Message("Change Account Password", recipients=[email])
#                 # msg.body = "your Code is " + ":"+ data.check_code
#                 # mail.send(msg)
#                 # return render_template('change_password.html', get_id = data.id),cleanup(db.session)
#             else:
#                 return {"status": "Failed", "message": "Email not Exist"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error", "message": "Cannot process your request now. please try again letter"}
#     else:
#         return {"status": "hack"}
#
#
# @app.route('/checkAndChangePassword', methods=['POST'])
# def change_password_email():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print ("auth")
#         try:
#             get_data = request.json
#             code= get_data['code']
#             new_password = get_data['new_password']
#             auth_code = get_data['authCode']
#             data = Users.query.filter_by(auth_code = auth_code).first()
#             if data:
#                 get_code = data.forgot_password_code
#                 if get_code == code:
#                     if data.update_date >= datetime.now():
#                         data.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
#                         db.session.commit()
#                         return {"status": "Success"}
#                     else:
#                         return {"status": "ExpireCode", "message": "Expired Code"}
#                 else:
#                     return {"status": "Invalid","message": "Invalid Code"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error", "message": "Cannot process your request now. please try again letter"}
#     else:
#         return {"status": "hack"}
#
#
# @app.route('/getAllUsers', methods=['POST'])
# def getAllUsers():
#     check_auth_value = verify_auth_api.check_header_auth_admin ()
#     if check_auth_value == "Auth":
#         print ("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             print (check_auth)
#             if check_auth['status'] == 'success':
#                 get_all_data = Users.query.all()
#                 all_data = []
#                 for rec in get_all_data:
#                     all_data.append({"id": rec.id ,"name": rec.user_name, "address": rec.address,
#                                      "mobile":rec.mobile,"email": rec.email,"last_login":rec.last_login,
#                                      "activity": rec.activate,"permission": rec.permission,
#                                      "is_saudi": rec.is_saudi,"is_turkey": rec.is_turkey,
#                                      "is_india": rec.is_india,"is_malaysia": rec.is_malaysia,
#                                      "is_global": rec.is_global,"is_egypt": rec.is_egypt,"is_georgia": rec.is_georgia,})
#                 return {"data": all_data}
#         except Exception as Error:
#             print(Error)
#             pass
#
#
# @app.route('/get_prices_from_admin', methods=['POST', 'GET'])
# def get_prices_from_admin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", get_data)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 get_available_country_code = check_country_available_for_user(get_admin_data.id)
#                 get_prices = Packages.query.filter(Packages.country_code.in_(get_available_country_code)).all()
#                 if get_prices :
#                     all_prices = []
#                     for rec in get_prices:
#                         all_prices.append({"id":rec.id,
#                                            "country_code": rec.country_code,
#                                            "price": rec.price,
#                                            "pos_no": rec.pos_no,
#                                            "currency": rec.currency_en,
#                                            "sub_type":rec.type,
#                                            "package_code": rec.pos_no_code
#                                            })
#                     return {"status": "Success", "data": all_prices}
#
#                 else:
#                     return {"status": "Invalid"}
#             else:
#                 return {"status": "unAuth"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#
#     else:
#         return {"status": "Error"}
#
# @app.route('/get_profile_data', methods=['POST'])
# def get_profile_data():
#     check_auth_value = verify_auth_api.check_header_auth_admin ()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             print (check_auth)
#             if check_auth['status'] == 'success':
#                 permission = get_user_data.permission
#                 account_status = get_user_data.activate
#                 name = get_user_data.user_name
#                 email = get_user_data.email
#                 gender = get_user_data.gender
#                 mobile = get_user_data.mobile
#                 job_grade = get_user_data.job_grade
#                 country = get_user_data.country
#                 address = get_user_data.address
#                 return {"status": "Success",
#                         "name": name,
#                         "email": email,
#                         "gender": gender,
#                         "mobile": mobile,
#                         "country": country,
#                         "address": address,
#                         "permission": permission,
#                         "activity": account_status,
#                         "job_grade":job_grade,
#                         "is_saudi": get_user_data.is_saudi,
#                         "is_turkey": get_user_data.is_turkey,
#                         "is_india": get_user_data.is_india,
#                         "is_malaysia": get_user_data.is_malaysia,
#                         "is_global": get_user_data.is_global,
#                         "is_egypt": get_user_data.is_egypt,
#                         "is_georgia": get_user_data.is_georgia}
#
#             else:
#                 return {"status": "Error"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "Error"}
#
#
# @app.route('/get_uer_profile_data', methods=['POST'])
# def get_uer_profile_data():
#     check_auth_value = verify_auth_api.check_header_auth_admin ()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             print (check_auth)
#             if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 get_user_data = Users.query.filter_by(id = get_data['user_id']).first()
#                 permission = get_user_data.permission
#                 account_status = get_user_data.activate
#                 name = get_user_data.user_name
#                 email = get_user_data.email
#                 gender = get_user_data.gender
#                 mobile = get_user_data.mobile
#                 job_grade = get_user_data.job_grade
#                 country = get_user_data.country
#                 address = get_user_data.address
#                 is_saudi = get_user_data.is_saudi
#                 is_turkey = get_user_data.is_turkey
#                 is_india = get_user_data.is_india
#                 is_malaysia = get_user_data.is_malaysia
#                 is_global = get_user_data.is_global
#                 is_egypt = get_user_data.is_egypt
#                 is_georgia = get_user_data.is_georgia
#                 return {"status": "Success","name": name,
#                         "email": email, "gender": gender,
#                         "mobile": mobile, "country": country,
#                         "address": address,"permission": permission,
#                         "activity": account_status,"job_grade":job_grade,
#                         "is_saudi": is_saudi,"is_turkey": is_turkey,
#                         "is_india": is_india,"is_malaysia": is_malaysia,
#                         "is_global": is_global,"is_egypt": is_egypt,"is_georgia": is_georgia,
#                         }
#             else:
#                 return {"status": "Error"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "Error"}
#
#
#
#
# @app.route('/updateProfileFromUser', methods=['POST', 'GET'])
# def updateProfileFromUser():
#     check_auth_value = verify_auth_api.check_header_auth_admin ()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             print(check_auth['user_id'])
#             get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             print (check_auth)
#             if check_auth['status'] == 'success':
#                 get_user_data.user_name = get_data['name']
#                 get_user_data.mobile = get_data['mobile']
#                 get_user_data.address = get_data['address']
#                 db.session.commit()
#                 return {"status": "Success"}
#             else:
#                 return {"status": "Error"}
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "Error"}
#
#
# @app.route('/updateProfileFromAdmin', methods=['POST', 'GET'])
# def updateProfileFromAdmin():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
#                 get_user_data = Users.query.filter_by(id = get_data['user_id']).first()
#                 get_user_data.user_name = get_data['name']
#                 get_user_data.email = get_data['email']
#                 get_user_data.gender = get_data['gender']
#                 get_user_data.mobile = get_data['mobile']
#                 get_user_data.job_grade = get_data['job_grade']
#                 get_user_data.country = get_data['country']
#                 get_user_data.address = get_data['address']
#                 get_user_data.permission = get_data['permissions']
#                 get_user_data.is_saudi = get_data['saudi']
#                 get_user_data.is_turkey = get_data['turkish']
#                 get_user_data.is_india = get_data['india']
#                 get_user_data.is_malaysia = get_data['malaysia']
#                 get_user_data.is_global = get_data['global']
#                 get_user_data.is_egypt = get_data['egypt']
#                 get_user_data.is_georgia = get_data['georgia']
#                 get_user_data.activate = get_data['activity']
#                 db.session.commit()
#                 return {"status": "Success"}
#             else:
#                 return {"status": "Error"}
#
#         except Exception as Error:
#             print(Error)
#             return {"status": "Error"}
#     else:
#         return {"status": "Error"}
#
#
#
#
#
#
#
# @app.route('/updatePasswordFromUserAdmin', methods=['POST', 'GET'])
# def updatePasswordFromUserAdmin():
#     check_auth_value = verify_auth_api.check_header_auth_admin ()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             old_password = get_data['old_password']
#             new_password = get_data['new_password']
#             retry_password = get_data['retry_password']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             print(check_auth['user_id'])
#             get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             print (check_auth)
#             if check_auth['status'] == 'success':
#                 if bcrypt.check_password_hash(get_user_data.password, old_password):
#                     if new_password == retry_password:
#                         get_user_data.password = bcrypt.generate_password_hash(new_password)
#                         db.session.commit()
#                         print("updated password successfully>>>>>>>>>>>>>")
#                         return {"status": "Success"}
#                     else:
#                         return {"status": "Password not matched"}
#                 else:
#                     return {"status": "Invalid old password"}
#
#             else:
#                 return {"status": "unauthorized"}
#         except Exception as Error:
#             print(Error)
#             return {"status": str(Error)}
#     else:
#         return {"status": "unauthorized"}
#
#
#
# @app.route('/updatePasswordFromAdmin', methods=['POST', 'GET'])
# def updatePasswordFromAdmin():
#     check_auth_value = verify_auth_api.check_header_auth_admin ()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             new_password = get_data['new_password']
#             retry_password = get_data['retry_password']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             print(check_auth['user_id'])
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             print (check_auth)
#             if check_auth['status'] == 'success' and  get_admin_data.permission == "developer":
#                 if new_password == retry_password:
#                     get_user_data = Users.query.filter_by(id = get_data['user_id']).first()
#                     get_user_data.password = bcrypt.generate_password_hash(new_password)
#                     db.session.commit()
#                     print("updated password successfully>>>>>>>>>>>>>")
#                     return {"status": "Success"}
#                 else:
#                     return {"status": "Password not matched"}
#             else:
#                 return {"status": "unauthorized"}
#         except Exception as Error:
#             print(Error)
#             return {"status": str(Error)}
#     else:
#         return {"status": "unauthorized"}
#
#
#     #add in 6-1-2023
# @app.route('/upgrade_demo_to_enterprise_with_admin_payment_cash', methods=['POST', 'GET'])
# def upgrade_demo_to_enterprise_with_admin_payment_cash():
#     check_auth_value = verify_auth_api.check_header_auth_admin()
#     if check_auth_value == "Auth":
#         print("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             if check_auth['status'] == 'success':
#                 customer_id = get_data['customer_id']
#                 pos_count = get_data['pos_count']
#                 receipt_voucher = get_data['receipt_voucher']
#                 subscription_type = get_data['subscription_type']
#                 get_customer_data = Subscription.query.filter_by(id=customer_id).first()
#                 expire_day_count = 0
#                 if subscription_type == 'Monthly':
#                     expire_day_count = 31
#                 elif subscription_type == 'yearly':
#                     expire_day_count = 366
#                 expire_db = datetime.now()+ timedelta(expire_day_count)
#                 date_order = datetime.now()
#                 random_code1 = random.randint(1, 100000)
#                 random_code2 = random.randint(1, 100000)
#                 transaction_ref = 'CASH'+str(random.randint(1, 10000000000))
#                 order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
#                 if get_customer_data:
#                     #update data in subscription table
#                     get_package_price = Packages.query.filter(and_(Packages.country_code == get_customer_data.country_code_id, Packages.pos_no == pos_count, Packages.type == subscription_type)).first()
#                     get_customer_data.stores_number = pos_count
#                     get_customer_data.subscription_type = "Enterprise"
#                     get_customer_data.payment_status = "Done"
#                     get_customer_data.plan_type = subscription_type
#                     get_customer_data.price = get_package_price.price
#                     get_customer_data.user_id = get_admin_data.id
#                     get_customer_data.user_name = get_admin_data.user_name
#                     get_customer_data.expire_db = expire_db
#                     db.session.commit()
#                     #create new record in order table
#                     gnerate_order_record = Order(get_customer_data.name,
#                                                  get_customer_data.email,get_customer_data.stores_number,
#                                                  get_customer_data.business_name,get_customer_data.city,
#                                                  get_customer_data.contact,get_customer_data.password,
#                                                  get_customer_data.tax_file,get_customer_data.commercial_register,
#                                                  datetime.today(),get_customer_data.street,get_customer_data.Country,
#                                                  get_customer_data.postcode,"Done",order_code,get_package_price.price,
#                                                  get_customer_data.plan_type,expire_db,get_customer_data.password_hash,get_package_price.id,get_customer_data.company_string_name)
#                     db.session.add(gnerate_order_record)
#                     db.session.commit()
#                     gnerate_order_record.account_type = "Live"
#                     gnerate_order_record.country_code_id = get_customer_data.country_code_id
#                     gnerate_order_record.auto_payment_status = "Done"
#                     gnerate_order_record.tans_ref = transaction_ref
#                     get_customer_data.order_id = gnerate_order_record.id
#                     gnerate_order_record.subscription_id = get_customer_data.id
#                     gnerate_order_record.order_id = gnerate_order_record.id
#                     gnerate_order_record.customer_token = receipt_voucher
#
#                     saller_name = 'Ultimate Solutions'
#                     seller_len = len(saller_name)
#                     vat_number = '311136332100003'
#                     dateandtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
#                     amount = str(gnerate_order_record.amount)
#                     amounts = gnerate_order_record.amount
#                     get_len = len(amount)
#                     tax = round(int(amounts)-(int(amounts) / 1.15), 2)
#                     # tax = (15 * int(amounts)) / 100
#                     get_tax_len = len(str(tax))
#                     company2hex = hexaConvertFunction.string2hex(saller_name)
#                     fullCompany2hex = '01' + str(hexaConvertFunction.int2hex(seller_len)) + company2hex
#                     vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
#                     fullnumber2hex = '020F' + vatnumber2hex
#                     datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
#                     fulldatetimehex = '0314'+ datetimeInvoicehex
#                     amount2hexa = hexaConvertFunction.string2hex(amount)
#                     fulamount2hexa = '040'+ str(get_len) + amount2hexa
#                     tax2hexa = hexaConvertFunction.string2hex(str(tax))
#                     fulltax2hexa = '050' + str(get_tax_len) + tax2hexa
#                     get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
#                     print('hexa code :>>>>>>>>>>>>>>>',fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
#                     print('base64 code >>>>>>>>>>>>>>',get_qr_base64)
#                     gnerate_order_record.qr_code_base64 = get_qr_base64
#                     db.session.commit()
#                     print("success payment")
#                     return {"status": "Success", "order_id": gnerate_order_record.id}
#                 pass
#         except Exception as error:
#             print(error)
#             return {"status": "Error", "message": str(error)}
#     else:
#         return {"status": "unAuth"}
#
#
# @app.route('/getAllSubscriptionDemoToCshPayment', methods=['POST'])
# def getAllSubscriptionDemoToCshPayment():
#     check_auth_value = verify_auth_api.check_header_auth_admin ()
#     if check_auth_value == "Auth":
#         print ("auth")
#         try:
#             get_data = request.json
#             access_token = get_data['access_token']
#             session_token = get_data['access_session']
#             print (">>>>>", session_token)
#             check_auth = checkAuthenticationForadmin(access_token, session_token)
#             get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
#             print (check_auth)
#             if check_auth['status'] == 'success':
#                 countries = None
#                 permission = get_user_data.permission
#                 account_status = get_user_data.activate
#                 is_saudi = get_user_data.is_saudi
#                 is_turkey = get_user_data.is_turkey
#                 is_india = get_user_data.is_india
#                 is_malaysia = get_user_data.is_malaysia
#                 is_global = get_user_data.is_global
#                 is_egypt = get_user_data.is_egypt
#                 is_georgia = get_user_data.is_georgia
#
#                 if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
#                     countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
#                 elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
#                     countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
#                 elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
#                     countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
#                 elif is_saudi and is_turkey and is_india and is_malaysia:
#                     countries = ["SAU", "TUR", "IND", "MYS"]
#                 elif is_saudi and is_turkey and is_india:
#                     countries = ["SAU", "TUR", "IND"]
#                 elif is_saudi and is_turkey:
#                     countries = ["SAU", "TUR"]
#                 elif is_saudi:
#                     countries = ["SAU"]
#                 elif is_turkey:
#                     countries = ["TUR"]
#                 elif is_india:
#                     countries = ["IND"]
#                 elif is_malaysia:
#                     countries = ["MYS"]
#                 elif is_egypt:
#                     countries = ["EGY"]
#                 elif is_global:
#                     countries = ["GLB"]
#                 elif is_georgia:
#                     countries = ["GEO"]
#                 else:
#                     countries = []
#                 print(countries)
#                 user_name = get_user_data
#                 if account_status:
#                     all_subscription = []
#                     get_subscription_record = Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_type == 'Demo')).all()
#
#                     for data in get_subscription_record:
#                         cs_name = data.name
#                         cs_email = data.email
#                         cs_company_name = data.company_string_name
#                         cs_contact = data.contact
#                         cs_pos_no = data.stores_number
#                         cs_reg_code = data.business_name
#                         cs_sub_type = data.subscription_type
#                         cs_sub_status = data.db_status
#                         cs_creation_date = data.db_create_date.strftime("%b %d %Y"),
#                         cs_city = data.city
#                         cs_street = data.street
#                         cs_country = data.Country
#                         cs_tax_file = data.tax_file
#                         cs_commercial_reg = data.commercial_register
#                         cs_expire_db = data.expire_db.strftime("%b %d %Y"),
#                         cs_order_id = data.order_id
#                         cs_postcode = data.postcode
#                         cs_plan_type = data.plan_type
#                         cs_subscription_status = data.subscription_status
#                         cs_country_code = data.country_code_id
#                         cs_activity = data.is_active
#                         all_subscription.append({"id":data.id,"cs_name":cs_name,
#                                                  "cs_email": cs_email,
#                                                  "cs_company_name": cs_company_name,
#                                                  "cs_contact": cs_contact,
#                                                  "cs_pos_no":cs_pos_no,
#                                                  "cs_reg_code": cs_reg_code,
#                                                  "cs_sub_type": cs_sub_type,
#                                                  "cs_sub_status": cs_sub_status,
#                                                  "cs_creation_date": cs_creation_date,
#                                                  "cs_city": cs_city,
#                                                  "cs_street": cs_street,
#                                                  "cs_country":cs_country,
#                                                  "cs_tax_file": cs_tax_file,
#                                                  "cs_commercial_reg": cs_commercial_reg,
#                                                  "cs_expire_db": cs_expire_db,
#                                                  "cs_order_id": cs_order_id,
#                                                  "cs_postcode": cs_postcode,
#                                                  "cs_plan_type": cs_plan_type,
#                                                  "cs_subscription_status": cs_subscription_status,
#                                                  "cs_country_code": cs_country_code,
#                                                  "cs_activity": cs_activity,
#                                                  })
#                     return {
#
#                         "data":all_subscription,
#
#                     }
#         except Exception as Error:
#             print(Error)
#     return {"samer": 5}
#


#generate token
def generateTokenCustom(name, email):
    '''generate token by jwt and bcrypt '''
    try:
        #        create custom random code
        random_code = random.randint(1,10000000000000000000000000000000000)
        #       hashing random code by bcrypt password hash
        random_code_hash = bcrypt.generate_password_hash(str(random_code)).decode("utf-8")
        #       create jwt token
        data = jwt.encode({
            'name':name ,
            'email':email,
            'code': random_code_hash
        },app.config['SECRET_KEY'],algorithm="HS256")
        return data
    except Exception as error:
        print(error)
        return {"status":"FAILED"}


def generateTokenCustomForSessions(name, email):
    '''generate token for session by jwt and bcrypt '''
    try:
        #        create custom random code
        random_code = random.randint(1,10000000000000000000000000000000000000)
        #       hashing random code by bcrypt password hash
        random_code_hash = bcrypt.generate_password_hash(str(random_code)).decode("utf-8")
        #       create jwt token
        data = jwt.encode({
            'name':name ,
            'email':email,
            'code': random_code_hash
        },app.config['SECRET_KEY'],algorithm="HS256")
        return data
    except Exception as error:
        print(error)
        return {"status":"FAILED"}

#---------------------------------------------------------------------------------------------------------------------------
@app.route('/checkAuthentication', methods=['POST'])
def checkAuthentication(access_token, session_token):
    try:
        get_access_token = access_token
        get_session_token = session_token
        check_user = Sessions.query.filter_by(access_token=get_access_token).first()
        if check_user:
            check_session = Sessions.query.filter_by(session_token=get_session_token).first()
            if check_session:
                return {"status":"success",
                        "user_id":check_session.subscription_id}
            else:
                return {"status":"invalid session"}
        else:
            return {"status": "invalid_user_authentication"}
    except Exception as error:
        print(error)
        return {"status":"Failed"}



@app.route('/checkAuthentication', methods=['POST'])
def checkAuthenticationForadmin(access_token, session_token):
    try:
        get_access_token = access_token
        get_session_token = session_token
        check_user = Sessions.query.filter_by(access_token=get_access_token).first()
        if check_user:
            check_session = Sessions.query.filter_by(session_token=get_session_token).first()
            if check_session:
                return {"status":"success",
                        "user_id":check_session.user_id}
            else:
                return {"status":"invalid session"}
        else:
            return {"status": "invalid_user_authentication"}
    except Exception as error:
        print(error)
        return {"status":"Failed"}


@app.route('/checkAuthenticationforJsonApi', methods=['POST'])
def checkAuthenticationforJsonApi():
    try:
        get_data = request.json
        get_access_token = get_data['access_token']
        get_session_token = get_data['access_session']
        check_user = Sessions.query.filter_by(access_token=get_access_token).first()
        if check_user:
            check_session = Sessions.query.filter_by(session_token=get_session_token).first()
            get_user_permission = Users.query.filter_by(id=check_session.user_id).first()
            if check_session and  get_user_permission:
                print(get_user_permission.permission)
                return {"status":"success", "permission": get_user_permission.permission}
            else:
                print("invalid session")
                return {"status":"invalid session"}
        else:
            print("invalid invalid_user_authentication")

            return {"status": "invalid_user_authentication"}
    except Exception as error:
        print(error)
        return {"status":"Failed"}


@app.route('/checkAuthenticationForSite', methods=['POST'])
def checkAuthenticationForSite():
    try:
        get_data = request.json
        get_access_token = get_data['access_token']
        get_session_token = get_data['access_session']
        check_user = Sessions.query.filter_by(access_token=get_access_token).first()
        if check_user:
            check_session = Sessions.query.filter_by(session_token=get_session_token).first()
            if check_session:
                return {"status":"success",
                        "user_id":check_session.subscription_id}
            else:
                return {"status":"invalid session"}
        else:
            return {"status": "invalid_user_authentication"}
    except Exception as error:
        print(error)
        return {"status":"Failed"}

    #----------------------------------------------------------------------------------------------------------------

# customers

def check_country_available_for_user(user_id):
    '''this function to return list country available for user or admin. for example ["SAU","TUR","MYS"]'''
    try:
        check_data = Users.query.filter_by(id = user_id).first()
        if check_data:
            is_saudi = check_data.is_saudi
            is_turkey = check_data.is_turkey
            is_india = check_data.is_india
            is_malaysia = check_data.is_malaysia
            is_global = check_data.is_global
            is_egypt = check_data.is_egypt
            is_georgia = check_data.is_georgia
            if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
                countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
            elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
                countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
            elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
                countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
            elif is_saudi and is_turkey and is_india and is_malaysia:
                countries = ["SAU", "TUR", "IND", "MYS"]
            elif is_saudi and is_turkey and is_india:
                countries = ["SAU", "TUR", "IND"]
            elif is_saudi and is_turkey:
                countries = ["SAU", "TUR"]
            elif is_saudi:
                countries = ["SAU"]
            elif is_turkey:
                countries = ["TUR"]
            elif is_india:
                countries = ["IND"]
            elif is_malaysia:
                countries = ["MYS"]
            elif is_egypt:
                countries = ["EGY"]
            elif is_global:
                countries = ["GLB"]
            elif is_georgia:
                countries = ["GEO"]
            else:
                countries = []
            return countries
    except Exception as Error:
        pass

def check_reg_code(country):
    if country == "Saudi Arabia":
        return {"country_code_3d": "SAU", "country_code_2d": "SA" }
    elif country == "India":
        return {"country_code_3d": "IND", "country_code_2d": "IN" }
    elif country == "Turkey":
        return {"country_code_3d": "TUR", "country_code_2d": "TR" }
    elif country == "Malaysia":
        return {"country_code_3d": "MYS", "country_code_2d": "MY" }
    elif country == "Egypt":
        return {"country_code_3d": "EGY", "country_code_2d": "EG" }
    elif country == "Georgia":
        return {"country_code_3d": "GEO", "country_code_2d": "GO" }
    else:
        return {"country_code_3d": "GLB", "country_code_2d": "GL" }


@app.route('/create_new_subscription_from_admin', methods=['POST', 'GET'])
def create_new_subscription_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", get_data)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                name = get_data['name']
                email = get_data['email']
                if Subscription.query.filter_by(email = email).first():
                    print("emil exists")
                    return {"status": "emailAlreadyExist"}
                else:
                    stores_number = get_data['stores_number']
                    reg_code = get_data['reg_code']
                    city = get_data['city']
                    contact = get_data['contact']
                    password = get_data['password']
                    file_taxes = get_data['file_taxes']
                    commercial_register = get_data['commercial_register']
                    country = get_data['country']
                    sub_type = get_data['sub_type']
                    street = get_data['street']
                    postcode = get_data['postcode']
                    company_string_name = get_data['company_string_name']
                    country_code = check_reg_code(country)
                    database_random_code = random.randint(1,1000000)
                    company_token = str(random.randint(1,100000000000000000000))
                    reg_code_full = str(country_code['country_code_3d']) + '_'+str(reg_code)+'_'+str(database_random_code)
                    password_hash = bcrypt.generate_password_hash(password)
                    plan_type = ""
                    price = ""
                    if get_data['sub_type'] == "Enterprise":
                        get_package_price = Packages.query.filter(and_(Packages.country_code == country_code['country_code_3d'], Packages.pos_no == stores_number, Packages.type == get_data['subscription'])).first()
                        plan_type = get_data['subscription']
                        price = get_package_price.price
                    else:
                        plan_type = ""
                    data = Subscription(name,email,
                                        stores_number,reg_code_full,'10',
                                        city,contact,datetime.now(),password,
                                        file_taxes,commercial_register,
                                        datetime.now()+timedelta(30),datetime.now(),
                                        country,sub_type,street,postcode,password_hash,
                                        company_string_name,"Admin_panel",company_token,"","","","")
                    db.session.add(data)
                    db.session.commit()
                    data.db_status = "Activated"
                    data.account_type = "live"
                    data.country_code_id = country_code['country_code_3d']
                    data.subscription_type = sub_type
                    data.plan_type = plan_type
                    data.price = price
                    data.subscription_created_from = "Admin_panel"
                    db.session.commit()
                    print("success33333333333333333333333")
                    return {"status":"Success"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status":"unauth"}


@app.route('/get_subscription_data_from_admin', methods=['POST', 'GET'])
def get_subscription_data_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", get_data)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success':
                get_subscription_data = Subscription.query.filter_by(id= get_data['subscription_id']).first()
                get_subscription_orders = Order.query.filter_by(subscription_id = get_data['subscription_id']).all()
                if get_subscription_data and get_subscription_data.country_code_id in check_country_available_for_user(get_admin_data.id):
                    all_orders = []
                    for rec in get_subscription_orders:
                        all_orders.append({"name": rec.name,
                                           "email": rec.email,
                                           "order_date": rec.order_date,
                                           "expire_date": rec.expire_db,
                                           "trans_ref":rec.tans_ref,
                                           "status": rec.auto_payment_status,
                                           "amount": rec.amount})
                    print(all_orders)
                    return {"status": "Success",
                            "name" : get_subscription_data.name,
                            "email" : get_subscription_data.email,
                            "subscription_type" : get_subscription_data.subscription_type,
                            "stores_number" : get_subscription_data.stores_number,
                            "reg_code" : get_subscription_data.business_name,
                            "best_time_call" :get_subscription_data.best_time_call,
                            "city" : get_subscription_data.city,
                            "contact" : get_subscription_data.contact,
                            "company_string_name" : get_subscription_data.company_string_name,
                            "commercial_register" : get_subscription_data.commercial_register,
                            "country" : get_subscription_data.Country,
                            "street" : get_subscription_data.street,
                            "postcode" : get_subscription_data.postcode,
                            "tax_file" : get_subscription_data.tax_file,
                            "password" : get_subscription_data.password,
                            "subscription" : get_subscription_data.plan_type,
                            "price":get_subscription_data.price,
                            "sub_date": get_subscription_data.db_create_date.strftime("%m/%d/%Y"),
                            "expire_date": str(get_subscription_data.expire_db.strftime("%Y-%m-%d")),
                            "Orders":all_orders
                            }
                else:
                    return {"status": "Invalid"}
            else:
                return {"status": "unAuth"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}

    else:
        return {"status": "Error"}



@app.route('/get_price_of_package_admin', methods=['POST'])
def get_price_of_package_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", get_data)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                get_country_code = check_reg_code(get_data['country'])
                get_package = Packages.query.filter(and_(Packages.country_code == get_country_code['country_code_3d'], Packages.pos_no == get_data['pos_no'], Packages.type == get_data['subscription'])).first()
                print("ok")
                return {"status": "Success" , "price": get_package.price, "currency": get_package.currency_en}
            else:
                return {"status":"Error"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "Error"}


@app.route('/update_subscription_data_from_admin', methods=['POST', 'GET'])
def update_subscription_data_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", get_data)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                get_subscription_object = Subscription.query.filter_by(id = get_data['subscription_id']).first()
                if get_subscription_object:
                    get_subscription_object.name = get_data['name']
                    get_subscription_object.email = get_data['email']
                    get_subscription_object.best_time_call = get_data['best_time_call']
                    get_subscription_object.city = get_data['city']
                    get_subscription_object.contact = get_data['contact']
                    get_subscription_object.company_string_name = get_data['company_string_name']
                    get_subscription_object.commercial_register = get_data['commercial_register']
                    get_subscription_object.street = get_data['street']
                    get_subscription_object.postcode = get_data['postcode']
                    get_subscription_object.tax_file = get_data['tax_file']
                    get_subscription_object.password = get_data['password']
                    get_subscription_object.password_hash = bcrypt.generate_password_hash(get_data['password'])
                    db.session.commit()
                    return {"status": "Success"}
                else:
                    return {"status": "Error", "message":"the subscription id not found in cashierme"}
            else:
                return {"status": "Invalid", "message":"you dont have permission to update subscription information. please contact with administrator "}
        except Exception as Error:
            return {"status": "Exception_error", "message": str(Error)}
    else:
        return {"status": "unAuth", "message": "unAuthorized"}






@app.route('/delete_customer_from_admin', methods=['POST', 'GET'])
def delete_customer_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                get_user_data = Subscription.query.filter_by(id = get_data['customer_id']).first()
                db.session.delete(get_user_data)
                db.session.commit()
                return {"status": "Success"}
            else:
                return {"status": "Error"}

        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "Error"}



def check_user_email_exist(email):
    try:
        get_data = Users.query.filter_by(email = email).first()
        if get_data:
            return {"status": "Exist"}
        else:
            return {"status": "dontExist"}

    except Exception as Error:
        print(Error)
        return {"status", str(Error)}

def generateTokenCustomForUsers(name, email):
    '''generate token by jwt and bcrypt '''
    try:
        #        create custom random code
        random_code = random.randint(1,10000000000000000000000000000000000)
        #       hashing random code by bcrypt password hash
        random_code_hash = bcrypt.generate_password_hash(str(random_code)).decode("utf-8")
        #       create jwt token
        data = jwt.encode({
            'name':name ,
            'email':email,
            'code': random_code_hash
        },app.config['SECRET_KEY'],algorithm="HS256")
        return data
    except Exception as error:
        print(error)
        return {"status":"FAILED"}



@app.route('/add_new_user_admin', methods=['POST', 'GET'])
def add_new_user_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        try:
            get_data = request.json
            get_name = get_data['name']
            name = get_name.replace(".", "_")
            email = get_data['email']
            password = get_data['password']
            gender = get_data['gender']
            job_grade = get_data['job_grade']
            mobile = get_data['mobile']
            country = get_data['country']
            address = get_data['address']
            permisions = get_data['permisions']
            saudi = get_data['saudi']
            turkish = get_data['turkish']
            india = get_data['india']
            malysia = get_data['malaysia']
            is_global = get_data['global']
            egypt = get_data['egypt']
            georgia = get_data['georgia']
            activity = get_data['activity']
            payment_cash = get_data['payment_cash']
            checkEmail = check_user_email_exist(email)

            if checkEmail['status'] == "Exist":
                print("email Exists")
                return {"status": "EmailExit"}
            elif checkEmail['status'] == "dontExist":
                try:
                    add_data = Users(name,email,bcrypt.generate_password_hash(password).decode('utf-8'),country,address,mobile,gender,job_grade,activity)
                    db.session.add(add_data)
                    db.session.commit()
                    add_data.is_georgia = georgia
                    add_data.is_egypt = egypt
                    add_data.is_global = is_global
                    add_data.is_malaysia = malysia
                    add_data.is_india = india
                    add_data.is_turkey = turkish
                    add_data.is_saudi = saudi
                    add_data.permission = permisions
                    add_data.payment_cash = payment_cash
                    db.session.commit()
                    session_token = generateTokenCustomForUsers(str(name), str(email))
                    access_token = generateTokenCustomForUsers(str(name), str(email))
                    add_session = Sessions(add_data.id, None, name,access_token,session_token,datetime.now(),'Admin')
                    db.session.add(add_session)
                    db.session.commit()
                    return {"status": "Success"}
                except Exception as Error:
                    print(Error)
            else:
                return {"status": "Error"}
        except Exception as Error:
            print(Error)
    else:
        return {"status": "Error"}
    return {"status": "Error"}



@app.route('/SubmitAdminLogin', methods=['POST', 'GET'])
def SubmitLoginAdmin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print ("auth")
        try:
            get_data = request.json
            get_email = get_data['email']
            get_password = get_data['password']
            print(get_data)
            check_data = Users.query.filter_by(email = str(get_email)).first()
            if check_data and bcrypt.check_password_hash(check_data.password, get_password):
                print("ok")
                get_tokens = Sessions.query.filter(and_(Sessions.user_id == check_data.id, Sessions.account_type == "Admin")).first()
                print("get_token",get_tokens)
                create_new_session = generateTokenCustomForUsers(check_data.user_name, check_data.email)
                get_tokens.session_token = create_new_session
                get_tokens.update_date = datetime.now()
                db.session.commit()
                access_token = get_tokens.access_token
                session_token = get_tokens.session_token
                return {"status":"success",
                        "access_token":access_token,
                        "session_token": session_token,
                        "activity": check_data.activate
                        }
            else:
                print({"status":"invalid"})
                return {"status":"invalid"}
        except Exception as Error:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>',Error)
            return {"status":"Faield"}
    else:
        print({"status":"Faield"}, "Error")
        return {"status": "Faield"}



def check_country_available_for_user(user_id):
    '''this function to return list country available for user or admin. for example ["SAU","TUR","MYS"]'''
    try:
        check_data = Users.query.filter_by(id = user_id).first()
        if check_data:
            is_saudi = check_data.is_saudi
            is_turkey = check_data.is_turkey
            is_india = check_data.is_india
            is_malaysia = check_data.is_malaysia
            is_global = check_data.is_global
            is_egypt = check_data.is_egypt
            is_georgia = check_data.is_georgia
            if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
                countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
            elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
                countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
            elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
                countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
            elif is_saudi and is_turkey and is_india and is_malaysia:
                countries = ["SAU", "TUR", "IND", "MYS"]
            elif is_saudi and is_turkey and is_india:
                countries = ["SAU", "TUR", "IND"]
            elif is_saudi and is_turkey:
                countries = ["SAU", "TUR"]
            elif is_saudi:
                countries = ["SAU"]
            elif is_turkey:
                countries = ["TUR"]
            elif is_india:
                countries = ["IND"]
            elif is_malaysia:
                countries = ["MYS"]
            elif is_egypt:
                countries = ["EGY"]
            elif is_global:
                countries = ["GLB"]
            elif is_georgia:
                countries = ["GEO"]
            else:
                countries = []
            return countries
    except Exception as Error:
        pass







@app.route('/get_all_countries', methods=['POST', 'GET'])
def get_all_countries():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' :
                is_saudi = get_admin_data.is_saudi
                is_turkey = get_admin_data.is_turkey
                is_india = get_admin_data.is_india
                is_malaysia = get_admin_data.is_malaysia
                is_global = get_admin_data.is_global
                is_egypt = get_admin_data.is_egypt
                is_georgia = get_admin_data.is_georgia
                if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
                    countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
                elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
                    countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
                elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
                    countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
                elif is_saudi and is_turkey and is_india and is_malaysia:
                    countries = ["SAU", "TUR", "IND", "MYS"]
                elif is_saudi and is_turkey and is_india:
                    countries = ["SAU", "TUR", "IND"]
                elif is_saudi and is_turkey:
                    countries = ["SAU", "TUR"]
                elif is_saudi:
                    countries = ["SAU"]
                elif is_turkey:
                    countries = ["TUR"]
                elif is_india:
                    countries = ["IND"]
                elif is_malaysia:
                    countries = ["MYS"]
                elif is_egypt:
                    countries = ["EGY"]
                elif is_global:
                    countries = ["GLB"]
                elif is_georgia:
                    countries = ["GEO"]
                else:
                    countries = []
                get_all_countries = Countries.query.filter(Countries.country_code.in_(countries)).all()
                all_countries = []
                for data in get_all_countries:
                    print(data.country_name)
                    all_countries.append({"id":data.id,"country_name": data.country_name,"code_3d": data.country_code,
                                          "code_2d": data.country_code, "currency":data.currency,
                                          "language": data.language,"default_language":data.default_language,
                                          "monthly_amount":data.monthly_amount,"annually_amount":data.annually_amount,"payment_getway":data.payment_getway})
                return {"status": "Success","data": all_countries}

        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "Error"}


def create_package_record_from_admin(pos_no,monthly_price,annually_price,en_string,ar_string,currency_en,currency_ar,country_code):
    packages_delete = Packages.query.filter_by(country_code = country_code).all()
    print("ok")
    for data in packages_delete:
        db.session.delete(data)
        db.session.commit()
    print("ok")
    month = 'Monthly'
    year = 'yearly'
    monthly_price = monthly_price
    annually_price = annually_price
    en_string = en_string
    ar_string = ar_string
    currency_en = currency_en
    currency_ar = currency_ar
    country_code = country_code
    for data in range(pos_no):
        get_code = data
        get_price_month = int(monthly_price) * int(data)
        get_price_year = int((int(annually_price) * int(data))*12)
        add_packages_month = Packages(get_price_month,str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,month,currency_en,currency_ar,str(get_code),get_code, country_code)
        add_packages_year = Packages(get_price_year,str(get_code),str(get_code)+" "+en_string,str(get_code)+" "+ar_string,year,currency_en,currency_ar,str(get_code),get_code ,country_code)
        db.session.add(add_packages_month)
        db.session.commit()
        db.session.add(add_packages_year)
        db.session.commit()
    return {"status": "Success"}


@app.route('/add_new_country_from_admin', methods=['POST'])
def add_new_country_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin ()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            print (check_auth)
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                print("developer auth>>>>>>>>>>>>>>>>")
                country_name = get_data['country_name']
                currency = get_data['currency']
                monthly_amount = get_data['monthly_amount']
                annually_amount = get_data['annually_amount']
                country_3d_code = get_data['country_3d_code']
                country_2d_code = get_data['country_2d_code']
                default_language = get_data['default_language']
                payment_getway = get_data['payment_getway']
                all_language = get_data['all_language']
                payment_merchant_id = get_data['payment_merchant_id']
                payment_currency = get_data['payment_currency']
                payment_api_url = get_data['payment_api_url']
                payment_api_key = get_data['payment_api_key']
                payment_query_url = get_data['payment_query_url']
                usd_convert = get_data['usd_convert']
                data = Countries(country_3d_code,country_2d_code,
                                 country_name,all_language,
                                 default_language,currency,
                                 monthly_amount,annually_amount,payment_getway,
                                 payment_merchant_id,payment_currency,payment_api_url,
                                 payment_api_key,payment_query_url)
                db.session.add(data)
                db.session.commit()
                create_package_record_from_admin(100,monthly_amount,annually_amount,"POS","",currency,currency,country_2d_code)
                print("Success add country record")
                return {"status": "Success"}
            else:
                return {"status": "notHavePermission"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "unAuth"}


@app.route('/delete_country_from_admin', methods=['POST', 'GET'])
def delete_country_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                get_country_data = Countries.query.filter_by(id = get_data['country_id']).first()
                delete_packages = Packages.query.filter_by(country_code = get_country_data.country_code_2d).all()
                for data in delete_packages:
                    db.session.delete(data)
                    db.session.commit()
                db.session.delete(get_country_data)
                db.session.commit()

                return {"status": "Success"}
            else:
                return {"status": "Error", "message": "You don,t have permission to do that please contact with administrator"}

        except Exception as Error:
            print(Error)
            return {"status": "Error", "message": str(Error)}
    else:
        return {"status": "Error", "message": "cannot process your request now please contact with administrator"}


@app.route('/get_country_data_from_admin', methods=['POST', 'GET'])
def get_country_data_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success':
                get_country_available = check_country_available_for_user(get_admin_data.id)
                get_countries = Countries.query.filter_by(id = get_data['country_code']).first()
                if get_countries.country_code in get_country_available:
                    country_name  = get_countries.country_name
                    currency  = get_countries.currency
                    monthly_amount  = get_countries.monthly_amount
                    annually_amount  = get_countries.annually_amount
                    country_3d_code  = get_countries.country_code
                    country_2d_code  = get_countries.country_code_2d
                    default_language  = get_countries.default_language
                    payment_getway  = get_countries.payment_getway
                    all_language  = get_countries.language
                    payment_merchant_id  = get_countries.payment_merchant_id
                    payment_currency  = get_countries.payment_currency
                    payment_api_url  = get_countries.payment_request_api_url
                    payment_api_key  = get_countries.payment_api_key
                    payment_query_url  = get_countries.payment_query_link
                    usd_convert  = get_countries.usd_convert
                    print("Success", get_countries.country_name,
                          )
                    return {"status": "Success",
                            "country_name": country_name,
                            "currency": currency,
                            "monthly_amount": monthly_amount,
                            "annually_amount": annually_amount,
                            "country_3d_code": country_3d_code,
                            "country_2d_code": country_2d_code,
                            "default_language": default_language,
                            "payment_getway": payment_getway,
                            "all_language": all_language,
                            "payment_merchant_id": payment_merchant_id,
                            "payment_currency": payment_currency,
                            "payment_api_url": payment_api_url,
                            "payment_api_key": payment_api_key,
                            "payment_query_url": payment_query_url,
                            "usd_convert": usd_convert,}
                else:
                    return {"status": "unAuthCountry"}
            else:
                return {"status": "unAuth"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "Error"}


@app.route('/update_country_data_from_admin', methods=['POST', 'GET'])
def update_country_data_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            get_country_data = Countries.query.filter_by(id = get_data['country_code']).first()
            if check_auth['status'] == 'success' and get_admin_data.permission == "manager":
                get_country_data.monthly_amount = get_data['monthly_amount']
                get_country_data.annually_amount = get_data['annually_amount']
                db.session.commit()
                create_package_record_from_admin(100,get_data['monthly_amount'],get_data['annually_amount'],"POS","",get_data['payment_currency'],get_data['payment_currency'],get_data['country_2d_code'])
                return {"status": "Success"}
            elif check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                get_country_data.country_name = get_data['country_name']
                get_country_data.currency = get_data['currency']
                get_country_data.monthly_amount = get_data['monthly_amount']
                get_country_data.annually_amount = get_data['annually_amount']
                get_country_data.country_code = get_data['country_3d_code']
                get_country_data.country_code_2d = get_data['country_2d_code']
                get_country_data.default_language = get_data['default_language']
                get_country_data.payment_getway = get_data['payment_getway']
                get_country_data.language = get_data['all_language']
                get_country_data.payment_merchant_id = get_data['payment_merchant_id']
                get_country_data.payment_currency = get_data['payment_currency']
                get_country_data.payment_request_api_url = get_data['payment_api_url']
                get_country_data.payment_api_key = get_data['payment_api_key']
                get_country_data.payment_query_link = get_data['payment_query_url']
                get_country_data.usd_convert = get_data['usd_convert']
                db.session.commit()
                create_package_record_from_admin(100,get_data['monthly_amount'],get_data['annually_amount'],"POS","",get_data['payment_currency'],get_data['payment_currency'],get_data['country_2d_code'])

                return {"status": "Success"}
            else:
                return {"status": "Error", "message": "You don,t have permission to do that please contact with administrator"}

        except Exception as Error:
            print(Error)
            return {"status": "Error", "message": str(Error)}
    else:
        return {"status": "Error", "message": "cannot process your request now please contact with administrator"}





@app.route('/getAllSubscription_old', methods=['POST'])
def getAllSubscription_old():
    check_auth_value = verify_auth_api.check_header_auth_admin ()
    if check_auth_value == "Auth":
        print ("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
            print (check_auth)
            if check_auth['status'] == 'success':
                countries = None
                permission = get_user_data.permission
                account_status = get_user_data.activate
                is_saudi = get_user_data.is_saudi
                is_turkey = get_user_data.is_turkey
                is_india = get_user_data.is_india
                is_malaysia = get_user_data.is_malaysia
                is_global = get_user_data.is_global
                is_egypt = get_user_data.is_egypt
                is_georgia = get_user_data.is_georgia

                if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
                    countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
                elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
                    countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
                elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
                    countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
                elif is_saudi and is_turkey and is_india and is_malaysia:
                    countries = ["SAU", "TUR", "IND", "MYS"]
                elif is_saudi and is_turkey and is_india:
                    countries = ["SAU", "TUR", "IND"]
                elif is_saudi and is_turkey:
                    countries = ["SAU", "TUR"]
                elif is_saudi:
                    countries = ["SAU"]
                elif is_turkey:
                    countries = ["TUR"]
                elif is_india:
                    countries = ["IND"]
                elif is_malaysia:
                    countries = ["MYS"]
                elif is_egypt:
                    countries = ["EGY"]
                elif is_global:
                    countries = ["GLB"]
                elif is_georgia:
                    countries = ["GEO"]
                else:
                    countries = []
                print(countries)
                user_name = get_user_data
                if account_status:
                    all_subscription = []
                    get_subscription_record = Subscription.query.filter(Subscription.country_code_id.in_(countries)).all()
                    get_len_demo = len(Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_type == "Demo")).all())
                    get_len_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_type == "Enterprise")).all())
                    get_len_cancel = len(Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_status == "Cancel")).all())
                    get_len_all = len(get_subscription_record)
                    len_saudi_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "SAU", Subscription.subscription_type =="Demo" )).all())
                    len_saudi_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "SAU", Subscription.subscription_type =="Enterprise" )).all())
                    len_egypt_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "EGY", Subscription.subscription_type =="Demo" )).all())
                    len_egypt_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "EGY", Subscription.subscription_type =="Enterprise" )).all())
                    len_global_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "GLB", Subscription.subscription_type =="Demo" )).all())
                    len_global_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "GLB", Subscription.subscription_type =="Enterprise" )).all())
                    len_turkey_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "TUR", Subscription.subscription_type =="Demo" )).all())
                    len_turkey_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "TUR", Subscription.subscription_type =="Enterprise" )).all())
                    len_india_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "IND", Subscription.subscription_type =="Demo" )).all())
                    len_india_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "IND", Subscription.subscription_type =="Enterprise" )).all())
                    len_malaysia_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "MYS", Subscription.subscription_type =="Demo" )).all())
                    len_malaysia_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "MYS", Subscription.subscription_type =="Enterprise" )).all())
                    len_georgia_demo = len(Subscription.query.filter(and_(Subscription.country_code_id == "GEO", Subscription.subscription_type =="Demo" )).all())
                    len_georgia_enterprise = len(Subscription.query.filter(and_(Subscription.country_code_id == "GEO", Subscription.subscription_type =="Enterprise" )).all())
                    for data in get_subscription_record:
                        cs_name = data.name
                        cs_email = data.email
                        cs_company_name = data.company_string_name
                        cs_contact = data.contact
                        cs_pos_no = data.stores_number
                        cs_reg_code = data.business_name
                        cs_sub_type = data.subscription_type
                        cs_sub_status = data.db_status
                        cs_creation_date = data.db_create_date.strftime("%b %d %Y"),
                        cs_city = data.city
                        cs_street = data.street
                        cs_country = data.Country
                        cs_tax_file = data.tax_file
                        cs_commercial_reg = data.commercial_register
                        cs_expire_db = data.expire_db.strftime("%b %d %Y"),
                        cs_order_id = data.order_id
                        cs_postcode = data.postcode
                        cs_plan_type = data.plan_type
                        cs_subscription_status = data.subscription_status
                        cs_country_code = data.country_code_id
                        cs_activity = data.is_active
                        all_subscription.append({"id":data.id,"cs_name":cs_name,
                                                 "cs_email": cs_email,
                                                 "cs_company_name": cs_company_name,
                                                 "cs_contact": cs_contact,
                                                 "cs_pos_no":cs_pos_no,
                                                 "cs_reg_code": cs_reg_code,
                                                 "cs_sub_type": cs_sub_type,
                                                 "cs_sub_status": cs_sub_status,
                                                 "cs_creation_date": cs_creation_date,
                                                 "cs_city": cs_city,
                                                 "cs_street": cs_street,
                                                 "cs_country":cs_country,
                                                 "cs_tax_file": cs_tax_file,
                                                 "cs_commercial_reg": cs_commercial_reg,
                                                 "cs_expire_db": cs_expire_db,
                                                 "cs_order_id": cs_order_id,
                                                 "cs_postcode": cs_postcode,
                                                 "cs_plan_type": cs_plan_type,
                                                 "cs_subscription_status": cs_subscription_status,
                                                 "cs_country_code": cs_country_code,
                                                 "cs_activity": cs_activity,
                                                 })
                    return {"all_sub":get_len_all,
                            "demo_sub":get_len_demo,
                            "enterprise_sub":get_len_enterprise,
                            "cancel_sub": get_len_cancel,
                            "data":all_subscription,
                            "user_name": get_user_data.user_name,
                            "saudi_demo_len": len_saudi_demo,
                            "saudi_enterprise_len": len_saudi_enterprise,
                            "egypt_demo_len":len_egypt_demo,
                            "egypt_enterprise_len":len_egypt_enterprise,
                            "global_demo_len": len_global_demo,
                            "global_enterprise_len": len_global_enterprise,
                            "turkey_demo_len": len_turkey_demo,
                            "turkey_enterprise_len": len_turkey_enterprise,
                            "india_demo_len":len_india_demo,
                            "india_enterprise_len":len_india_enterprise,
                            "malaysia_demo_len": len_malaysia_demo,
                            "malaysia_enterprise_len": len_malaysia_enterprise,
                            "georgia_demo_len": len_georgia_demo,
                            "georgia_enterprise_len": len_georgia_enterprise,
                            }
        except Exception as Error:
            print(Error)
    return {"samer": 5}


@app.route('/delete_user_from_admin', methods=['POST', 'GET'])
def delete_user_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                get_user_data = Users.query.filter_by(id = get_data['user_id']).first()
                db.session.delete(get_user_data)
                db.session.commit()
                return {"status": "Success"}
            else:
                return {"status": "Error"}

        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "Error"}


@app.route('/forgot_password_check_email_exist', methods=['POST'])
def forgot_password_check():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print ("auth")
        try:
            get_data = request.json
            email = get_data['email']
            data = Users.query.filter_by(email = email).first()
            if data:
                data.forgot_password_code = random.randint(1, 1000000)
                auth_code = random.randint(1, 10000000000000000000000000000000000000000000000000)
                data.auth_code = auth_code
                data.update_date = datetime.now()+timedelta(minutes=10)
                db.session.commit()
                print("ok send auth code")
                return {"status": "Success", "authCode": str(auth_code)}
                # msg = Message("Change Account Password", recipients=[email])
                # msg.body = "your Code is " + ":"+ data.check_code
                # mail.send(msg)
                # return render_template('change_password.html', get_id = data.id),cleanup(db.session)
            else:
                return {"status": "Failed", "message": "Email not Exist"}
        except Exception as Error:
            print(Error)
            return {"status": "Error", "message": "Cannot process your request now. please try again letter"}
    else:
        return {"status": "hack"}


@app.route('/checkAndChangePassword', methods=['POST'])
def change_password_email():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print ("auth")
        try:
            get_data = request.json
            code= get_data['code']
            new_password = get_data['new_password']
            auth_code = get_data['authCode']
            data = Users.query.filter_by(auth_code = auth_code).first()
            if data:
                get_code = data.forgot_password_code
                if get_code == code:
                    if data.update_date >= datetime.now():
                        data.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
                        db.session.commit()
                        return {"status": "Success"}
                    else:
                        return {"status": "ExpireCode", "message": "Expired Code"}
                else:
                    return {"status": "Invalid","message": "Invalid Code"}
        except Exception as Error:
            print(Error)
            return {"status": "Error", "message": "Cannot process your request now. please try again letter"}
    else:
        return {"status": "hack"}


@app.route('/getAllUsers', methods=['POST', 'GET'])
def getAllUsers():
    check_auth_value = verify_auth_api.check_header_auth_admin ()
    if check_auth_value == "Auth":
        print ("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
            print (check_auth)
            if check_auth['status'] == 'success':
                get_all_data = Users.query.all()
                all_data = []
                for rec in get_all_data:
                    all_data.append({"id": rec.id ,"name": rec.user_name, "address": rec.address,
                                     "mobile":rec.mobile,"email": rec.email,"last_login":rec.last_login,
                                     "activity": rec.activate,"permission": rec.permission,
                                     "is_saudi": rec.is_saudi,"is_turkey": rec.is_turkey,
                                     "is_india": rec.is_india,"is_malaysia": rec.is_malaysia,
                                     "is_global": rec.is_global,"is_egypt": rec.is_egypt,"is_georgia": rec.is_georgia,})
                return {"data": all_data}
        except Exception as Error:
            print(Error)
            pass


@app.route('/get_prices_from_admin', methods=['POST', 'GET'])
def get_prices_from_admin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", get_data)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                get_available_country_code = check_country_available_for_user(get_admin_data.id)
                get_prices = Packages.query.filter(Packages.country_code.in_(get_available_country_code)).all()
                if get_prices :
                    all_prices = []
                    for rec in get_prices:
                        all_prices.append({"id":rec.id,
                                           "country_code": rec.country_code,
                                           "price": rec.price,
                                           "pos_no": rec.pos_no,
                                           "currency": rec.currency_en,
                                           "sub_type":rec.type,
                                           "package_code": rec.pos_no_code
                                           })
                    return {"status": "Success", "data": all_prices}

                else:
                    return {"status": "Invalid"}
            else:
                return {"status": "unAuth"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}

    else:
        return {"status": "Error"}

@app.route('/get_profile_data', methods=['POST'])
def get_profile_data():
    check_auth_value = verify_auth_api.check_header_auth_admin ()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
            print (check_auth)
            if check_auth['status'] == 'success':
                permission = get_user_data.permission
                account_status = get_user_data.activate
                name = get_user_data.user_name
                email = get_user_data.email
                gender = get_user_data.gender
                mobile = get_user_data.mobile
                job_grade = get_user_data.job_grade
                country = get_user_data.country
                address = get_user_data.address
                return {"status": "Success",
                        "name": name,
                        "email": email,
                        "gender": gender,
                        "mobile": mobile,
                        "country": country,
                        "address": address,
                        "permission": permission,
                        "activity": account_status,
                        "job_grade":job_grade,
                        "is_saudi": get_user_data.is_saudi,
                        "is_turkey": get_user_data.is_turkey,
                        "is_india": get_user_data.is_india,
                        "is_malaysia": get_user_data.is_malaysia,
                        "is_global": get_user_data.is_global,
                        "is_egypt": get_user_data.is_egypt,
                        "is_georgia": get_user_data.is_georgia,
                        "payment_cash": get_user_data.payment_cash}

            else:
                return {"status": "Error"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "Error"}


@app.route('/get_uer_profile_data', methods=['POST'])
def get_uer_profile_data():
    check_auth_value = verify_auth_api.check_header_auth_admin ()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            print (check_auth)
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                get_user_data = Users.query.filter_by(id = get_data['user_id']).first()
                permission = get_user_data.permission
                account_status = get_user_data.activate
                name = get_user_data.user_name
                email = get_user_data.email
                gender = get_user_data.gender
                mobile = get_user_data.mobile
                job_grade = get_user_data.job_grade
                country = get_user_data.country
                address = get_user_data.address
                is_saudi = get_user_data.is_saudi
                is_turkey = get_user_data.is_turkey
                is_india = get_user_data.is_india
                is_malaysia = get_user_data.is_malaysia
                is_global = get_user_data.is_global
                is_egypt = get_user_data.is_egypt
                is_georgia = get_user_data.is_georgia
                payment_cash = get_user_data.payment_cash
                return {"status": "Success","name": name,
                        "email": email, "gender": gender,
                        "mobile": mobile, "country": country,
                        "address": address,"permission": permission,
                        "activity": account_status,"job_grade":job_grade,
                        "is_saudi": is_saudi,"is_turkey": is_turkey,
                        "is_india": is_india,"is_malaysia": is_malaysia,
                        "is_global": is_global,"is_egypt": is_egypt,"is_georgia": is_georgia,"payment_cash": payment_cash
                        }
            else:
                return {"status": "Error"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "Error"}




@app.route('/updateProfileFromUser', methods=['POST', 'GET'])
def updateProfileFromUser():
    check_auth_value = verify_auth_api.check_header_auth_admin ()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            print(check_auth['user_id'])
            get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
            print (check_auth)
            if check_auth['status'] == 'success':
                get_user_data.user_name = get_data['name']
                get_user_data.mobile = get_data['mobile']
                get_user_data.address = get_data['address']
                db.session.commit()
                return {"status": "Success"}
            else:
                return {"status": "Error"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "Error"}


@app.route('/updateProfileFromAdmin', methods=['POST', 'GET'])
def updateProfileFromAdmin():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' and get_admin_data.permission == "developer":
                get_user_data = Users.query.filter_by(id = get_data['user_id']).first()
                get_user_data.user_name = get_data['name']
                get_user_data.email = get_data['email']
                get_user_data.gender = get_data['gender']
                get_user_data.mobile = get_data['mobile']
                get_user_data.job_grade = get_data['job_grade']
                get_user_data.country = get_data['country']
                get_user_data.address = get_data['address']
                get_user_data.permission = get_data['permissions']
                get_user_data.is_saudi = get_data['saudi']
                get_user_data.is_turkey = get_data['turkish']
                get_user_data.is_india = get_data['india']
                get_user_data.is_malaysia = get_data['malaysia']
                get_user_data.is_global = get_data['global']
                get_user_data.is_egypt = get_data['egypt']
                get_user_data.is_georgia = get_data['georgia']
                get_user_data.activate = get_data['activity']
                get_user_data.payment_cash = get_data['payment_cash']
                db.session.commit()
                return {"status": "Success"}
            else:
                return {"status": "Error"}

        except Exception as Error:
            print(Error)
            return {"status": "Error"}
    else:
        return {"status": "Error"}







@app.route('/updatePasswordFromUserAdmin', methods=['POST', 'GET'])
def updatePasswordFromUserAdmin():
    check_auth_value = verify_auth_api.check_header_auth_admin ()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            old_password = get_data['old_password']
            new_password = get_data['new_password']
            retry_password = get_data['retry_password']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            print(check_auth['user_id'])
            get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
            print (check_auth)
            if check_auth['status'] == 'success':
                if bcrypt.check_password_hash(get_user_data.password, old_password):
                    if new_password == retry_password:
                        get_user_data.password = bcrypt.generate_password_hash(new_password)
                        db.session.commit()
                        print("updated password successfully>>>>>>>>>>>>>")
                        return {"status": "Success"}
                    else:
                        return {"status": "Password not matched"}
                else:
                    return {"status": "Invalid old password"}

            else:
                return {"status": "unauthorized"}
        except Exception as Error:
            print(Error)
            return {"status": str(Error)}
    else:
        return {"status": "unauthorized"}



@app.route('/updatePasswordFromAdmin', methods=['POST', 'GET'])
def updatePasswordFromAdmin():
    check_auth_value = verify_auth_api.check_header_auth_admin ()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            new_password = get_data['new_password']
            retry_password = get_data['retry_password']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            print(check_auth['user_id'])
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            print (check_auth)
            if check_auth['status'] == 'success' and  get_admin_data.permission == "developer":
                if new_password == retry_password:
                    get_user_data = Users.query.filter_by(id = get_data['user_id']).first()
                    get_user_data.password = bcrypt.generate_password_hash(new_password)
                    db.session.commit()
                    print("updated password successfully>>>>>>>>>>>>>")
                    return {"status": "Success"}
                else:
                    return {"status": "Password not matched"}
            else:
                return {"status": "unauthorized"}
        except Exception as Error:
            print(Error)
            return {"status": str(Error)}
    else:
        return {"status": "unauthorized"}



@app.route('/upgrade_demo_to_enterprise_with_admin_payment_cash', methods=['POST', 'GET'])
def upgrade_demo_to_enterprise_with_admin_payment_cash():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success' and get_admin_data.payment_cash == True:
                customer_id = get_data['customer_id']
                pos_count = get_data['pos_count']
                receipt_voucher = get_data['receipt_voucher']
                subscription_type = get_data['subscription_type']
                get_customer_data = Subscription.query.filter_by(id=customer_id).first()
                expire_day_count = 0
                if subscription_type == 'Monthly':
                    expire_day_count = 31
                elif subscription_type == 'yearly':
                    expire_day_count = 366
                expire_db = datetime.now()+ timedelta(expire_day_count)
                date_order = datetime.now()
                random_code1 = random.randint(1, 100000)
                random_code2 = random.randint(1, 100000)
                transaction_ref = 'CASH'+str(random.randint(1, 10000000000))
                order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
                if get_customer_data:
                    #update data in subscription table
                    get_package_price = Packages.query.filter(and_(Packages.country_code == get_customer_data.country_code_id, Packages.pos_no == pos_count, Packages.type == subscription_type)).first()
                    get_customer_data.stores_number = pos_count
                    get_customer_data.subscription_type = "Enterprise"
                    get_customer_data.payment_status = "Done"
                    get_customer_data.plan_type = subscription_type
                    get_customer_data.price = get_package_price.price
                    get_customer_data.user_id = get_admin_data.id
                    get_customer_data.user_name = get_admin_data.user_name
                    get_customer_data.expire_db = expire_db
                    db.session.commit()
                    #create new record in order table
                    gnerate_order_record = Order(get_customer_data.name,
                                                 get_customer_data.email,get_customer_data.stores_number,
                                                 get_customer_data.business_name,get_customer_data.city,
                                                 get_customer_data.contact,get_customer_data.password,
                                                 get_customer_data.tax_file,get_customer_data.commercial_register,
                                                 datetime.today(),get_customer_data.street,get_customer_data.Country,
                                                 get_customer_data.postcode,"Done",order_code,get_package_price.price,
                                                 get_customer_data.plan_type,expire_db,get_customer_data.password_hash,get_package_price.id,get_customer_data.company_string_name)
                    db.session.add(gnerate_order_record)
                    db.session.commit()
                    gnerate_order_record.account_type = "Live"
                    gnerate_order_record.country_code_id = get_customer_data.country_code_id
                    gnerate_order_record.auto_payment_status = "Done"
                    gnerate_order_record.tans_ref = transaction_ref
                    get_customer_data.order_id = gnerate_order_record.id
                    gnerate_order_record.subscription_id = get_customer_data.id
                    gnerate_order_record.order_id = gnerate_order_record.id
                    gnerate_order_record.customer_token = receipt_voucher

                    saller_name = 'Ultimate Solutions'
                    seller_len = len(saller_name)
                    vat_number = '311136332100003'
                    dateandtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                    amount = str(gnerate_order_record.amount)
                    amounts = gnerate_order_record.amount
                    get_len = len(amount)
                    tax = round(int(amounts)-(int(amounts) / 1.15), 2)
                    # tax = (15 * int(amounts)) / 100
                    get_tax_len = len(str(tax))
                    company2hex = hexaConvertFunction.string2hex(saller_name)
                    fullCompany2hex = '01' + str(hexaConvertFunction.int2hex(seller_len)) + company2hex
                    vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
                    fullnumber2hex = '020F' + vatnumber2hex
                    datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
                    fulldatetimehex = '0314'+ datetimeInvoicehex
                    amount2hexa = hexaConvertFunction.string2hex(amount)
                    fulamount2hexa = '040'+ str(get_len) + amount2hexa
                    tax2hexa = hexaConvertFunction.string2hex(str(tax))
                    fulltax2hexa = '050' + str(get_tax_len) + tax2hexa
                    get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('hexa code :>>>>>>>>>>>>>>>',fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
                    print('base64 code >>>>>>>>>>>>>>',get_qr_base64)
                    gnerate_order_record.qr_code_base64 = get_qr_base64
                    db.session.commit()
                    print("success payment")
                    return {"status": "Success", "order_id": gnerate_order_record.id}
                pass
        except Exception as error:
            print(error)
            return {"status": "Error", "message": str(error)}
    else:
        return {"status": "unAuth"}


@app.route('/getAllSubscriptionDemoToCshPayment', methods=['POST'])
def getAllSubscriptionDemoToCshPayment():
    check_auth_value = verify_auth_api.check_header_auth_admin ()
    if check_auth_value == "Auth":
        print ("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", session_token)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
            print (check_auth)
            if check_auth['status'] == 'success':
                countries = None
                permission = get_user_data.permission
                account_status = get_user_data.activate
                is_saudi = get_user_data.is_saudi
                is_turkey = get_user_data.is_turkey
                is_india = get_user_data.is_india
                is_malaysia = get_user_data.is_malaysia
                is_global = get_user_data.is_global
                is_egypt = get_user_data.is_egypt
                is_georgia = get_user_data.is_georgia

                if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
                    countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
                elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
                    countries = ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
                elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
                    countries = ["SAU", "TUR", "IND", "MYS", "GLB"]
                elif is_saudi and is_turkey and is_india and is_malaysia:
                    countries = ["SAU", "TUR", "IND", "MYS"]
                elif is_saudi and is_turkey and is_india:
                    countries = ["SAU", "TUR", "IND"]
                elif is_saudi and is_turkey:
                    countries = ["SAU", "TUR"]
                elif is_saudi:
                    countries = ["SAU"]
                elif is_turkey:
                    countries = ["TUR"]
                elif is_india:
                    countries = ["IND"]
                elif is_malaysia:
                    countries = ["MYS"]
                elif is_egypt:
                    countries = ["EGY"]
                elif is_global:
                    countries = ["GLB"]
                elif is_georgia:
                    countries = ["GEO"]
                else:
                    countries = []
                print(countries)
                user_name = get_user_data
                if account_status:
                    all_subscription = []
                    get_subscription_record = Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_type == 'Demo')).all()

                    for data in get_subscription_record:
                        cs_name = data.name
                        cs_email = data.email
                        cs_company_name = data.company_string_name
                        cs_contact = data.contact
                        cs_pos_no = data.stores_number
                        cs_reg_code = data.business_name
                        cs_sub_type = data.subscription_type
                        cs_sub_status = data.db_status
                        cs_creation_date = data.db_create_date.strftime("%b %d %Y"),
                        cs_city = data.city
                        cs_street = data.street
                        cs_country = data.Country
                        cs_tax_file = data.tax_file
                        cs_commercial_reg = data.commercial_register
                        cs_expire_db = data.expire_db.strftime("%b %d %Y"),
                        cs_order_id = data.order_id
                        cs_postcode = data.postcode
                        cs_plan_type = data.plan_type
                        cs_subscription_status = data.subscription_status
                        cs_country_code = data.country_code_id
                        cs_activity = data.is_active
                        all_subscription.append({"id":data.id,"cs_name":cs_name,
                                                 "cs_email": cs_email,
                                                 "cs_company_name": cs_company_name,
                                                 "cs_contact": cs_contact,
                                                 "cs_pos_no":cs_pos_no,
                                                 "cs_reg_code": cs_reg_code,
                                                 "cs_sub_type": cs_sub_type,
                                                 "cs_sub_status": cs_sub_status,
                                                 "cs_creation_date": cs_creation_date,
                                                 "cs_city": cs_city,
                                                 "cs_street": cs_street,
                                                 "cs_country":cs_country,
                                                 "cs_tax_file": cs_tax_file,
                                                 "cs_commercial_reg": cs_commercial_reg,
                                                 "cs_expire_db": cs_expire_db,
                                                 "cs_order_id": cs_order_id,
                                                 "cs_postcode": cs_postcode,
                                                 "cs_plan_type": cs_plan_type,
                                                 "cs_subscription_status": cs_subscription_status,
                                                 "cs_country_code": cs_country_code,
                                                 "cs_activity": cs_activity,
                                                 })
                    return {

                        "data":all_subscription,

                    }
        except Exception as Error:
            print(Error)
    return {"samer": 5}




@app.route('/get_subscription_data_from_admin_and_reg_code', methods=['POST', 'GET'])
def get_subscription_data_from_admin_and_reg_code():
    check_auth_value = verify_auth_api.check_header_auth_admin()
    if check_auth_value == "Auth":
        print("auth")
        try:
            get_data = request.json
            access_token = get_data['access_token']
            session_token = get_data['access_session']
            print (">>>>>", get_data)
            check_auth = checkAuthenticationForadmin(access_token, session_token)
            get_admin_data = Users.query.filter_by(id = check_auth['user_id']).first()
            if check_auth['status'] == 'success':
                get_subscription_data = Subscription.query.filter_by(business_name= get_data['reg_code']).first()
                get_subscription_orders = Order.query.filter_by(subscription_id = get_subscription_data.id).all()
                if get_subscription_data and get_subscription_data.country_code_id in check_country_available_for_user(get_admin_data.id):
                    all_orders = []
                    for rec in get_subscription_orders:
                        all_orders.append({"name": rec.name,
                                           "email": rec.email,
                                           "order_date": rec.order_date,
                                           "expire_date": rec.expire_db,
                                           "trans_ref":rec.tans_ref,
                                           "status": rec.auto_payment_status,
                                           "amount": rec.amount})
                    print(all_orders)
                    return {"status": "Success",
                            "id": get_subscription_data.id,
                            "name" : get_subscription_data.name,
                            "email" : get_subscription_data.email,
                            "subscription_type" : get_subscription_data.subscription_type,
                            "stores_number" : get_subscription_data.stores_number,
                            "reg_code" : get_subscription_data.business_name,
                            "best_time_call" :get_subscription_data.best_time_call,
                            "city" : get_subscription_data.city,
                            "contact" : get_subscription_data.contact,
                            "company_string_name" : get_subscription_data.company_string_name,
                            "commercial_register" : get_subscription_data.commercial_register,
                            "country" : get_subscription_data.Country,
                            "street" : get_subscription_data.street,
                            "postcode" : get_subscription_data.postcode,
                            "tax_file" : get_subscription_data.tax_file,
                            "password" : get_subscription_data.password,
                            "subscription" : get_subscription_data.plan_type,
                            "price":get_subscription_data.price,
                            "sub_date": get_subscription_data.db_create_date.strftime("%m/%d/%Y"),
                            "expire_date": str(get_subscription_data.expire_db.strftime("%Y-%m-%d")),
                            "Orders":all_orders
                            }
                else:
                    return {"status": "Invalid"}
            else:
                return {"status": "unAuth"}
        except Exception as Error:
            print(Error)
            return {"status": "Error"}

    else:
        return {"status": "Error"}



if __name__ == '__main__':
    app.run()






































