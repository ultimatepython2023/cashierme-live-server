import json
import requests
from flask import Flask
from app import *
import SECURE_KEYS


def payment_3d_turkish_request(merchant_name, merchant_key, callback_url, ref_number,amount, UNIQUE_KEY,customer_name,email,address, method_no) :
    '''Get Unique key for card with api the unique key
    its used for recurring payment and normal payment'''
    try :
        get_ip = request.remote_addr
        data ={
            "Config":{
                "MERCHANT":str("cashierme.com"),
                "MERCHANT_KEY":str("BSDFQx8d1bx6khXNB+V2+CJST2VMoLGabPKnF0P8D8ZhN/wivEov3A=="),
                "BACK_URL":str(callback_url),
                "PRICES_CURRENCY":"TRY",
                "ORDER_REF_NUMBER": str(ref_number),
                "ORDER_AMOUNT":str(amount),
                "USER_ID":"",
                "BY_WHO":"",
                "METHOD":method_no
            },
            "CreditCard":{
                "INSTALLMENT_NUMBER":"1",
                "UNIQUE_KEY": str(UNIQUE_KEY)
            },
            "Customer":{
                "FIRST_NAME":str(customer_name),
                "LAST_NAME":"-",
                "MAIL":str(email),
                "PHONE":"05435434343",
                "CITY":"İstanbul",
                "STATE":"Kağıthane",
                "ADDRESS":str(address),
                "CLIENT_IP":str(get_ip)
            }
        }
        response = requests.post(str("https://posservice.esnekpos.com/api/pay/EYV3DPay"), data=json.dumps(data),headers={ "Content-Type" :"application/json"})
        get_data = json.loads(response.content)
        print('>>>>>>RESPONSE ',response.text)
        STATUS = get_data['STATUS']
        RETURN_CODE = get_data['RETURN_CODE']
        RETURN_MESSAGE = get_data['RETURN_MESSAGE']
        HASH = get_data['HASH']
        ORDER_REF_NUMBER = get_data['ORDER_REF_NUMBER']
        URL_3D = get_data['URL_3DS']
        print(UNIQUE_KEY)
        print(RETURN_CODE)
        print(RETURN_MESSAGE)
        print(HASH)
        print(ORDER_REF_NUMBER)
        if RETURN_CODE == "0" and STATUS == "SUCCESS":
            return {"STATUS" :"SUCCESS", "HASH": str(HASH),"RETURN_CODE": str(RETURN_CODE) , "ORDER_REF_NUMBER": str(ORDER_REF_NUMBER), "response": str(get_data), "CUSTOMER_IP": str(get_ip), "URL_3D": str(URL_3D)}
        elif RETURN_CODE == "93":
            return {"STATUS" :"ENCRYPT_CARD", "MESSAGE": RETURN_MESSAGE, "response": str(get_data), "HASH": str("HASH")}
        elif RETURN_CODE == "58":
            return {"STATUS": "INVALID_TURKISH_CARD", "MESSAGE": RETURN_MESSAGE,"response": str(get_data), "HASH": str("HASH")}
        else :
            return {"STATUS" :"FAILED", "MESSAGE": str(RETURN_MESSAGE),"response": str(get_data), "HASH": str("HASH")}
    except Exception as Error :
        print(">>>>>>>>>>>>",Error)
        return {"STATUS": "Error", "MESSAGE": str(Error),"RETURN_CODE": str("101"), "HASH": str("HASH")  }

