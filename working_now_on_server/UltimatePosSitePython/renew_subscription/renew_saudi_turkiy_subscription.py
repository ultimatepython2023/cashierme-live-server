from flask import Flask, render_template, request, redirect, json, Blueprint
from renew_subscription import renew
from app import *
from ultimate_saas_functions.paytabs_requests import paytabs_requests
from ultimate_saas_functions.add_order import add_order_record_from_current_user
from ultimate_saas_functions.update_order import update_order_record_from_current_user
from ultimate_saas_functions.delete_order import delete_order_record_from_current_user
from ultimate_saas_functions.expire_days_no import get_expire_days
from ultimate_saas_functions.generate_qr_code import generate_saudi_qr_code, generate_normal_qr_code
from ultimate_saas_functions.invoice_mail import send_email_for_upgrade_subscription


@renew.route('/upgrade_subscription_renew', methods=['POST', 'GET'])
def upgrade_subscription_renew():
    try:
        if current_user.account_type == "Test" and current_user.country_code_id == "TUR":
            get_countries_data = Countries.query.filter_by(country_code = "TUR").first()
            calculation_payment_amount = float(current_user.price) * float(get_countries_data.usd_convert)
            payment_amount = Decimal(float(calculation_payment_amount)).quantize(Decimal('.01'),rounding=ROUND_DOWN)

            get_transaction_ref = paytabs_requests("test","123456789", payment_amount, current_user.name, current_user.email,current_user.city,current_user.contact,current_user.street,current_user.country_code_id,"/get_response_from_paytabs_for_upgrade_subscription")
            add_order_record = add_order_record_from_current_user(current_user.id)
            update_order_record = update_order_record_from_current_user(add_order_record['order_id'], get_transaction_ref['transaction_ref'],current_user.id )
            if update_order_record["status"] == "Success":
                return redirect(get_transaction_ref['redirect_url'])
            else:
                delete_order_record_from_current_user(add_order_record['order_id'])
                return redirect('/invoices')
        else:
            return redirect("/")
    except Exception as Error:
        print(Error)
        return redirect("/")


@renew.route('/get_response_from_paytabs_for_upgrade_subscription',methods=['POST'] )
def get_response_from_paytabs_for_upgrade_subscription():
    try:
        get_response = request.form.to_dict()
        if get_response :
            get_transaction_ref = get_response['tranRef']
            get_transaction_token = get_response['token']
            get_transaction_message = get_response['respMessage']
            get_transaction_status = get_response['respStatus']
            if get_transaction_status == "A" and get_transaction_message == "Authorised":
                check_order_data = Order.query.filter_by(tans_ref = get_transaction_ref).first()
                check_subscription_data = Subscription.query.filter_by(id = check_order_data.subscription_id).first()
                if check_order_data and check_subscription_data:
                    print("Iam check th order and  >>>>>>>>>>>> sameer")
                    get_days = get_expire_days(check_subscription_data.plan_type, check_subscription_data.account_type)
                    check_order_data.customer_token = get_transaction_token
                    check_order_data.amount = check_subscription_data.price
                    check_order_data.country_code_id = check_subscription_data.country_code_id
                    check_order_data.sub_type_toUpdate = check_subscription_data.plan_type
                    check_order_data.sub_type = check_subscription_data.plan_type
                    check_order_data.pos_no_toUpdate = check_subscription_data.stores_number
                    check_order_data.price_toUpdate = check_subscription_data.price
                    check_order_data.payment_getway = "paytabs"
                    check_order_data.account_type = "Live"
                    check_order_data.expire_db = datetime.now()+timedelta(get_days['days_no'])
                    check_order_data.auto_payment_status = 'Done'
                    db.session.commit()
                    check_subscription_data.account_type = "Live"
                    check_subscription_data.order_id = check_order_data.id
                    check_subscription_data.expire_db = datetime.now()+timedelta(get_days['days_no'])
                    db.session.commit()
                    try:
                        get_qr_code = generate_normal_qr_code(check_subscription_data.price)
                        check_order_data.qr_code_base64 = get_qr_code["qr_code"]
                        db.session.commit()
                    except Exception as Error:
                        print(Error)

                    # try:
                    #     send_email_for_upgrade_subscription(check_order_data.email,check_order_data.id)
                    # except Exception as Error:
                    #     print(Error)
                    #     pass
                    return redirect('/invoices')
            elif get_transaction_status == "E":
                return "/"
            else:
                return "/"
        else:
            return "/"
    except Exception as Error:
        print(Error)
        return {"test":str(Error)}



















































# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> automatic Payment Scheduler >>>>>>>>>>>>>>>>>>
@scheduler.task('interval', id='do_jo125222',seconds=84400)
def check_payment_update():
    try:
        print("start job")
        get_data = Order.query.filter(and_(Order.expire_db < datetime.now(), Order.auto_payment_status != 'Failed',Order.auto_payment_status != 'invalid_process', Order.auto_payment_status != 'Canceled')).all()
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
                        db.session.commit()
                        sub_data = Subscription.query.filter_by(id = data.subscription_id).first()
                        sub_data.order_id = order_data.id
                        sub_data.stores_number = order_data.stores_number
                        sub_data.plan_type = order_data.sub_type
                        sub_data.price = order_data.amount
                        sub_data.expire_db = datetime.now()+ timedelta(update_time)
                        sub_data.payment_status = 'Payment Successfully'
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
                        order_data.customer_token = get_data.customer_token
                        order_data.auto_payment_status = 'Failed'
                        order_data.country_code_id = data.country_code_id
                        db.session.commit()
                        sub_data = Subscription.query.filter_by(id = data.subscription_id).first()
                        sub_data.order_id = order_data.id
                        sub_data.expire_db = datetime.now()
                        sub_data.plan_type = get_data.sub_type
                        sub_data.price = get_data.amount
                        sub_data.payment_status = 'Payment Failed'
                        db.session.commit()
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Payment Failed")
                        get_logger_function('check_payment_update','info', 'update payment is failed created the tran_ref is>>>'+ get_json_transaction_ref +'and order table id is >>> '+order_data.id ,'cashier me site')
                else:
                    data.auto_payment_status = 'invalid_process'
                    db.session.commit()
                    get_logger_function('check_payment_update','error', 'error for send request to paytabs the tran_ref is >>> '+transaction_ref,'cashier me site')
                    print("error response   >>>>>>>>>> for >>>>>",transaction_ref,response.content)
    except Exception as Error:
        print(Error)
        get_logger_function('check_payment_update', 'error','error in check payment upgrade scheduler function please check this and the error is >>>>>'+str(Error),'cashier me site')



