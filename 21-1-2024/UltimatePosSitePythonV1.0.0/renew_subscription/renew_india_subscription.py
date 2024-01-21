from flask import Flask, render_template, request, redirect, json, Blueprint
from renew_subscription import renew
from app import *
from ultimate_saas_functions.paytabs_requests import paytabs_requests
from ultimate_saas_functions.add_order import add_order_record_from_current_user
from ultimate_saas_functions.update_order import update_order_record_from_current_user
from ultimate_saas_functions.delete_order import delete_order_record_from_current_user
from ultimate_saas_functions.expire_days_no import get_expire_days
from ultimate_saas_functions.generate_qr_code import generate_saudi_qr_code, generate_normal_qr_code
from ultimate_saas_functions.invoice_mail import send_email_for_upgrade_subscription
import SECURE_KEYS
import razorpay


@renew.route('/renew_india_subscription', methods=['POST'])
def renew_india_subscription() :
    try :
        get_order_id = current_user.order_id
        if current_user.expire_db <= datetime.now():
            get_order = Order.query.filter_by(id = get_order_id).first()
            amount = ""
            pos_no = ""
            if get_order.sub_type_toUpdate == 'yearly' :
                update_time = 366
            if get_order.sub_type_toUpdate is None and get_order.sub_type == 'yearly' :
                update_time = 366
            if get_order.sub_type_toUpdate == 'Monthly' :
                update_time = 31
            if get_order.sub_type_toUpdate is None and get_order.sub_type == 'Monthly' :
                update_time = 31
            if get_order.sub_type_toUpdate :
                add_subtype = get_order.sub_type_toUpdate
            else :
                add_subtype = get_order.sub_type
            if get_order.price_toUpdate :
                amount = get_order.price_toUpdate
            else :
                amount = get_order.amount
            if get_order.pos_no_toUpdate :
                pos_no = get_order.pos_no_toUpdate
            else :
                pos_no = get_order.stores_number
            price = int(amount) * 100
            client = razorpay.Client(
                auth=(SECURE_KEYS.RAZORPAY_ID,
                      SECURE_KEYS.RAZORPAY_SECRET))
            razorpay_data = {"amount" :price, "currency" :"INR",
                             "receipt" :"order_rcptid_11"}
            payment = client.order.create(data=razorpay_data)
            add_order_rec = Order(get_order.name, get_order.email, pos_no, get_order.business_name,
                  get_order.city, get_order.contact, get_order.password, get_order.tax_file,
                  get_order.commercial_register, datetime.now( ), get_order.street,
                  get_order.Country, get_order.postcode, 'in-progress', payment["id"], amount,
                  add_subtype
                  , datetime.now( )+timedelta(update_time), get_order.password_hash,
                  get_order.package_id, get_order.company_string_name)
            db.session.add(add_order_rec)
            db.session.commit()
            add_order_rec.razorpay_order_id = payment["id"]
            add_order_rec.payment_getway = "razorpay"
            add_order_rec.country_code_id = get_order.country_code_id
            add_order_rec.subscription_id = current_user.id
            db.session.commit()
            return payment
    except Exception as Error :
        print(Error)
        return "Error"
    return "Error"


#this function for upgrade subscrition
@app.route('/upgrade_subscription_india/<string:raz_order_id>/<string:raz_payment_id>/<string:raz_signature>', methods=['POST'])
def upgrade_subscription_india(raz_order_id,raz_payment_id,raz_signature):
    try:
        order_data = Order.query.filter(and_(Order.razorpay_order_id == raz_order_id)).first()
        order_data.order_id = order_data.id
        order_data.razorpay_payment_id = raz_payment_id
        order_data.razorpay_signature = raz_signature
        order_data.auto_payment_status = 'Done'
        order_data.account_type = "Live"
        get_qr_code = generate_normal_qr_code(order_data.amount)
        order_data.qr_code_base64 = get_qr_code["qr_code"]
        db.session.commit( )
        sub_data = Subscription.query.filter_by(id=order_data.subscription_id).first( )
        sub_data.order_id = order_data.id
        sub_data.stores_number = order_data.stores_number
        sub_data.plan_type = order_data.sub_type
        sub_data.price = order_data.amount
        sub_data.expire_db = order_data.expire_db
        sub_data.payment_status = 'Payment Successfully'
        sub_data.account_type = "Live"
        db.session.commit( )
        return {"status": "Success"}
    except Exception as Error:
        print(Error)
        return redirect("/")
    return {"status": "Errror"}