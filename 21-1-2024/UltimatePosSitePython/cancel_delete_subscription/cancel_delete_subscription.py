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

@cs.route('/cancel_delete_account', methods=['POST', "GET"])
@login_required
def cancel_delete_account():
    seven_days_to_delete = datetime.now()+timedelta(days=7)
    delete_account_date = seven_days_to_delete.strftime("%Y-%m-%d")
    delete_account_time = seven_days_to_delete.strftime('%I:%M %p')
    return render_template('delete_account.html',delete_account_date= delete_account_date, delete_account_time=delete_account_time)


@cs.route('/confirm_cancel_subscription', methods=['POST', 'GET'])
@login_required
@check_coutry
def confirm_cancel_subscription():
    get_id = current_user.id
    status = request.form['cancel_subscription']
    check_sub_data = Subscription.query.filter_by(id = get_id).first()
    try:
        add_seven_days = datetime.now()+timedelta(days=7)
        check_order_data = Order.query.filter_by(id= check_sub_data.order_id).first()
        check_sub_data.subscription_status = status
        if status == 'Delete':
            check_sub_data.delete_account_at = add_seven_days
        if check_order_data:
            check_order_data.auto_payment_status = status
        db.session.commit()
        get_logger_function('/confirm_cancel_subscription','info', 'Canceled subscription successfully'+check_sub_data.business_name,'cashier me site')
        return redirect('/cancel_delete_account')
    except Exception as error:
        print(error)
        get_logger_function('/confirm_cancel_subscription','error', str(error) +'error for cancel subscription for this'+check_sub_data.business_name,'cashier me site')
        return redirect('/cancel_delete_account')
