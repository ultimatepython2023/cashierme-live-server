from flask import Flask, render_template, request, redirect, json, Blueprint
from malaysia_subscription import malaysia_sub
from app import *
from ultimate_saas_functions.paytabs_requests import paytabs_requests
from ultimate_saas_functions.add_order import add_order_record_from_current_user
from ultimate_saas_functions.update_order import update_order_record_from_current_user
from ultimate_saas_functions.delete_order import delete_order_record_from_current_user
from ultimate_saas_functions.expire_days_no import get_expire_days
from ultimate_saas_functions.generate_qr_code import generate_saudi_qr_code, generate_normal_qr_code
from ultimate_saas_functions.invoice_mail import send_email_for_upgrade_subscription
from ultimate_saas_functions.get_card_unique_key import get_unique_key
from ultimate_saas_functions.add_order import  upgrade_order_same_setting_turkish
from ultimate_saas_functions.payment_3d_turkish import payment_3d_turkish_request
from ultimate_saas_functions.duration_settings import get_duration





#calling this function by paytabs callback function
@malaysia_sub.route('/get_response_revpay', methods=['POST','GET'])
def get_response_revpay():
    '''very import function its return and calling by payment getway  *revpay*
    1- get api and check data
    2- check transaction ref from api and search this to order table if exist or Not
    3-if transaction exists send api to get all transaction information
    4-if status == 00 can be created database and send email and created qr code for invoice'''
    get_response_data = request.json
    # get_response_data = request.json
    if get_response_data:
        get_transaction_ref = get_response_data['Reference_Number']
        if get_transaction_ref:
            get_data = Order.query.filter_by(tans_ref = get_transaction_ref).first()
            get_json_transaction_ref = get_transaction_ref
            get_response_status = get_response_data['Response_Code']
            # get_response_message = get_json_payment_result['Error_Description']
            if get_data.tans_ref == get_json_transaction_ref:
                get_logger_function('/get_transaction','info', 'get response from payment getway successfully','cashier me site')
                print('ok')
                if get_response_status == "3D":
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
                    created_from = 'From_site'
                    company_token = random.randint(1,100000000000000000)
                    if not Subscription.query.filter(and_(Subscription.name == name, Subscription.email == email, Subscription.contact == contact)).first():
                        data = Subscription(name, email ,stores_number, database_fullname,
                                            best_time_call, city, contact,database_create_dt,password,
                                            file_taxess,commercial_register,expire_db,database_create_dt,
                                            country,'Enterprise',get_data.street,get_data.postcode,
                                            password_bcrypt,company_string_name,created_from,company_token, "","","","")
                        db.session.add(data)
                        db.session.commit()
                        data.db_status = "pending"
                        data.order_id = get_data.id
                        data.payment_status = 'Payment Successfully'
                        data.plan_type = get_data.sub_type
                        data.price = get_data.amount
                        data.country_code_id = get_data.country_code_id
                        data.payment_getway = "revpay"
                        data.account_type = "Live"
                        db.session.commit()
                        get_data.subscription_id = data.id
                        get_data.auto_payment_status = 'Done'
                        get_data.expire_db = expire_db
                        get_data.account_type = "Live"
                        db.session.commit()
                        # import mysql.connector
                        # try:
                        #     conMysql = mysql.connector.connect(user=SECURE_KEYS.DB_USER,  password=SECURE_KEYS.DB_PASSWORD, host='localhost', database=SECURE_KEYS.CONTROLLER_DB_NAME)
                        #     if conMysql:
                        #         status = 'Enterprise'
                        #         url = SECURE_KEYS.DASHBOARD_URL+database_fullname
                        #         connect = conMysql.cursor()
                        #         connect.execute("INSERT INTO  subscriptions (full_name,company_name,url_unique_name,"
                        #                         "email,db_name, url_input,status,db_create_date,stores_number,contact,"
                        #                         "time_call,password,password_hash,company_string_name,tax_file,commercial_register,"
                        #                         "check_email_time,expire_db,country,street,postcode,subscription_type,created_from,sub_table_id,company_token )"
                        #                         " VALUES (%s, %s, %s,%s, %s, %s, %s, %s,%s,%s,%s, %s, %s,%s, %s, %s, %s, %s,%s,%s, %s,%s,%s,%s,%s)"
                        #                         ,(name, business_name, database_fullname, email,database_fullname, url, status, database_create_dt,stores_number,contact ,
                        #                           best_time_call,password,password_bcrypt,company_string_name,file_taxess,commercial_register,
                        #                           database_create_dt,expire_db,country,get_data.street,get_data.postcode,get_data.sub_type,created_from,data.id,company_token ))
                        #         conMysql.commit()
                        #     else:
                        #         return redirect('/')
                        # except Exception as error:
                        #     get_logger_function ('/get_transaction', 'error',
                        #                          'error for create in db controller' +str(error),
                        #                          'cashier me site')

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



