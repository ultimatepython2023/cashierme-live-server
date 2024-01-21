from flask import Flask
from app import *


def paytabs_requests(cart_description,cart_id,amount, name, email,city,contact,street,country_code,callback_url ):
    get_payment_data = Countries.query.filter(
        and_(Countries.country_code == country_code)).first( )
    create_json = {'profile_id' :str(
        get_payment_data.payment_merchant_id),
        'tran_type' :str('sale'),
        'tran_class' :str('ecom'),
        "tokenise" :"2",
        'cart_description' :str(cart_description),
        'cart_id' :str(cart_id),
        'cart_currency' :str(get_payment_data.payment_currency),
        'cart_amount' :float(amount),
        'callback' :str(SECURE_KEYS.CALL_BACK_URL + callback_url),
        'return' :str(SECURE_KEYS.CALL_BACK_URL + callback_url),
        "hide_shipping" :True,
        'customer_details' :{
            'name' :str(name),
            'email' :str(email),
            'city' :str(city),
            'phone' :str(contact),
            'street1' :str(street),
            'country' :"SA",
            'state' :"Makkah"
        }}
    response = requests.post(str(get_payment_data.payment_request_api_url),
                             data=json.dumps(create_json), headers={
            'authorization' :str(get_payment_data.payment_api_key),
            'content-type' :'https://cashierme.com/json'})
    print(response.content)
    datas = json.loads(response.content)
    print(datas.get('redirect_url'))
    get_url_response = datas.get('redirect_url')
    transaction_ref = datas.get('tran_ref')
    print(transaction_ref)
    return {"redirect_url": get_url_response,
            "transaction_ref": transaction_ref}