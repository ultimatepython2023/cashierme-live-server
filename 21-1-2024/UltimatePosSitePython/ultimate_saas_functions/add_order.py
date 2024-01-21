from flask import Flask
from app import *
from ultimate_saas_functions.generate_qr_code import generate_saudi_qr_code, generate_normal_qr_code



def add_order_record_from_current_user(user_id):
    try:
        get_data = Subscription.query.filter_by(id = user_id).first()
        if get_data:
            add_order = Order(get_data.name,
                              get_data.email,
                              get_data.stores_number,
                              get_data.business_name,
                              get_data.city,
                              get_data.contact,
                              get_data.password,
                              get_data.tax_file,
                              get_data.commercial_register,
                              datetime.now(),
                              get_data.street,
                              get_data.Country,
                              get_data.postcode,
                              "in-progress",
                              "",
                              get_data.price,
                              get_data.plan_type,
                              datetime.now()+ timedelta(1),
                              get_data.password_hash,
                              "",
                              get_data.company_string_name
                              )
            db.session.add(add_order)
            db.session.commit()
            add_order.subscription_id = user_id
            db.session.commit()
            return {"order_id":add_order.id }
    except Exception as Error:
        print(Error)
        pass

def upgrade_order_same_setting_turkish(ref_number, hash_number, number_of_days, user_id, country_code,):
    try:
        order_data = Order.query.filter_by(id=user_id).first()
        order_data.order_id = order_data.id
        order_data.tans_ref = ref_number
        order_data.auto_payment_status = 'Done'
        order_data.country_code_id = country_code
        order_data.expire_db = datetime.now()+timedelta(number_of_days)
        order_data.turkish_hash_number = hash_number
        order_data.account_type = "Live"
        get_qr_code = generate_normal_qr_code(order_data.amount)
        order_data.qr_code_base64 = get_qr_code["qr_code"]
        db.session.commit()
        sub_data = Subscription.query.filter_by(id=order_data.subscription_id).first()
        sub_data.order_id = order_data.id
        sub_data.expire_db = datetime.now( )+timedelta(number_of_days)
        sub_data.payment_status = 'Payment Successfully'
        sub_data.account_type = "Live"
        db.session.commit( )
        return {"status": "Success"}
    except Exception as Error:
        pass

def upgrade_demo_to_enterprise_turkish_(ref_number, hash_number, number_of_days, user_id, country_code,):
    try:
        order_data = Order.query.filter_by(id=user_id).first()
        order_data.order_id = order_data.id
        order_data.tans_ref = ref_number
        order_data.auto_payment_status = 'Done'
        order_data.country_code_id = country_code
        order_data.expire_db = datetime.now()+timedelta(number_of_days)
        order_data.turkish_hash_number = hash_number
        order_data.account_type = "Live"
        get_qr_code = generate_normal_qr_code(order_data.amount)
        order_data.qr_code_base64 = get_qr_code["qr_code"]
        db.session.commit()
        sub_data = Subscription.query.filter_by(id=order_data.subscription_id).first()
        sub_data.order_id = order_data.id
        sub_data.expire_db = datetime.now( )+timedelta(number_of_days)
        sub_data.payment_status = 'Payment Successfully'
        sub_data.subscription_type = "Enterprise"
        sub_data.plan_type = order_data.sub_type
        sub_data.price = order_data.amount
        sub_data.account_type = "Live"
        sub_data.stores_number = order_data.stores_number
        sub_data.name = order_data.name
        db.session.commit( )
        return {"status": "Success"}
    except Exception as Error:
        pass

# def upgrade_enterprise_order_same_setting_turkish(ref_number, hash_number, number_of_days, user_id, country_code,):
#     try:
#         order_data = Order.query.filter_by(id=user_id).first()
#         order_data.order_id = order_data.id
#         order_data.tans_ref = ref_number
#         order_data.auto_payment_status = 'Done'
#         order_data.country_code_id = country_code
#         order_data.expire_db = datetime.now()+timedelta(number_of_days)
#         order_data.turkish_hash_number = hash_number
#         order_data.account_type = "Live"
#         get_qr_code = generate_normal_qr_code(order_data.amount)
#         order_data.qr_code_base64 = get_qr_code["qr_code"]
#         db.session.commit()
#         return {"status": "Success"}
#     except Exception as Error:
#         pass



