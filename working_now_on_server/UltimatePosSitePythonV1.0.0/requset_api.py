import api_keys
import requests, json
from app import *


def createDabaseFromRequestApi(dbname,
                                user_password,
                                company_name,
                                company_token,
                                company_country,
                                company_city,
                                company_address,
                                company_postcode,
                                company_commercial_record,
                                company_tax_file,
                                contact_mobile,
                                contact_email,
                                contact_name,
                                unit_count
                                ):

     try:
         request_data = {
             "dbname": str(dbname),
             "user_password": str(user_password),
             "company_name": str(company_name),
             "company_token": str(company_token),
             "company_country": str(company_country),
             "company_city": str(company_city),
             "company_address": str(company_address),
             "company_postcode": str(company_postcode),
             "company_commercial_record": str(company_commercial_record),
             "company_tax_file": str(company_tax_file),
             "contact_mobile": str(contact_mobile),
             "contact_email": str(contact_email),
             "contact_name": str(contact_name),
             "stores_number": str(unit_count),
             "best_time_call": "10pm",
         }
         print(request_data)
         response = requests.post(str(api_keys.api_url_request),
                                  data=json.dumps(request_data),
                                  headers={
                                      'api_auth_header': str(api_keys.api_auth_header),
                                      'content-type': 'application/json'}
                                  )
         print(response.content)
         get_data = json.loads(response.content)
         get_response_code = get_data["Result"]["ErrNo"]
         get_response_status = get_data["Result"]["ErrMsg"]
         if get_response_code == 0 and get_response_status == "Success":
             return {"status": "Activated", "message":"Success", "request":str(request_data)}
         else:
             return {"status": "Failed", "message":str(get_data),"request":str(request_data) }
     except Exception as Error:
         print (Error)
         return {"status": "Error", "message": str(Error),"request":str(request_data)}

