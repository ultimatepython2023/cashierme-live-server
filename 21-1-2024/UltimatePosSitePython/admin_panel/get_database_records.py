import datetime

from admin_panel.pagination_with_serve import Paginate
from admin_panel import admin_panel
from admin_panel.dashboard import get_countries_available_for_admin_account
from admin_panel import check_token_expired as CHECK_TOKEN
from admin_panel import dashboard as D
from app import *
import random


P = Paginate('Subscription')

def get_all_data_from_model_with_paginate_with_subscription(model_name,countries , start_rows, select_limit):
    try:
        all_data = db.session.query(eval(model_name)).filter(eval(model_name).country_code_id.in_(countries)).order_by(eval(model_name).id.desc()).offset(start_rows).limit(select_limit).all()
        my_list = generate_dict_and_remove_instance_state(all_data, "other")
        return my_list
    except Exception as Error:
        print(Error)
        return []

def get_all_data_from_model_with_paginate_and_filter(model_name,countries ,start_rows, select_limit,field_name, field_value):
    try:
        con_model_and_field = str(model_name+'.'+field_name)
        all_data = db.session.query(eval(model_name)).filter(and_(eval(model_name).country_code_id.in_(countries), eval(con_model_and_field) == field_value)).order_by(eval(model_name).id.desc()).offset(start_rows).limit(select_limit).all()
        my_list = generate_dict_and_remove_instance_state(all_data, "other")
        return my_list
    except Exception as Error:
        print(Error)
        return []

def get_all_data_from_model_with_paginate_and_search_with_condition(model_name,countries,start_rows, select_limit,field_name, field_value):
    try:
        con_model_and_field = str(model_name+'.'+field_name)
        all_data = db.session.query(eval(model_name)).filter(and_(eval(model_name).country_code_id.in_(countries), eval(con_model_and_field).regexp_match(field_value))).order_by(eval(model_name).id.desc()).offset(start_rows).limit(select_limit).all()
        my_list = generate_dict_and_remove_instance_state(all_data, "other")
        return my_list
    except Exception as Error:
        print(Error)
        return []



def get_all_data_from_model_with_paginate_and_between_date(model_name,countries,start_rows, select_limit,field_name, start_date, end_date):
    try:
        con_model_and_field = str(model_name+'.'+field_name)
        all_data = db.session.query(eval(model_name)).filter(and_(eval(model_name).country_code_id.in_(countries), eval(con_model_and_field).between(start_date, end_date))).order_by(eval(model_name).id.desc()).offset(start_rows).limit(select_limit).all()
        my_list = generate_dict_and_remove_instance_state(all_data, "other")
        return my_list
    except Exception as Error:
        print(Error)
        return []



def get_all_data_from_model_for_subscription(model_name,countries):
    try:
        return eval(model_name).query.filter(eval(model_name).country_code_id.in_(countries)).order_by(eval(model_name).id.desc()).all()
    except Exception as Error:
        print(Error)
        pass
        return []

def get_all_data_from_model_with_filter_with_condition(model_name, countries , field_name, field_value, ):
    con_model_and_field = str(model_name+'.'+field_name)
    try:
        all_data = eval(model_name).query.filter(and_(eval(model_name).country_code_id.in_(countries), eval(con_model_and_field) == str(field_value))).order_by(eval(model_name).id.desc()).all()
        return all_data
    except Exception as Error:
        print(Error)
        return []

def get_all_data_from_model_with_search_with_condition(model_name, countries , field_name, field_value):
    con_model_and_field = str(model_name+'.'+field_name)
    try:
        all_data = eval(model_name).query.filter(and_(eval(model_name).country_code_id.in_(countries), eval(con_model_and_field).regexp_match(field_value))).order_by(eval(model_name).id.desc()).all()
        return all_data
    except Exception as Error:
        print(Error)
        return []



def get_data_between_date_from_model_name(model_name, countries , field_name, start_date, end_date):
    con_model_and_field = str(model_name+'.'+field_name)
    try:
        all_data = eval(model_name).query.filter(and_(eval(model_name).country_code_id.in_(countries), eval(con_model_and_field).between(start_date, end_date))).order_by(eval(model_name).id.desc()).all()
        return all_data
    except Exception as Error:
        print(Error)
        return []

def generate_dict_and_remove_instance_state(get_object, type):
    my_list = []
    if type == "other":
        for  data  in get_object:
            my_list.append({'data':data.__dict__})
        for rec in my_list:
            del rec['data']['_sa_instance_state']
            try:
                if rec['data']['image_1']:
                    del rec['data']['image_1']
                if rec['data']['image_2']:
                    del rec['data']['image_2']
                if rec['data']['image_3']:
                    del rec['data']['image_3']
            except:
                pass
        return my_list




@admin_panel.route('/get_all_data_from_model_name', methods=['POST', 'GET'])
def get_all_data_from_model_name_for_subscription():
    if verify_auth_api.check_header_auth_admin() == "Auth":
        try:
            get_data = request.json
            print(get_data)
            check_auth = CHECK_TOKEN.check_token_expired_for_admin_panel(get_data['access_token'], get_data['access_session'])
            if check_auth['status'] == 'success':
                get_user_data = Users.query.filter_by(id = check_auth['user_id']).first()
                if get_user_data.activate:
                    countries = get_countries_available_for_admin_account(get_user_data)
                    model_name = get_data['model_name']
                    pagination_value = get_data['pagination_value']
                    filter_field_name = get_data['filter_field_name']
                    filter_field_value = get_data['filter_field_value']
                    search_field_name = get_data['search_field_name']
                    search_field_value = get_data['search_field_value']
                    custom_filter_date = get_data['custom_filter_date']
                    print(custom_filter_date)
                    models_ref_list = get_data['models_ref_list']
                    current_page_count = 0
                    if get_data['current_count_page']:
                        current_page_count = int(get_data['current_count_page'])
                    else:
                        current_page_count = 1
                    if pagination_value:
                        my_data_len = ""
                        if filter_field_name and filter_field_value:
                            my_data_len = get_all_data_from_model_with_filter_with_condition(model_name, countries, filter_field_name, filter_field_value)
                        elif search_field_name and search_field_value:
                            my_data_len = get_all_data_from_model_with_search_with_condition(model_name, countries, search_field_name, search_field_value)
                        elif custom_filter_date[0]['start_date'] and custom_filter_date[0]['end_date']:
                            my_data_len = get_data_between_date_from_model_name(model_name,countries,custom_filter_date[0]['field_name'], custom_filter_date[0]['start_date'],custom_filter_date[0]['end_date'] )
                            print(my_data_len)

                        else:
                            my_data_len = get_all_data_from_model_for_subscription(model_name, countries)
                        generate_pagination_object = P.get_current_rows_paginate(len(my_data_len), current_page_count, pagination_value)
                        my_data = []
                        if filter_field_name and filter_field_value:
                            my_data = get_all_data_from_model_with_paginate_and_filter(model_name, countries, int(generate_pagination_object['current_start_rows']), current_page_count,filter_field_name, filter_field_value)
                        elif search_field_name and search_field_value:
                            my_data = get_all_data_from_model_with_paginate_and_search_with_condition(model_name, countries, int(generate_pagination_object['current_start_rows']), current_page_count,search_field_name, search_field_value)
                        elif custom_filter_date[0]['start_date'] and custom_filter_date[0]['end_date'] :
                            my_data = get_all_data_from_model_with_paginate_and_between_date(model_name, countries, int(generate_pagination_object['current_start_rows']), current_page_count,custom_filter_date[0]['field_name'], custom_filter_date[0]['start_date'],custom_filter_date[0]['end_date'] )
                        else:
                            my_data = get_all_data_from_model_with_paginate_with_subscription(model_name,countries, int(generate_pagination_object['current_start_rows']), current_page_count)
                        return {
                            'status': "success",
                            'my_data': my_data,
                            "data_len": len(my_data_len),
                            "current_start_rows": generate_pagination_object['current_start_rows'],
                            "current_end_rows":  generate_pagination_object['current_end_rows'],
                            "all_pages_count":  generate_pagination_object['all_pages_count']
                        }

                    else:
                        my_data = get_all_data_from_model_for_subscription(model_name,countries)
                        mylist = []
                        my_list = []
                        for data in my_data:
                            mylist.append(data.__dict__)
                        for rec in mylist:
                            del rec['_sa_instance_state']
                            my_list.append(rec)
                        return {'status': "success", 'my_data': my_list}
            else:
                return {"status":"invalid token"}
        except Exception as error:
            print(error)
            return {"status":"invalid"}
    else:
        print("auth invalied")
        return {"status": "invalid"}