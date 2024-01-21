from request_api import req_api
from app import *
from flask import request
import verify_auth_api
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
                                MessageAttributes=message_attr,MessageGroupId='messageGroup1'
                                )
    return res


@req_api.route('/IsCustomerExist', methods=['POST','GET'])
def is_customer_exists():
    try:
        check_auth_value = verify_auth_api.check_header_auth ()
        if check_auth_value == "Auth":
            get_post_data = request.json
            get_logger_function('IsCustomerExist','info', 'the request'+str(get_post_data) ,'cashier me site')
            customer_email = get_post_data['customer_email']
            customer_mobile_number = get_post_data['customer_mobile_number']
            print(get_post_data)
            if customer_email and not customer_mobile_number:
                check_data = Subscription.query.filter_by(email = str(customer_email)).first()
                if check_data:
                    return jsonify({'Result':True, "ErrorMsg":"", "db_name":check_data.business_name, "subscription_type": check_data.subscription_type,"company_token":check_data.company_token})
                else:
                    return jsonify({'Result':False,"ErrorMsg":"", "db_name":"", "subscription_type":""})
            elif customer_mobile_number and not customer_email:
                check_data = Subscription.query.filter_by(contact = str(customer_mobile_number)).first()
                if check_data:
                    return jsonify({'Result':True,"ErrorMsg":"","db_name":check_data.business_name, "subscription_type": check_data.subscription_type,"company_token":check_data.company_token})
                else:
                    return jsonify({'Result':False,"ErrorMsg":"","db_name":"", "subscription_type":""})
            elif customer_mobile_number and customer_email:
                check_data = Subscription.query.filter(and_(Subscription.contact == str(customer_mobile_number), Subscription.email == str(customer_email))).first()
                if check_data:
                    return jsonify({'Result':True,"ErrorMsg":"","db_name":check_data.business_name, "subscription_type": check_data.subscription_type,"company_token":check_data.company_token})
                else:
                    return jsonify({'Result':False,"ErrorMsg":"","db_name":"", "subscription_type":""})
            else:
                return jsonify({"Result":"Failed",'ErrorMsg':'Error please check your param',"db_name":"", "subscription_type":""})
        else:
            return jsonify({"Result":"Error",'ErrorMsg':'unauthorized',"db_name":"", "subscription_type":""})
    except Exception as Error:
        return jsonify({"Result":"Error",'ErrorMsg':str(Error),"db_name":"", "subscription_type":""})



@req_api.route('/CreateSubscription', methods=['POST', 'GET'])
def createSubscriptionFromApi():
    try:
        check_auth_value = verify_auth_api.check_header_auth ()
        if check_auth_value == "Auth":
            get_post_data = request.json
            get_logger_function('createSubscriptionFromApi','info', 'the request'+str(get_post_data) ,'cashier me site')
            dbname = get_post_data['dbname'].replace(" ", "")
            user_password = get_post_data['user_password']
            company_name = get_post_data['company_name']
            company_token = random.randint(1,100000000000000000)
            company_country = get_post_data['company_country']
            company_city = get_post_data['company_city']
            company_address = get_post_data['company_address']
            company_postcode = get_post_data['company_postcode']
            company_commercial_record = get_post_data['company_commercial_record']
            company_tax_file = get_post_data['company_tax_file']
            contact_mobile = get_post_data['contact_mobile'].replace(" ", "")
            contact_email = get_post_data['contact_email']
            contact_name = get_post_data['contact_name']
            stores_number = get_post_data['stores_number']
            database_create_dt = datetime.now()
            best_time_call = "10pm"
            country_code_list = ["SAU", "TUR", "EGY", "MYS", "IND", "GLB", "GEO"]
            country_code_id = ""
            if str(dbname[0:3]) in country_code_list:
                country_code_id = str(dbname[0:3])
            else:
                country_code_id = "GLB"
            if dbname[0:3] == "TUR":
                days = 31
            else:
                days = 61

            expire_db = datetime.now()+ timedelta(days)
            password_bcrypt = bcrypt.generate_password_hash(user_password).decode("utf-8")
            check_reg_code = Subscription.query.filter_by(business_name = dbname).first()
            if check_reg_code:
                return jsonify({"Result":"Failed",'ErrorMsg': dbname + " "+ "already exists",'CompanyToken':""})
            else:
                check_email = Subscription.query.filter(and_(Subscription.email == contact_email, Subscription.contact == contact_mobile)).first()
                if check_email:
                    return jsonify({"Result":"Failed",'ErrorMsg': "email or contact number" + " "+ "already exists"})
                else:
                    if dbname and company_name and company_token and company_country and contact_name and stores_number:
                        if contact_email or contact_mobile:
                                response = send_queue(SECURE_KEYS.AWS_QUERY_URL, str(company_token), {"data":{
                                    'StringValue':str({"name":str(contact_name), "email":str(contact_email),
                                                       "stores_number":str(stores_number),
                                                       "database_fullname":str(dbname),
                                                       "best_time_call":str(best_time_call),
                                                       "city":str(company_city), "contact":str(contact_mobile),
                                                       "database_created_date":str(database_create_dt),
                                                       "password":str(user_password),
                                                       "file_taxes":str(company_tax_file),
                                                       "commercial_register":str(company_commercial_record),
                                                       "expire_db":str(expire_db),
                                                       "database_create_dt":str(database_create_dt),
                                                       "country":str(company_country),
                                                       "sub_type": str("Demo"),
                                                       "street":str(company_address),
                                                       "postcode":str(company_postcode),
                                                       "password_bcrypt":str(password_bcrypt),
                                                       "company_string_name":str(
                                                           company_name),
                                                       "created_from":str("api"),
                                                       "company_token":str(company_token),
                                                       "db_status":"pending",
                                                       "account_type":"Demo",
                                                       "country_code":country_code_id}),

                                    'DataType':'String'},
                                }
                                                      )
                                print(response)
                                get_logger_function('createSubscriptionFromApi','info', 'the request'+str(response) ,'cashier me site')
                                return jsonify({"Result":"Success"})
                            # else:
                            #     return jsonify({"Result":"Failed",'ErrorMsg':'tax file or commercial registration  is null','CompanyToken': "" })
                        else:
                            return jsonify({"Result":"Failed",'ErrorMsg':'email or contact number is null','CompanyToken': "" })
                    else:
                        return jsonify({"Result":"Failed",'ErrorMsg':'some fields null','CompanyToken': "" })
        else:
            return jsonify({"Result":"Error",'ErrorMsg':"unauthorized",'CompanyToken': ""})
    except Exception as Error:
        return jsonify({"Result":"Error",'ErrorMsg':str(Error),'CompanyToken':""})




