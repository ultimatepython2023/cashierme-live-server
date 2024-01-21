from flask import Flask, render_template, request, redirect, json, Blueprint
from turkish_subscription import DemoToEnterprise
from app import *
from ultimate_saas_functions.paytabs_requests import paytabs_requests
from ultimate_saas_functions.add_order import add_order_record_from_current_user,upgrade_demo_to_enterprise_turkish_
from ultimate_saas_functions.update_order import update_order_record_from_current_user
from ultimate_saas_functions.delete_order import delete_order_record_from_current_user
from ultimate_saas_functions.expire_days_no import get_expire_days
from ultimate_saas_functions.generate_qr_code import generate_saudi_qr_code, generate_normal_qr_code
from ultimate_saas_functions.invoice_mail import send_email_for_upgrade_subscription
from ultimate_saas_functions.get_card_unique_key import get_unique_key
from ultimate_saas_functions.add_order import  upgrade_order_same_setting_turkish
from ultimate_saas_functions.payment_3d_turkish import payment_3d_turkish_request
from ultimate_saas_functions.duration_settings import get_duration
from ultimate_saas_functions.add_subscription import add_subscription_record
from ultimate_saas_functions.add_subscription_order import add_enterprise_record

from flask_bcrypt import Bcrypt


#>>>>>>>>>>>>>>>>> upgrade to Annualy ajax <<<<<<<<<<<<
@DemoToEnterprise.route('/update_subscription_to_yearly_turkish/<string:pos_num>', methods=['POST'])
def update_subscription_to_yearly_turkish(pos_num):
    get_price_annualy = get_price_of_package(pos_num, 'yearly' )
    print("##########################################################",get_price_annualy)
    total = get_price_annualy['price']
    Balance = get_price_annualy['Balance']
    to_payment_price = int(total) - int(Balance)
    print('>>>>>>>>>>>>>>>>>>>>',to_payment_price)
    get_order_id = current_user.order_id
    check_data = Order.query.filter_by(id = get_order_id).first()
    get_payment_data = Countries.query.filter_by(country_code = check_data.country_code_id).first()
    customer_token = check_data.customer_token
    check_package = Packages.query.filter(and_(Packages.type == 'yearly', Packages.pos_no_code == pos_num,Packages.country_code == session['country_code'])).first()
    random_code1 = random.randint(1, 100000)
    random_code2 = random.randint(1, 100000)
    order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
    add_ref_number = "REF_"+str(random.randint(1, 100000000))
    payment_request = payment_3d_turkish_request(
        get_payment_data.turkish_merchant_id,
        get_payment_data.turkish_merchant_key,
        SECURE_KEYS.CALL_BACK_URL,
        add_ref_number, to_payment_price,
        check_data.customer_token, check_data.name, check_data.email,
        check_data.street,2)
    print("^^^^^^^^^^^^^^^^", payment_request)
    if payment_request["STATUS"] == "SUCCESS" :
        get_logger_function('/update_subscription_to_yearly_turkish', 'info', 'the response from create 3d payment'+str(payment_request), 'cashier me site')
        check_data.tans_ref = add_ref_number
        db.session.commit()
        update_time = 366
        try:
            if payment_request["STATUS"] == "SUCCESS":
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
                                   Balance,
                                   'yearly'
                                   ,datetime.now()+ timedelta(update_time),
                                   check_data.password_hash,
                                   check_package.id,
                                   check_data.company_string_name)
                db.session.add(order_data)
                db.session.commit()
                order_data.order_id = order_data.id
                order_data.tans_ref = add_ref_number
                order_data.subscription_id = check_data.subscription_id
                order_data.auto_payment_status = 'Done'
                order_data.expire_db = datetime.now()+ timedelta(update_time)
                order_data.customer_token = customer_token
                order_data.sub_type_toUpdate = 'yearly'
                order_data.pos_no_toUpdate = pos_num
                order_data.price_toUpdate = total
                order_data.account_type = "Live"
                order_data.country_code_id = "TUR"
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
                    get_qr_code = generate_normal_qr_code(order_data.amount)
                    order_data.qr_code_base64 = get_qr_code["qr_code"]
                    db.session.commit( )
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
                                                   img_data=get_qr_code)
                        mail.send(msg)
                    except Exception as error:
                        get_logger_function('/update_subscription_to_yearly','error', str(error),'cashier me site')
                        pass
                except Exception as error:
                    get_logger_function('/update_subscription_to_yearly','error', str(error),'cashier me site')
                    print(error)
                    pass
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Payment Successful")
                get_logger_function('update_subscription_to_yearly','info', 'update payment is successfully created the tran_ref is>>>'+ str(add_ref_number) +'and order table id is >>> '+str(order_data.id) ,'cashier me site')
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