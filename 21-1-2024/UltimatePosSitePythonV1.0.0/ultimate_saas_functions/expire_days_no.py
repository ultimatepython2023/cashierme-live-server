from flask import Flask
from app import *



def get_expire_days(subscription_type,account_type):
    try:

        if subscription_type == 'yearly':
            days_no = 366
        elif subscription_type == 'Monthly':
            days_no = 31
        elif account_type != "Test":
            days_no = 180
        else:
            days_no = 0
        return {"days_no": days_no}
    except Exception as Error:
        print(Error)
        return {"status": "Error"}