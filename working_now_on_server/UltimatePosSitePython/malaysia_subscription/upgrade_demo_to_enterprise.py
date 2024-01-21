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
@malaysia_sub.route('/getResponseForUpgrade_malaysia_subscription', methods=['POST', 'GET'])
def getResponseForUpgrade_malaysia_subscription():
    '''very import function its return and calling by payment getway  *paytabs*
    1- get api and check data
    2- check transaction ref from api and search this to order table if exist or Not
    3-if transaction exists send api to get all transaction information
    4-if status == A can be upgrade subscription to enterprise and send email and created qr code for invoice'''
    #get_response_data = request.form.to_dict()
    get_response_data = request.form.to_dict()
    # get_response_data = request.json
    # get_logger_function('/get_transaction','info', 'get response >>>>>>'+str(get_response_data),'cashier me site')
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
                    get_data.account_type = "Live"
                    db.session.commit()
                    database_name = 'upos_'+data.business_name
                    # import mysql.connector
                    # try:
                    #     conMysql = mysql.connector.connect(user=SECURE_KEYS.DB_USER,  password=SECURE_KEYS.DB_PASSWORD, host='localhost', database=SECURE_KEYS.CONTROLLER_DB_NAME)
                    #     url = SECURE_KEYS.DASHBOARD_URL+data.business_name
                    #     connect = conMysql.cursor()
                    #     connect.execute("UPDATE  subscriptions set  full_name='"+str(data.name)+"',db_name='"+str(database_name)+
                    #                     "', url_input='"+str(url)+"',status='"+ str(data.subscription_type)+"',stores_number='"
                    #                     +str(data.stores_number)+"',contact='"+str(data.contact)+"',time_call='"+str(data.best_time_call)+"',password='"+str(data.password)
                    #                     +"',password_hash='"+str(data.password_hash)+"',company_string_name='"+str(data.company_string_name)+"',tax_file='"
                    #                     +str(data.tax_file)+"',commercial_register='"+str(data.commercial_register)+"',expire_db='"+str(data.expire_db)
                    #                     +"',country='"+str(data.Country)+"',street='"+str(data.street)+"',postcode='"+str(data.postcode)+"',subscription_type='"
                    #                     +str(get_data.sub_type)+"',created_from='"+str(data.created_from)+"',sub_table_id='"+str(data.id)+"',company_token='"+
                    #                     str(data.company_token)+"' where db_name='"+str(data.business_name)+"' ")
                    #     conMysql.commit()
                    # except Exception as error:
                    #     get_logger_function('/getResponseForUpgrade_subscription','error', 'error for update data in upos_controller subscription table'+database_name ,'cashier me site')
                    #     get_logger_function('/getResponseForUpgrade_subscription','error', str(error) + '---> from exption error from  the database upos_controller----> ' ,'cashier me site')
                    #     pass
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
                    # try:
                    #     msg = Message(recipients=[email])
                    #     msg.html = render_template('invoicess.html',
                    #                                password = data.password,
                    #                                database_fullname = data.business_name,
                    #                                name = get_data.name,
                    #                                address = get_data.street,
                    #                                city = get_data.city,
                    #                                country = get_data.Country,
                    #                                zip = get_data.postcode,
                    #                                package = get_data.stores_number,
                    #                                company = get_data.business_name,
                    #                                domain = SECURE_KEYS.DASHBOARD_URL+data.business_name,
                    #                                subscription = get_data.sub_type,
                    #                                expire = get_data.expire_db,
                    #                                price = get_data.amount,
                    #                                invoice_num = str(get_data.id ),
                    #                                invoice_date = datetime.now(),
                    #                                img_data=get_qr_base64)
                    #     mail.send(msg)
                    # except Exception as error:
                    #     get_logger_function('/getResponseForUpgrade_subscription','error', str(error),'cashier me site')
                    #     pass
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




