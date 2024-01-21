from flask import Flask
from app import *



def create_esnekpos_requests(amount, name, email,city,contact,street,callback_url):
    try:
        get_payment_data = Countries.query.filter_by(payment_getway ="esnekpos").first()
        merchant_id = str(get_payment_data.turkish_merchant_id)
        print(merchant_id)
        merchant_key = str(get_payment_data.turkish_merchant_key)
        print(merchant_key)
        print(get_payment_data.payment_request_api_url)
        email = str(email)
        payment_amount = str(amount)
        data_random =  random.randint(1,1000000000000000000)
        order_ref_number = str(data_random)
        user_name = str(name)
        user_address =str(city+"_"+ street)
        user_phone = str(contact)
        merchant_ok_url = str(SECURE_KEYS.CALL_BACK_URL + "/" + callback_url)
        print("ima>>>>>>>>>>>>>>goto 112111")
        params = {
                    "Config" :  {
                        "MERCHANT" : str(merchant_id),
                        "MERCHANT_KEY" : str(merchant_key),
                        "ORDER_REF_NUMBER" : str(order_ref_number),
                        "ORDER_AMOUNT" : str(payment_amount),
                        "PRICES_CURRENCY" : "TRY",
                        "BACK_URL" : str(merchant_ok_url),
                        "LOCALE" : "tr"
                    },
                    "Customer" : {
                         "FIRST_NAME" : str(user_name),
                         "LAST_NAME" : "cashierme",
                         "MAIL" : email,
                         "PHONE" : "05435434343",
                         "CITY" : "İstanbul",
                         "STATE" : "Kağıthane",
                         "ADDRESS" : str(user_address)
                    }
                 }
        api_request = requests.post(
            "https://posservice.esnekpos.com/api/pay/CommonPaymentDealer",
            data=json.dumps(params), headers={"content-type":"application/json"})
        res = json.loads(api_request.content)
        if res['STATUS'] == 'SUCCESS' :
            print(res['RETURN_CODE'])
            print(res['URL_3DS'])
            print(res['REFNO'])
            print(res['HASH'])
            print(res['ORDER_REF_NUMBER'])
            RETURN_CODE = res['RETURN_CODE']
            STATUS = res['STATUS']
            URL_3DS = res['URL_3DS']
            REFNO = res['REFNO']
            HASH = res['HASH']
            ORDER_REF_NUMBER = res['ORDER_REF_NUMBER']
            return {"RETURN_CODE":str(RETURN_CODE),
                    "STATUS":str(STATUS),
                    "URL_3DS":str(URL_3DS),
                    "REFNO":str(REFNO),
                    "HASH":str(HASH),
                    "ORDER_REF_NUMBER":str(ORDER_REF_NUMBER)
                                        }
        else:
            print('esnekpos_request_result',api_request.text)
            return {"token": "Error"}
        return {"token": "Error"}
    except Exception as Error:
        print('esnekpos_request_result',Error)


# { 'DATE' :'3.08.2022 02:33:28',
#   'HASH' :'0afc7596cf7d875ae5e03e65d433dffe3c2d1b3b5da6ddbd963b116c6e5ad3e2',
#   'ORDER_REF_NUMBER' :'896190608138689120',
#   'REFNO' :'3584789',
#   'RETURN_CODE' :'ISO8583-14',
#   'RETURN_MESSAGE' :'Gecersiz hesap numarasi. (hostmsg:[RC 14] Red Hatalı Kart - Invalid Card)',
#   'RETURN_MESSAGE_TR' :'Gecersiz hesap numarasi. (hostmsg:[RC 14] Red Hatalı Kart - Invalid Card)',
#   'STATUS' :'Declined',
#   'ERROR_CODE' :'ISO8583-14',
#   'CUSTOMER_NAME' :'sameer mostafa cashierme',
#   'CUSTOMER_MAIL' :'ssamerfasthey2002@gmail.com',
#   'CUSTOMER_PHONE' :'05435434343', 'CUSTOMER_ADDRESS' :'cairo_test1',
#   'CUSTOMER_CC_NUMBER' :'453144******2283', 'CUSTOMER_CC_NAME' :'SAMIR MOSTAFA',
#   'COMMISSION' :'147,33', 'AMOUNT' :'7403,59', 'INSTALLMENT' :'1' }
