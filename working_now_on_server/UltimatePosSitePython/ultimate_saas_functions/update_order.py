from flask import Flask
from app import *


def update_order_record_from_current_user(order_id,transaction_ref, subscription_id):
    try:
        get_data = Order.query.filter_by(id = order_id).first()
        if get_data:
            get_data.tans_ref = transaction_ref
            get_data.subscription_id = subscription_id
            db.session.commit()
            return {"status":"Success" }
    except Exception as Error:
        print(Error)
        return {"status": "Error"}