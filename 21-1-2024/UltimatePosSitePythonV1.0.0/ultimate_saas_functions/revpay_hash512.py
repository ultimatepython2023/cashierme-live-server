import json
from flask import Flask, render_template, json
import hashlib
import requests


def get_hashing(merchant_id,m_key,ref_number,amount):
    merchant_id = merchant_id
    m_key = m_key
    ref_number = ref_number
    amount = amount
    currency = "MYR"
    signature_value = m_key + merchant_id + ref_number + amount + currency
    get_hashing_code = hashlib.sha512(signature_value.encode('utf-8')).hexdigest()
    return {"hash": str(get_hashing_code)}