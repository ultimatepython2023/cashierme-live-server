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
from ultimate_saas_functions.add_order import  upgrade_order_same_setting_turkish
from ultimate_saas_functions.payment_3d_turkish import payment_3d_turkish_request
from ultimate_saas_functions.duration_settings import get_duration


#upgrade pos number in subscription monthly or Annualy
@DemoToEnterprise.route('/confirm_upgrade_posNo_subscription_monthly_for_turkish/<string:price_old>/<string:pos_no_get>/<string:sub_type>', methods=['POST'])
@check_coutry
def confirm_upgrade_posNo_subscription_monthly_for_turkish(price_old,pos_no_get,sub_type):
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
        get_payment_data = Countries.query.filter(and_(Countries.country_code ==current_user.country_code_id,Countries.payment_getway == "esnekpos")).first()
        get_customer_token = get_data.customer_token
        order_code = "REF_"+str(random.randint(1, 100000000))
        payment_request = payment_3d_turkish_request(
            get_payment_data.turkish_merchant_id,
            get_payment_data.turkish_merchant_key,
            SECURE_KEYS.CALL_BACK_URL,
            order_code, price,
            get_customer_token, get_data.name,
            get_data.email,
            get_data.street,2)
        get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','info', 'invoice (QR) created successfully for>>>>'+get_data.business_name,'cashier me site')
        try:
            if payment_request['STATUS'] == "SUCCESS":
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
                trans_ref = order_code
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
                    get_qr_code = generate_normal_qr_code(create_order.amount)
                    create_order.qr_code_base64 = get_qr_code["qr_code"]
                    db.session.commit()
                    get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','info', 'invoice (QR) created successfully for>>>>'+get_data.business_name,'cashier me site')
                    # try:
                    #     msg = Message(recipients=[email])
                    #     msg.body = gettext('User No :') + '1' +  '\n'+ gettext('password :') + get_data.password + '\n'+ gettext('Registration Code For Application:')+ '\n'+get_data.business_name+ '\n'+ gettext('Update Subscription in:')+ get_data.expire_db.strftime("%b %d %Y")+'\n'+ SECURE_KEYS.DASHBOARD_URL+get_data.business_name
                    #     msg.html = render_template('invoicess.html',
                    #                                password = get_data.password,
                    #                                database_fullname = get_data.business_name,
                    #                                name = get_data.name,
                    #                                address = get_data.street,
                    #                                city = get_data.city,
                    #                                country = get_data.Country,
                    #                                zip = get_data.postcode,
                    #                                package = pos_no,
                    #                                company = get_data.business_name,
                    #                                domain = SECURE_KEYS.DASHBOARD_URL+get_data.business_name,
                    #                                subscription = get_data.sub_type,
                    #                                expire = get_data.expire_db,
                    #                                price = price,
                    #                                invoice_num = str(create_order.id),
                    #                                invoice_date = datetime.now(),
                    #                                img_data=get_qr_base64)
                    #     mail.send(msg)
                    # except Exception as error:
                    #     get_logger_function('/confirm_upgrade_posNo_subscription_monthly','error', str(error),'cashier me site')
                    #     print(error)
                    #     pass
                except Exception as error:
                    get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','error', str(error),'cashier me site')
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
                    get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','info', 'update pos no has been successfully updated in subscription table'+get_data.business_name,'cashier me site')
                    return jsonify({"status":"success",
                                    "value":create_order.id})
                except Exception as error:
                    get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','error', str(error),'cashier me site')
                    print(error)
                    return "Failed_update"
            elif payment_request['STATUS'] == 'ENCRYPT_CARDs':
                get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','info', 'customer not have money in cared to update point of sale'+get_data.business_name,'cashier me site')
                return "customer_havenot_money"
            elif payment_request['STATUS'] == 'FAILEDs':
                get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','info', 'paytabs not proccess this transaction please try again'+get_data.business_name,'cashier me site')
                print("D")
                return "Cant_process_now"
            else:
                get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','info', 'you have response code not add in system please fixed this code and search in paytabs to fixed it'+get_data.business_name,'cashier me site')
                return "get_code_error"
        except Exception as error:
            get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','error', str(error),'cashier me site')
            print(error)
            return "error_for_request"
    except Exception as error:
        get_logger_function('/confirm_upgrade_posNo_subscription_monthly_for_turkish','error', str(error),'cashier me site')
        print(error)
        return "Error"