import requests
from flask import Flask, request

api_auth_key = '965845^er-lL988E2L-CA122984-MRVO962'


def check_header_auth():
    try:
        header = request.headers["auth"]
        if str(header) == api_auth_key:
            return "Auth"
        else:
            return "Failure"
    except Exception as Error:
        print(Error)
        return "Error"
        pass

def check_header_auth_admin():
    try:
        header = request.headers["cashier-backend-auth-header"]
        if str(header) == api_auth_key:
            return "Auth"
        else:
            return "Failure"
    except Exception as Error:
        print(Error)
        return "Error"
        pass



