from flask import Flask , jsonify , request , json , session , render_template , \
    redirect
from flask_login import login_user, login_required, LoginManager, UserMixin, logout_user, current_user

from flask_mail import Mail , Message

import requests
import random

import requests
from datetime import datetime , timedelta
import hexaConvertFunction
import hexa2base64
import app
import SECURE_KEYS
from ChangeCard import changeCard
import verify_auth_api
from app import Subscription, Order , Countries , db
from cancel_delete_subscription import cs
from app import *



@cs.route('/reactive_subscription', methods=['POST'])
@login_required
def reactive_subscription():
    get_id = current_user.id
    check_sub_data = Subscription.query.filter_by(id = get_id).first()
    try:
        check_order_data = Order.query.filter_by(id= check_sub_data.order_id).first()
        check_sub_data.subscription_status = ''
        check_sub_data.delete_account_at = None
        if check_order_data:
            check_order_data.auto_payment_status = ''
        db.session.commit()
        get_logger_function('/confirm_cancel_subscription','info', 'reactive  subscription successfully'+check_sub_data.business_name,'cashier me site')
        return redirect('/invoices'),cleanup(db.session)
    except Exception as error:
        print(error)
        get_logger_function('/confirm_cancel_subscription','error', str(error) +'error for reactive subscription for this'+check_sub_data.business_name,'cashier me site')
        return redirect('/invoices'),cleanup(db.session)