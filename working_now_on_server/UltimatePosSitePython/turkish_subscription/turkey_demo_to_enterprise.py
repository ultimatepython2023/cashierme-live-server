from flask import Flask, render_template, request, redirect, json, Blueprint
from turkish_subscription import DemoToEnterprise
from app import *
from ultimate_saas_functions.paytabs_requests import paytabs_requests
from ultimate_saas_functions.add_order import add_order_record_from_current_user
from ultimate_saas_functions.update_order import update_order_record_from_current_user
from ultimate_saas_functions.delete_order import delete_order_record_from_current_user
from ultimate_saas_functions.expire_days_no import get_expire_days
from ultimate_saas_functions.generate_qr_code import generate_saudi_qr_code, generate_normal_qr_code
from ultimate_saas_functions.invoice_mail import send_email_for_upgrade_subscription
from ultimate_saas_functions.get_card_unique_key import get_unique_key
from ultimate_saas_functions.add_order import upgrade_order_same_setting_turkish
from ultimate_saas_functions.payment_3d_turkish import payment_3d_turkish_request
from ultimate_saas_functions.duration_settings import get_duration



@DemoToEnterprise.route('/upgrade_payment_url_redirect', methods=['POST', 'GET'])
def upgrade_payment_url_redirect():
    try:
        get_data = request.form.to_dict()
        get_logger_function('/upgrade_payment_url_redirect', 'info', 'response from redirect '+str(get_data), 'cashier me site')
        return_code = get_data['RETURN_CODE']
        order_ref = get_data['ORDER_REF_NUMBER']
        if return_code == "0":
            get_order = Order.query.filter_by(tans_ref = str(order_ref)).first()
            if get_order:
                get_days = get_duration(get_order.sub_type)
                upgrade_order = upgrade_demo_to_enterprise_turkish_(order_ref,get_data['HASH'],get_days["duration"],get_order.id,"TUR")
                if upgrade_order['status'] == "Success" :
                    session['language'] = "tr"
                    message = gettext('The process has been completed successfully. Please check your email for registration information. ')
                    return render_template('enterprise_payment_result.html'
                                           , get_url =SECURE_KEYS.DASHBOARD_URL + get_order.business_name,
                                           message_sucssess = message,
                                           name = get_order.name,
                                           address = get_order.street,
                                           city = get_order.city,
                                           country = get_order.Country,
                                           zip = get_order.postcode,
                                           package = get_order.stores_number,
                                           company = get_order.business_name,
                                           domain =SECURE_KEYS.DASHBOARD_URL + get_order.business_name,
                                           subscription = get_order.sub_type,
                                           expire = get_order.expire_db,
                                           price = get_order.amount,
                                           invoice_num = str(get_order.order_id ),
                                           invoice_date = datetime.now(),
                                           img_data=get_order.qr_code_base64,
                                           email = get_order.email,
                                           password = get_order.password,
                                           session_language = "tr"
                                           ),cleanup(db.session)
        else:
            get_logger_function('/payment_url_redirect_turkish','info', '"The process cannot be completed, please try another payment card if you want to back pricing page','cashier me site')
            message_error = get_data['RETURN_MESSAGE']
            return render_template('enterprise_payment_result.html', get_url='https://cashierme.com/pricing',message_error = str(message_error) ),cleanup(db.session)

    except Exception as Error:
        get_logger_function('/payment_url_redirect_turkish', 'Error', 'Error form redirect payment '+str(Error), 'cashier me site')
        return redirect('/')



@DemoToEnterprise.route('/upgradeDemoToEnterpriseTurkishSubscription/<string:name>/<string:bs_name_string>/<string:pos_num>/<string:vat_number>/<string:commercial_register>/<string:phone>/<string:country>/<string:city>/<string:street>/<string:Card_Number>/<string:Card_Name>/<string:expirymonth>/<string:expiryyear>/<string:Card_CvC>/<string:sub_type>/<string:postcode>', methods=['POST','GET'])
def upgradeDemoToEnterpriseTurkishSubscription(name,bs_name_string,
                                                pos_num,vat_number,commercial_register,phone,
                                                country,city,street,Card_Number,Card_Name,
                                                expirymonth,expiryyear,Card_CvC,sub_type,postcode ):
    try:
        if Card_Name and Card_Number and expiryyear and expirymonth and Card_CvC != "":
            card_number = Card_Number.replace(" ", "")
            # get payment getway data
            get_turkish_payment_data = Countries.query.filter(and_(Countries.country_code == "TUR", Countries.payment_getway == "esnekpos")).first()
            print("ok")
            # generate unique key for payment it will be return json status
            generate_unique_key = get_unique_key(get_turkish_payment_data.turkish_merchant_id,
                                                 get_turkish_payment_data.turkish_merchant_key,
                                                 card_number,
                                                 Card_Name,
                                                 expirymonth,
                                                 expiryyear,
                                                 Card_CvC)
            get_status = generate_unique_key['STATUS']
            get_logger_function('/upgradeDemoToEnterpriseTurkishSubscription', 'info', 'the response from create card is '+str(generate_unique_key), 'cashier me site')
            if get_status == "SUCCESS":
                print("Success")
                unique_key = generate_unique_key['UNIQUE_KEY']
                create_order = add_enterprise_record(name,current_user.email,pos_num,current_user.business_name,city,
                                                     phone,current_user.password,vat_number,commercial_register,
                                                     street,country,postcode,sub_type,bs_name_string,"TUR")
                order_id = create_order['order_id']
                if order_id :
                    add_ref_number = "REF_"+str(random.randint(1, 100000000))
                    update_order = Order.query.filter_by(id=order_id).first( )
                    update_order.customer_token = unique_key
                    update_order.subscription_id = current_user.id
                    update_order.tans_ref = add_ref_number
                    db.session.commit( )
                    payment_request = payment_3d_turkish_request(
                        get_turkish_payment_data.turkish_merchant_id,
                        get_turkish_payment_data.turkish_merchant_key,
                        SECURE_KEYS.CALL_BACK_URL + "/upgrade_payment_url_redirect",
                        add_ref_number, update_order.amount,
                        unique_key, update_order.name, update_order.email,
                        update_order.street,1)
                    print("^^^^^^^^^^^^^^^^", payment_request)
                    get_logger_function('/upgradeDemoToEnterpriseTurkishSubscription', 'info', 'the response from create 3d payment'+str(payment_request), 'cashier me site')
                    if payment_request["STATUS"] == "SUCCESS" :
                        return {"status": "Success","URL": str(payment_request['URL_3D']) }
                    else :
                        get_logger_function('/create_turkish_enterprise_subscription_live', 'info',str(payment_request), 'cashier me site')
                        ERROR_MESSAGE = payment_request["MESSAGE"]
                        return {"status": "Failed", "message": str(ERROR_MESSAGE) }
            else :
                return { "status" :"Error", }
        else :
            print("error2")
            return { "status" :"fields_error" }
    except Exception as Error:
        print(Error,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    return { "status" :"fields_error" }



def add_enterprise_record (name, email,stores_number,business_name,city,contact,password,
                           tax_file,commercial_register,street,Country,postcode,plan_type,company_string_name, country_id):
    password_bcrypt = bcrypt.generate_password_hash(password).decode("utf-8")
    get_data = Packages.query.filter(
        and_(Packages.type == plan_type, Packages.pos_no_code == stores_number,
             Packages.country_code == str(country_id))).first( )

    price = get_data.price
    try :
        add_order = Order(name,email,stores_number,business_name,city,contact,
                          password,tax_file,commercial_register,datetime.now( ),
                          street,Country,postcode,"in-progress","",price,plan_type,
                          datetime.now( )+timedelta(1),password_bcrypt,"",company_string_name
                          )
        db.session.add(add_order)
        db.session.commit( )
        return { "order_id" :add_order.id }
    except Exception as Error :
        print(Error)
        pass

def upgrade_demo_to_enterprise_turkish_(ref_number, hash_number, number_of_days, user_id, country_code,):
    try:
        order_data = Order.query.filter_by(id=user_id).first()
        order_data.order_id = order_data.id
        order_data.tans_ref = ref_number
        order_data.auto_payment_status = 'Done'
        order_data.country_code_id = country_code
        order_data.expire_db = datetime.now()+timedelta(number_of_days)
        order_data.turkish_hash_number = hash_number
        order_data.account_type = "Live"
        get_qr_code = generate_normal_qr_code(order_data.amount)
        order_data.qr_code_base64 = get_qr_code["qr_code"]
        db.session.commit()
        sub_data = Subscription.query.filter_by(id=order_data.subscription_id).first()
        sub_data.order_id = order_data.id
        sub_data.expire_db = datetime.now( )+timedelta(number_of_days)
        sub_data.payment_status = 'Payment Successfully'
        sub_data.subscription_type = "Enterprise"
        sub_data.plan_type = order_data.sub_type
        sub_data.price = order_data.amount
        sub_data.account_type = "Live"
        sub_data.stores_number = order_data.stores_number
        sub_data.name = order_data.name
        db.session.commit( )
        return {"status": "Success"}
    except Exception as Error:
        pass