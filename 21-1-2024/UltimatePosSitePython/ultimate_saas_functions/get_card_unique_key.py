import json
import requests
from flask import Flask
from app import *
import SECURE_KEYS


def get_unique_key (merchant_name, merchant_key, card_number, card_name,
                    expire_month, expire_year, card_ccv) :
    '''Get Unique key for card with api the unique key
    its used for recurring payment and normal payment'''
    try :
        data = {
            "MERCHANT" :str("cashierme.com"),
            "MERCHANT_KEY" :str("BSDFQx8d1bx6khXNB+V2+CJST2VMoLGabPKnF0P8D8ZhN/wivEov3A=="),
            "CUSTOMER_GSM" :str("05327985256"),
            "CUSTOMER_FULL_NAME" :str(card_name),
            "CARD_NUMBER" :str(card_number),
            "CARD_EXPIRE_YEAR" :str(expire_year),
            "CARD_EXPIRE_MONTH" :str(expire_month)
        }
        response = requests.post(str("https://posservice.esnekpos.com/api/card/addcard"), data=json.dumps(data),
                                 headers={ "Content-Type" :"application/json"})
        get_data = json.loads(response.content)
        print(response.text)
        UNIQUE_KEY = get_data['UNIQUE_KEY']
        RETURN_CODE = get_data['RETURN_CODE']
        RETURN_MESSAGE = get_data['RETURN_MESSAGE']
        print(RETURN_CODE)
        if RETURN_CODE == "0" :
            return {"STATUS" :"SUCCESS", "UNIQUE_KEY": str(UNIQUE_KEY),"RETURN_CODE": str(RETURN_CODE) }
        else :
            return {"STATUS" :"FAILED", "MESSAGE": str(RETURN_MESSAGE),"RETURN_CODE": str(RETURN_CODE) }
    except Exception as Error :
        print(">>>>>>>>>>>>",Error)
        return {"STATUS": "Error", "MESSAGE": str(Error),"RETURN_CODE": str(RETURN_CODE)  }
