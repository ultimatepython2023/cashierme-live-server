from flask import Flask
from app import *


def send_email_for_upgrade_subscription(email, order_id):
    try :
        data = Order.query.filter_by(id = order_id).first()
        if data:
            msg = Message(recipients=[email])
            msg.html = render_template('invoicess.html',
                                       password=data.password,
                                       database_fullname=data.business_name,
                                       name=data.name,
                                       address=data.street,
                                       city=data.city,
                                       country=data.Country,
                                       zip=data.postcode,
                                       package=data.stores_number,
                                       company=data.business_name,
                                       domain=SECURE_KEYS.DASHBOARD_URL + data.business_name,
                                       subscription=data.sub_type,
                                       expire=data.expire_db,
                                       price=data.amount,
                                       invoice_num=str(data.id),
                                       invoice_date=datetime.now(),
                                       img_data=data.qr_code_base64)
            mail.send(msg)
            return {"status": "Success"}
        else:
            pass
    except Exception as error :
        get_logger_function('/send_email_for_upgrade_subscription', 'error',
                            str(error), 'cashier me site')
        print(error)
        return {"status": "Error"}


