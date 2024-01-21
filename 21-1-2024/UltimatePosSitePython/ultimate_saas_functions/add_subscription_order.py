from flask import Flask
from app import *


def add_enterprise_record (name, email,stores_number,business_name,city,contact,password,
                           tax_file,commercial_register,street,Country,postcode,plan_type,company_string_name, country_id):
    password_bcrypt = bcrypt.generate_password_hash(password).decode("utf-8")
    get_data = Packages.query.filter(
        and_(Packages.type == plan_type, Packages.pos_no_code == stores_number,
             Packages.country_code == str(country_id))).first( )

    price = get_data.price
    try :
        add_order = Order(name,email,stores_number,business_name,city,contact,
                          password,tax_file,commercial_register,datetime.now( ),
                          street,Country,postcode,"in-progress","",price,plan_type,
                          datetime.now( )+timedelta(1),password_bcrypt,"",company_string_name
                          )
        db.session.add(add_order)
        db.session.commit( )
        return { "order_id" :add_order.id }
    except Exception as Error :
        print(Error)
        pass