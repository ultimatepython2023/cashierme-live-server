from flask import Flask , jsonify , request , json , session , render_template , \
    redirect
from flask_login import login_user, login_required, LoginManager, UserMixin, logout_user, current_user

from flask_mail import Mail , Message

import requests
import random

import requests
from datetime import datetime , timedelta
import hexaConvertFunction
import hexa2base64
import app
import SECURE_KEYS
from ChangeCard import changeCard
import verify_auth_api
from app import Subscription, Order , Countries , db


@changeCard.route('/check_response_status/<string:transaction_ref>', methods=['POST', 'GET'])
def check_response_status_fun(transaction_ref):
    get_payment_data = Countries.query.filter_by(country_code = "SAU").first()
    get_data = Order.query.filter_by(tran_ref_to_update = transaction_ref).first()
    if get_data:
        data = {
            'profile_id': get_payment_data.payment_merchant_id,
            'tran_ref':str(get_data.tran_ref_to_update)
        }
    res = requests.post(get_payment_data.payment_query_link, data=json.dumps(data),headers = {'authorization':get_payment_data.payment_api_key,'content-type':'https://cashierme.com/get_transaction'})
    result = json.loads(res.content)
    print(result)
    return str(result)

@changeCard.route('/change_credit_card')
def change_credit_card():
    return render_template('change_credit_card.html')

@changeCard.route('/change_card_form_site', methods=['POST', 'GET'])
def change_card_form_site():
    if current_user.country_code_id == 'SAU':
        try:
            get_user_id = current_user.id
            get_cs_data = Subscription.query.filter_by(id = get_user_id).first()
            get_order_data = Order.query.filter_by(id = current_user.order_id).first()
            try:
                random_code1 = random.randint(1, 100000)
                random_code2 = random.randint(1, 100000)
                order_code = str(random_code1)+ '-'+ str(random_code2)+'-'+str(datetime.now().date())
                get_payment_data = Countries.query.filter_by(country_code = "SAU").first()
                if get_payment_data.payment_getway == "paytabs" :
                    create_json = {'profile_id':get_payment_data.payment_merchant_id,
                                   'tran_type':str('sale'),
                                   'tran_class':str('ecom'),
                                   "tokenise": "2",
                                   'cart_description':str("add new card"),
                                   'cart_id':str(order_code),
                                   'cart_currency':get_payment_data.payment_currency,
                                   'cart_amount':"1.00",
                                   'callback':str(SECURE_KEYS.CALL_BACK_URL+'/change_card_response'),
                                   'return':str(SECURE_KEYS.CALL_BACK_URL+'/change_card_response'),
                                   "hide_shipping": True,
                                   'customer_details':{
                                       'name':str(get_cs_data.name),
                                       'email': str(get_cs_data.email),
                                       'city': str(get_cs_data.city),
                                       'phone':str(get_cs_data.contact),
                                       'street1': str(get_cs_data.street),
                                       'country': "SA",
                                       'state': "Makkah"
                                   }}
                    try:
                        response = requests.post(get_payment_data.payment_request_api_url,
                                                 data = json.dumps(create_json),
                                                 headers = {'authorization':get_payment_data.payment_api_key ,
                                                            'content-type':'https://saas-mplus.ultimate-test.com//json'})
                        print(response.content)
                        datas = json.loads(response.content)
                        print(datas.get('redirect_url'))
                        get_url_response = datas.get('redirect_url')
                        transaction_ref = datas.get('tran_ref')
                        get_order_data.tran_ref_to_update = transaction_ref
                        db.session.commit()
                        return redirect(get_url_response)
                    except Exception as Error:
                        print(Error)
                        return {"status":"invalid"}
            except Exception as Error:
                print(Error)
                return {"status":"invalid", "msg": str(Error)}

        except Exception as error:
            print(error)
            return render_template('change_credit_card.html', name = current_user.name)
    else:
        return render_template('change_credit_card.html', name = current_user.name)



@changeCard.route('/change_card_response', methods=['POST','GET'])
def change_card_response():
    get_response_data = request.form.to_dict()
    # get_logger_function('/get_transaction','info', 'get response >>>>>>'+str(get_response_data),'cashier me site')
    if get_response_data:
        get_transaction_ref = get_response_data['tranRef']
        get_transaction_token = get_response_data['token']
        if get_transaction_ref:
            get_payment_data = Countries.query.filter_by(country_code = "SAU").first()
            get_data = Order.query.filter_by(tran_ref_to_update = get_transaction_ref).first()
            if get_data:
                data = {
                    'profile_id': get_payment_data.payment_merchant_id,
                    'tran_ref':str(get_data.tran_ref_to_update)
                }
            res = requests.post(get_payment_data.payment_query_link, data=json.dumps(data),headers = {'authorization':get_payment_data.payment_api_key,'content-type':'https://cashierme.com/get_transaction'})
            result = json.loads(res.content)
            print(result)
            get_json_transaction_ref = result.get('tran_ref')
            get_json_payment_result = result.get('payment_result')
            get_response_status = get_json_payment_result['response_status']
            get_response_message = get_json_payment_result['response_message']
            if get_data.tran_ref_to_update == get_json_transaction_ref:
                # app.get_logger_function('/change_card_response','info', str(result),'cashier me site')
                print('ok')
                if get_response_status == "A" and get_response_message == "Authorised":
                    get_data.tran_ref_old = get_data.tans_ref
                    get_data.cs_token_old = get_data.customer_token
                    get_data.tans_ref = get_transaction_ref
                    get_data.customer_token = result.get('token')
                    db.session.commit()
                    return render_template('change_credit_card.html', message_success= "success")
                else:
                    return render_template('change_credit_card.html', alert_message= get_response_message)
            else:
                return render_template('change_credit_card.html', alert_message= 'cannot process your request now please try again later or contact with us')
        else:
            return render_template('change_credit_card.html', alert_message= 'cannot process your request now please try again later or contact with us')
    else:
        return render_template('change_credit_card.html', alert_message= 'cannot process your request now please try again later or contact with us')

# {'tran_ref': 'TST2310001554235', 'tran_type': 'Sale', 'cart_id': '7676-26777-2023-04-10', 'cart_description': 'test', 'cart_currency': 'EGP', 'cart_amount': '1.00', 'tran_currency': 'EGP', 'tran_total': '1.00', 'customer_details': {'name': 'sameer mostafa', 'email': 'samefathey2002@gamil.com', 'phone': '+201558414779', 'street1': 'test1, 12', 'city': 'cairo', 'state': '02', 'country': 'SA', 'zip': '26352', 'ip': '156.210.114.242'}, 'payment_result': {'response_status': 'A', 'response_code': 'G32567', 'response_message': 'Authorised', 'transaction_time': '2023-04-10T13:16:07Z'}, 'payment_info': {'payment_method': 'Visa', 'card_type': 'Credit', 'card_scheme': 'Visa', 'payment_description': '4111 11## #### 1111', 'expiryMonth': 11, 'expiryYear': 2023}, 'serviceId': 2, 'token': '2C4653BE67A3E937C6B390FF66867CBC', 'profileId': 85475, 'merchantId': 34495, 'trace': 'PMNT0403.64340DE4.0005AB5A'}
