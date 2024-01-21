from admin_panel.pagination_with_serve import Paginate as P
from admin_panel import admin_panel
from admin_panel import check_token_expired as CHECK_TOKEN
from app import *
import random


@admin_panel.route('/get_data_with_model_name', methods=['POST','GET'])
def get_data_with_model_name():
    try:
        check_auth_value = verify_auth_api.check_header_auth_admin ()
        if check_auth_value == "Auth":
            print ("auth")
            try:
                pass
            except:
                pass
        else:
            return {"status": "fail", "message": "un authenticated header"}

    except Exception as e:
        print(e)
        return {"status": "error", "message":str(e)}


def get_countries_available_for_admin_account(user_object):
    try:
        is_saudi = user_object.is_saudi
        is_turkey = user_object.is_turkey
        is_india = user_object.is_india
        is_malaysia = user_object.is_malaysia
        is_global = user_object.is_global
        is_egypt = user_object.is_egypt
        is_georgia = user_object.is_georgia
        if is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt and is_georgia:
            return ["SAU", "TUR", "IND", "MYS", "GLB", "EGY","GEO"]
        elif is_saudi and is_turkey and is_india and is_malaysia and is_global and is_egypt:
            return ["SAU", "TUR", "IND", "MYS", "GLB", "EGY"]
        elif is_saudi and is_turkey and is_india and is_malaysia and is_global:
            return ["SAU", "TUR", "IND", "MYS", "GLB"]
        elif is_saudi and is_turkey and is_india and is_malaysia:
            return ["SAU", "TUR", "IND", "MYS"]
        elif is_saudi and is_turkey and is_india:
            return ["SAU", "TUR", "IND"]
        elif is_saudi and is_turkey:
            return ["SAU", "TUR"]
        elif is_saudi:
            return ["SAU"]
        elif is_turkey:
            return ["TUR"]
        elif is_india:
            return ["IND"]
        elif is_malaysia:
            return ["MYS"]
        elif is_egypt:
            return ["EGY"]
        elif is_global:
            return ["GLB"]
        elif is_georgia:
            return ["GEO"]
        else:
            return []
    except Exception as e:
        return []


def get_subscription_type_count_for_countries():
    try:
        with app.test_request_context():
            return {
            "len_saudi_demo" : len(Subscription.query.filter(and_(Subscription.country_code_id == "SAU", Subscription.subscription_type =="Demo" )).all()),
            "len_saudi_enterprise" : len(Subscription.query.filter(and_(Subscription.country_code_id == "SAU", Subscription.subscription_type =="Enterprise" )).all()),
            "len_egypt_demo" : len(Subscription.query.filter(and_(Subscription.country_code_id == "EGY", Subscription.subscription_type =="Demo" )).all()),
            "len_egypt_enterprise" : len(Subscription.query.filter(and_(Subscription.country_code_id == "EGY", Subscription.subscription_type =="Enterprise" )).all()),
            "len_global_demo" : len(Subscription.query.filter(and_(Subscription.country_code_id == "GLB", Subscription.subscription_type =="Demo" )).all()),
            "len_global_enterprise" : len(Subscription.query.filter(and_(Subscription.country_code_id == "GLB", Subscription.subscription_type =="Enterprise" )).all()),
            "len_turkey_demo" : len(Subscription.query.filter(and_(Subscription.country_code_id == "TUR", Subscription.subscription_type =="Demo" )).all()),
            "len_turkey_enterprise" : len(Subscription.query.filter(and_(Subscription.country_code_id == "TUR", Subscription.subscription_type =="Enterprise" )).all()),
            "len_india_demo" : len(Subscription.query.filter(and_(Subscription.country_code_id == "IND", Subscription.subscription_type =="Demo" )).all()),
            "len_india_enterprise" : len(Subscription.query.filter(and_(Subscription.country_code_id == "IND", Subscription.subscription_type =="Enterprise" )).all()),
            "len_malaysia_demo" : len(Subscription.query.filter(and_(Subscription.country_code_id == "MYS", Subscription.subscription_type =="Demo" )).all()),
            "len_malaysia_enterprise" : len(Subscription.query.filter(and_(Subscription.country_code_id == "MYS", Subscription.subscription_type =="Enterprise" )).all()),
            "len_georgia_demo" : len(Subscription.query.filter(and_(Subscription.country_code_id == "GEO", Subscription.subscription_type =="Demo" )).all()),
            "len_georgia_enterprise" : len(Subscription.query.filter(and_(Subscription.country_code_id == "GEO", Subscription.subscription_type =="Enterprise" )).all()),
            }
    except Exception as e:
        print(e)
        return {}


def get_all_subscriptions_count(countries):
    try:
        with app.test_request_context():
            return {
            "subscriptions_list" : Subscription.query.filter(Subscription.country_code_id.in_(countries)).all(),
            "get_len_demo" : len(Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_type == "Demo")).all()),
            "get_len_enterprise" : len(Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_type == "Enterprise")).all()),
            "get_len_cancel" : len(Subscription.query.filter(and_(Subscription.country_code_id.in_(countries), Subscription.subscription_status == "Cancel")).all()),
            "get_len_all" : len(Subscription.query.filter(Subscription.country_code_id.in_(countries)).all())
            }
    except Exception as e:
        return {}


def formatting_subscriptions_object_return_list(subscriptions):
    try:
        all_subscriptions = []
        for data in subscriptions:
            cs_name = data.name
            cs_email = data.email
            cs_company_name = data.company_string_name
            cs_contact = data.contact
            cs_pos_no = data.stores_number
            cs_reg_code = data.business_name
            cs_sub_type = data.subscription_type
            cs_sub_status = data.db_status
            cs_creation_date = data.db_create_date.strftime("%b %d %Y"),
            cs_city = data.city
            cs_street = data.street
            cs_country = data.Country
            cs_tax_file = data.tax_file
            cs_commercial_reg = data.commercial_register
            cs_expire_db = data.expire_db.strftime("%b %d %Y"),
            cs_order_id = data.order_id
            cs_postcode = data.postcode
            cs_plan_type = data.plan_type
            cs_subscription_status = data.subscription_status
            cs_country_code = data.country_code_id
            cs_activity = data.is_active
            all_subscriptions.append({"id":data.id,
                                         "cs_name":cs_name,
                                         "cs_email": cs_email,
                                         "cs_company_name": cs_company_name,
                                         "cs_contact": cs_contact,
                                         "cs_pos_no":cs_pos_no,
                                         "cs_reg_code": cs_reg_code,
                                         "cs_sub_type": cs_sub_type,
                                         "cs_sub_status": cs_sub_status,
                                         "cs_creation_date": cs_creation_date,
                                         "cs_city": cs_city,
                                         "cs_street": cs_street,
                                         "cs_country":cs_country,
                                         "cs_tax_file": cs_tax_file,
                                         "cs_commercial_reg": cs_commercial_reg,
                                         "cs_expire_db": cs_expire_db,
                                         "cs_order_id": cs_order_id,
                                         "cs_postcode": cs_postcode,
                                         "cs_plan_type": cs_plan_type,
                                         "cs_subscription_status": cs_subscription_status,
                                         "cs_country_code": cs_country_code,
                                         "cs_activity": cs_activity,
                                     })
        return all_subscriptions
    except Exception as e:
        return []


def returned_finally_process_function(get_subscription_object,get_len_all_countries_counts,get_user_data):
    return {"all_sub":get_subscription_object['get_len_all'],
            "demo_sub":get_subscription_object['get_len_demo'],
            "enterprise_sub":get_subscription_object['get_len_enterprise'],
            "cancel_sub": get_subscription_object['get_len_cancel'],
            "data":formatting_subscriptions_object_return_list(get_subscription_object['subscriptions_list']),
            "user_name": get_user_data.user_name,
            "saudi_demo_len": get_len_all_countries_counts['len_saudi_demo'],
            "saudi_enterprise_len": get_len_all_countries_counts['len_saudi_enterprise'],
            "egypt_demo_len":get_len_all_countries_counts['len_egypt_demo'],
            "egypt_enterprise_len":get_len_all_countries_counts['len_egypt_enterprise'],
            "global_demo_len": get_len_all_countries_counts['len_global_demo'],
            "global_enterprise_len": get_len_all_countries_counts['len_global_enterprise'],
            "turkey_demo_len": get_len_all_countries_counts['len_turkey_demo'],
            "turkey_enterprise_len": get_len_all_countries_counts['len_turkey_enterprise'],
            "india_demo_len":get_len_all_countries_counts['len_india_demo'],
            "india_enterprise_len":get_len_all_countries_counts['len_india_enterprise'],
            "malaysia_demo_len": get_len_all_countries_counts['len_malaysia_demo'],
            "malaysia_enterprise_len": get_len_all_countries_counts['len_malaysia_enterprise'],
            "georgia_demo_len": get_len_all_countries_counts['len_georgia_demo'],
            "georgia_enterprise_len": get_len_all_countries_counts['len_georgia_enterprise'],
            }


@admin_panel.route('/getAllSubscription', methods=['POST'])
def getAllSubscription():
    if verify_auth_api.check_header_auth_admin() == "Auth":
        try:
            get_data = request.json
            check_auth = CHECK_TOKEN.check_token_expired_for_admin_panel(get_data['access_token'], get_data['access_session'])
            if check_auth['status'] == 'success':
                get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
                if get_user_data.activate:
                    countries = get_countries_available_for_admin_account(get_user_data)
                    get_subscription_object = get_all_subscriptions_count(countries)
                    get_len_all_countries_counts = get_subscription_type_count_for_countries()
                    return returned_finally_process_function(get_subscription_object, get_len_all_countries_counts, get_user_data)
                else:
                    return {'status': "suspended", 'msg': 'this account has been suspended by administrator'}
            else:
                return {'status': "failed", 'msg': 'invalid token'}
        except Exception as Error:
            print(Error)
    else:
        return {"status": "invalied"}


