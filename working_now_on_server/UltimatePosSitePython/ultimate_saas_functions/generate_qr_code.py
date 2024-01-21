from flask import Flask
from app import *


def generate_saudi_qr_code(amount_parm):
    try:
        saller_name = 'Ultimate Solutions'
        seller_len = len(saller_name)
        vat_number = '311136332100003'
        dateandtime = datetime.now( ).strftime('%Y-%m-%dT%H:%M:%SZ')
        amount = str(amount_parm)
        amounts = amount_parm
        get_len = len(amount)
        tax = round(int(amounts)-(int(amounts) / 1.15), 2)
        get_tax_len = len(str(tax))
        company2hex = hexaConvertFunction.string2hex(saller_name)
        fullCompany2hex = '01'+str(hexaConvertFunction.int2hex(seller_len))+company2hex
        vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
        fullnumber2hex = '020F'+vatnumber2hex
        datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
        fulldatetimehex = '0314'+datetimeInvoicehex
        amount2hexa = hexaConvertFunction.string2hex(amount)
        fulamount2hexa = '040'+str(get_len)+amount2hexa
        tax2hexa = hexaConvertFunction.string2hex(str(tax))
        fulltax2hexa = '050'+str(get_tax_len)+tax2hexa
        get_qr_base64 = hexa2base64.hex2funbase64(fullCompany2hex+fullnumber2hex+fulldatetimehex+fulamount2hexa+fulltax2hexa)
        return {"status": "Done",
                "qr_code": get_qr_base64}
    except Exception as Error:
        print(Error)
        return {"status": "Error"}


def generate_normal_qr_code(amount_parm):
    try:
        saller_name = 'Ultimate Solutions'
        vat_number = '311136332100003'
        dateandtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        amount = str(amount_parm)
        amounts = amount_parm
        tax = round(int(amounts)-(int(amounts) / 1.15), 2)
        company2hex = hexaConvertFunction.string2hex(saller_name)
        vatnumber2hex = hexaConvertFunction.string2hex(vat_number)
        datetimeInvoicehex = hexaConvertFunction.string2hex(dateandtime)
        amount2hexa = hexaConvertFunction.string2hex(amount)
        tax2hexa = hexaConvertFunction.string2hex(str(tax))
        get_qr_base64 = hexa2base64.hex2funbase64(company2hex+vatnumber2hex+datetimeInvoicehex+amount2hexa+tax2hexa)
        return {"status": "Done",
                "qr_code": get_qr_base64}
    except Exception as Error:
        print(Error)
        return {"status": "Error"}

