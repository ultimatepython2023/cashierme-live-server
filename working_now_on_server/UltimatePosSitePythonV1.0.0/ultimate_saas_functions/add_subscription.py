from flask import Flask
from app import *
from flask_bcrypt import Bcrypt


def add_subscription_record(name, email, stores_number, database_fullname,
                            best_time_call, city, contact, database_create_dt,password,
                            file_taxess, commercial_register, expire_db,country, db_type,street,postcode,
                            password_bcrypt, company_string_name, created_from,company_token,amount, country_code):
    try:
        data = Subscription(name, email, stores_number, database_fullname,
                            best_time_call, city, contact, database_create_dt,password,
                            file_taxess, commercial_register, expire_db,
                            database_create_dt,
                            country, "Enterprise", street,
                            postcode,
                            password_bcrypt, company_string_name, created_from,
                            company_token, "","","","")
        db.session.add(data)
        db.session.commit()
        data.plan_type = db_type
        data.price = amount
        data.db_status = "pending"
        data.country_code_id = country_code
        db.session.commit()
        return {"status": "Success", "sub_id":str(data.id)}
    except Exception as Error:
        return {"status" :"Invalid" }
