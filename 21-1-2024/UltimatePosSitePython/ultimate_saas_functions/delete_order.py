from flask import Flask
from app import *


def delete_order_record_from_current_user(order_id):
    try:
        get_data = Order.query.filter_by(id = order_id).first()
        if get_data:
            db.session.delete(get_data)
            db.session.commit()
            return {"status":"Success"}
    except Exception as Error:
        print(Error)
        return {"status": "Error"}