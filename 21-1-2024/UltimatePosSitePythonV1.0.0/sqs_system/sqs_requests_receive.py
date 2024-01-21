from sqs_system import sqsRoute
from app import *
import json
import boto3
import requset_api
import ast
import SECURE_KEYS

sqs_send = boto3.client('sqs', aws_access_key_id=SECURE_KEYS.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=SECURE_KEYS.AWS_SECRET_ACCESS_KEY,
                        region_name=SECURE_KEYS.AWS_REGION)
queue_url = SECURE_KEYS.AWS_QUERY_URL


def send_queue(queue_url, message_body, message_attr):
    res = sqs_send.send_message(QueueUrl=queue_url, MessageBody=message_body,
                                MessageAttributes=message_attr,MessageGroupId='messageGroup1')
    return res


def receive_queue():
    # all_message = []
    response = sqs_send.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'data'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'data'
        ],
        VisibilityTimeout=60,
        WaitTimeSeconds=10
    )
    for message in response['Messages']:
        if 'MessageAttributes' in message:
            type = True
            data = response['Messages'][0]['MessageAttributes']['data']['StringValue']
        else:
            type= False
            data = response['Messages'][0]['Body']
        return {"data":str(data),
                "message_handler": response['Messages'][0]['ReceiptHandle'],
                "type": type }


# cretae demo subscription
@sqsRoute.route('/submit', methods=[ 'POST' , 'GET'])
def submit():
    if recaptcha.verify():
        get_name = request.form[ 'name' ]
        name = get_name.replace(".", "_")
        email = request.form[ 'email' ]
        check_email_verify = verify_email.check(email)
        if check_email_verify == "Success":
            data = Subscription.query.filter_by(email=email).first()
            if data:
                try:
                    get_logger_function('/submit', 'info',
                                        email + 'Email Already Exists!!',
                                        'cashier me site')
                    flash(gettext("Email Already Exists!!"))
                    return redirect('/subscriptions')
                except:
                    get_logger_function('/submit', 'error',
                                        'error for submit check email alraedy Exists this line code is 369',
                                        'cashier me site')
                    flash(gettext("Email Already Exists!!"))
                    return redirect('/subscriptions')
            else:
                from datetime import timedelta
                stores_number = '2'
                bs_name = request.form[ 'business_name' ]
                company_string_name = request.form[ 'business_name_string' ]
                business_name = bs_name.replace(".", "_")
                password = request.form[ 'password' ]
                file_taxess = request.form[ 'tax_number' ]
                commercial_register = request.form[ 'commercial_register' ]
                database_create_dt = datetime.now()
                if session[ 'country_code' ] == "TUR":
                    days = 31
                elif session['country_code'] == "EGY":
                    days = 16
                else:
                    days = 61
                expire_db = datetime.now() + timedelta(days)
                database_create_name = business_name.replace(" ", "")
                random_name = random.randint(1, 1000000)
                database_fullname = str(session["country_code" ]) + "_" + database_create_name + '_' + str(
                    random_name)
                best_time_call = request.form[ 'best_time_call' ]
                city = request.form[ 'city' ]
                country = request.form[ 'country' ]
                contact = request.form[ 'contact' ]
                street = request.form[ 'street' ]
                postcode = request.form[ 'postcode' ]
                created_from = 'From_site'
                company_token = random.randint(1, 100000000000000000)
                password_bcrypt = bcrypt.generate_password_hash(password).decode("utf-8")
                response = send_queue(queue_url, str(company_token), {"data":{
                    'StringValue':str({"name":str(name), "email":str(email),
                                       "stores_number":str(stores_number),
                                       "database_fullname":str(database_fullname),
                                       "best_time_call":str(best_time_call),
                                       "city":str(city), "contact":str(contact),
                                       "database_created_date":str(database_create_dt),
                                       "password":str(password),
                                       "file_taxes":str(file_taxess),
                                       "commercial_register":str(commercial_register),
                                       "expire_db":str(expire_db),
                                       "database_create_dt":str(database_create_dt),
                                       "country":str(country), "sub_type":"",
                                       "street":str(street),
                                       "postcode":str(postcode),
                                       "password_bcrypt":str(password_bcrypt),
                                       "company_string_name":str(
                                           company_string_name),
                                       "created_from":str(created_from),
                                       "company_token":str(company_token),
                                       "db_status":"pending",
                                       "account_type":"Demo",
                                       "country_code":str(
                                           session[ 'country_code' ])}),

                    'DataType':'String'},
                }
                                      )
                print(response)
                return render_template('success_subscription_demo.html',name=name,email=email,package=stores_number,expire_date=expire_db, reg_code=database_fullname)

        else:
            return redirect('/subscriptions')
    else:
        return redirect('/subscriptions')





import api_keys
import requests, json



def createDabaseFromRequestApi(dbname,
                               user_password,
                               company_name,
                               company_token,
                               company_country,
                               company_city,
                               company_address,
                               company_postcode,
                               company_commercial_record,
                               company_tax_file,
                               contact_mobile,
                               contact_email,
                               contact_name,
                               unit_count
                               ):
    try:
        the_request = {
            "dbname": str(dbname),
            "user_password": str(user_password),
            "company_name": str(company_name),
            "company_token": str(company_token),
            "company_country": str(company_country),
            "company_city": str(company_city),
            "company_address": str(company_address),
            "company_postcode": str(company_postcode),
            "company_commercial_record": str(company_commercial_record),
            "company_tax_file": str(company_tax_file),
            "contact_mobile": str(contact_mobile),
            "contact_email": str(contact_email),
            "contact_name": str(contact_name),
            "stores_number": str(unit_count),
            "best_time_call": "10pm",
        }
        response = requests.post(str(api_keys.api_url_request),
                                 data=json.dumps(the_request),
                                 headers={
                                     'api_auth_header': str(api_keys.api_auth_header),
                                     'content-type': 'application/json'}
                                 )
        datas = json.loads(response.content)
        get_logger_function('/createDabaseFromRequestApi', 'info',
                            str(the_request),
                            'cashier me site')
        get_logger_function('/createDabaseFromRequestApi', 'info',
                            str(datas),
                            'cashier me site')
        get_response_code = datas["Result"]["ErrNo"]
        get_response_status = datas["Result"]["ErrMsg"]
        if get_response_code == 0 and get_response_status == "Success":
            return {"status": "Activated", "message":""}
        else:
            return {"status": "Failed", "message":str(datas) }
    except Exception as Error:
        return {"status": "Error", "message": str(Error)}




@scheduler.task('interval', id='cashierme_coron_scheduler_for_test123456',seconds=30)
def get_aws_sqs_messages():
    try:
        get_message = receive_queue()
        operation_type = get_message['type']
        get_message_handler = str(get_message['message_handler'])
        message_handler = str(get_message['message_handler'])
        print(get_message)
        sqs_send.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message_handler)
        if operation_type is True:
            get_data = ast.literal_eval(get_message['data'])
            print(type(get_data))
            if not Subscription.query.filter_by(business_name = get_data['database_created_date'] ).first():
                    request_create_db_api = createDabaseFromRequestApi(str(get_data['database_fullname']),
                                                                                       str(get_data['password']),
                                                                                       str(get_data['company_string_name']),
                                                                                       str(get_data['company_token']),
                                                                                       str(get_data['country']),
                                                                                       str(get_data['city']),
                                                                                       str(get_data['street']),
                                                                                       str(get_data['postcode']),
                                                                                       str(get_data['commercial_register']),
                                                                                       str(get_data['file_taxes']),
                                                                                       str(get_data['contact']),
                                                                                       str(get_data['email']),
                                                                                       str(get_data['name']),
                                                                                       str(get_data['stores_number']))
                    get_db_status = request_create_db_api
                    add_record = Subscription(str(get_data['name']),
                                              str(get_data['email']),
                                              str(get_data['stores_number']),
                                              str(get_data['database_fullname']),
                                              str("10"),
                                              str(get_data['city']),
                                              str(get_data['contact']),
                                              str(get_data['database_created_date']),
                                              str(get_data['password']),
                                              str(get_data['file_taxes']),
                                              str(get_data['commercial_register']),
                                              str(get_data['expire_db']),
                                              str(get_data['database_created_date']),
                                              str(get_data['country']),
                                              str("Demo"),
                                              str(get_data['street']),
                                              str(get_data['postcode']),
                                              str(get_data['password_bcrypt']),
                                              str(get_data['company_string_name']),
                                              str(get_data['created_from']),
                                              str(get_data['company_token']),
                                              str(get_db_status['status']),
                                              str(get_db_status['message']),
                                              str(get_data['country_code']),
                                              str(get_data['account_type'])
                                              )
                    db.session.add(add_record)
                    db.session.commit()
                    try:
                        import mysql.connector
                        conMysql = mysql.connector.connect(user=SECURE_KEYS.DB_USER,  password=SECURE_KEYS.DB_PASSWORD, host='localhost', database=SECURE_KEYS.CONTROLLER_DB_NAME)
                        print("sssss")
                        status = 'Demo'
                        url = SECURE_KEYS.DASHBOARD_URL+get_data['database_fullname']
                        connect = conMysql.cursor()
                        connect.execute("INSERT INTO  subscriptions (full_name,company_name,url_unique_name,"
                                        "email,db_name, url_input,status,db_create_date,stores_number,contact,"
                                        "time_call,password,password_hash,company_string_name,tax_file,commercial_register,"
                                        "check_email_time,expire_db,country,street,postcode,subscription_type,created_from,sub_table_id ,company_token,db_status,country_code_id,alert_message,is_active)"
                                        " VALUES (%s, %s, %s,%s, %s, %s, %s, %s,%s,%s,%s, %s, %s,%s, %s, %s, %s, %s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s,%s)"
                                        ,(get_data['name'], get_data['database_fullname'], get_data['database_fullname'],get_data['email'],get_data['database_fullname'], url, status, get_data['database_created_date'],
                                          get_data['stores_number'],get_data['contact'] ,
                                          "10",get_data['password'],get_data['password_bcrypt'],get_data['company_string_name'],get_data['file_taxes'],get_data['commercial_register'],
                                          get_data['database_created_date'],get_data['expire_db'],get_data['country'],get_data['street'],get_data['postcode'],'Demo 60 Days',get_data['created_from'],
                                          add_record.id,get_data['company_token'],add_record.db_status,add_record.country_code_id,request_create_db_api['message'], True))
                        conMysql.commit()
                        connect.close()
                        conMysql.close()
                    except Exception as error:
                        print(error)
                        pass
                    get_logger_function ('get_aws_sqs_messages', 'info',str('success add record for recive sqs message>>>>')+str(add_record.name), 'cashier me site')
                    send_queue(queue_url, str(add_record.id),{})
            else:
                pass
        else:
            with app.test_request_context():
                rec = Subscription.query.filter_by(id=get_message['data']).first()
                sendSubscriptionEmail(rec.name, rec.business_name,"1", rec.password,rec.expire_db,rec.subscription_type,rec.email,rec.country_code_id)
        return sqs_send.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=get_message_handler,)
    except Exception as Error:
        # get_logger_function ('get_aws_sqs_messages', 'error',str('Error >>>>')+str(Error), 'cashier me site')
        print(Error)
        # get_logger_function('get_aws_sqs_messages', 'error',str(Error), 'cashier me site')
        # sqs_send.delete_message(
        #     QueueUrl=queue_url,
        #     ReceiptHandle=message_handler)


@sqsRoute.route('/checkAccountStatus', methods=['POST'])
def checkAccountStatus():
    try:
        api_request = request.json
        reg_code = api_request['reg_code']
        message = ""
        status = "Pending"
        check_account = Subscription.query.filter_by(business_name = reg_code).first()
        if check_account:
            status = check_account.db_status
            if check_account.db_status == "Activated":
                message = check_account.company_token
            else:
                message = check_account.notes
        return {"Result":str(status), "Msg":str(message)}
    except Exception as Error:
        print(Error)
        return {"Result": "Error", "Msg":str(Error)}

#
@sqsRoute.route('/checkAccountStatusNormal/<string:reg_code>', methods=['POST'])
def checkAccountStatusNormal(reg_code):
    try:
        message = ""
        status = "Pending"
        check_account = Subscription.query.filter_by(business_name = reg_code).first()
        if check_account:
            status = check_account.db_status
            if check_account.db_status == "Activated":
                message = check_account.company_token
                login_user(check_account)
                session['email'] = check_account.email
            else:
                message = check_account.notes
        return {"Result":str(status), "Msg":str(message)}
    except Exception as Error:
        print(Error)
        return {"Result": "Error", "Msg":str(Error)}
