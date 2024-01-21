import random

from flask import redirect, render_template, request, json, jsonify
from payment_card import card
from ultimate_saas_functions.get_card_unique_key import get_unique_key
from ultimate_saas_functions.add_order import add_order_record_from_current_user, upgrade_order_same_setting_turkish
from ultimate_saas_functions.payment_3d_turkish import payment_3d_turkish_request
from ultimate_saas_functions.duration_settings import get_duration
from app import *



@card.route('/paymentCard')
def paymentCard():
    return render_template('payment_card.html')



@card.route('/paymentCardSubmit/<string:Card_Number>/<string:Card_Name>/<string:expirymonth>/<string:expiryyear>/<string:Card_CvC>', methods=['POST', 'GET'])
def paymentCardSubmit(Card_Number,Card_Name,expirymonth,expiryyear,Card_CvC ):
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
            if get_status == "SUCCESS":
                print("Success")
                unique_key = generate_unique_key['UNIQUE_KEY']
                create_order = add_order_record_from_current_user(current_user.id)
                order_id = create_order['order_id']
                if order_id:
                    update_order = Order.query.filter_by(id=order_id).first()
                    update_order.customer_token = unique_key
                    db.session.commit()
                    add_ref_number = "REF_"+str(random.randint(1,100000000))
                    payment_request = payment_3d_turkish_request(get_turkish_payment_data.turkish_merchant_id,
                                                                 get_turkish_payment_data.turkish_merchant_key,
                                                                 "https://cashierme.com/testrevpay",
                                                                 add_ref_number,update_order.amount,
                                                                 unique_key,update_order.name,update_order.email,update_order.street)
                    print("^^^^^^^^^^^^^^^^",payment_request)
                    if payment_request["STATUS"] == "SUCCESS" :
                        get_days = get_duration(update_order.sub_type)
                        upgrade_order = upgrade_order_same_setting_turkish(add_ref_number,payment_request['HASH'],get_days["duration"],update_order.id,"TUR")
                        if upgrade_order['status'] == "Success":
                            # return redirect('/view_invoice/'+str(update_order.id))
                            return {"status": "Success", "order_id": str(update_order.id)}
                    else:
                        # return redirect('/invoices')
                        return {"status": "Failed",}

                else:
                    pass
            elif get_status == "FAILED":
                code = generate_unique_key['RETURN_CODE']
                message = generate_unique_key['MESSAGE']
                # return render_template('payment_card.html',message=message ,code=code)
                return {"status": "Error", "message": message, "Code": code}


            else:
                code = generate_unique_key['RETURN_CODE']
                message = generate_unique_key['MESSAGE']
                # return render_template('payment_card.html', message=message,
                #                        code=code)
                return { "status" :"Error", "message" :message, "Code" :code }
        else:
            return {"status": "fields_error"}
    except Exception as Error:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>ssss>>>>>>>>>>",Error)
        # return redirect('/paymentCard')
        return {"status": "function_error"}
