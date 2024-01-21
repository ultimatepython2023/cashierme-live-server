from datetime import datetime

def check_account_status(account_status, expire_date) :
    try:
        if account_status is None and expire_date > datetime.now() :
            return True
        elif account_status is None and expire_date < datetime.now() :
            return True
        elif account_status == "Canceled" and expire_date > datetime.now() :
            return True
        elif account_status == "Canceled" and expire_date < datetime.now() :
            return False
        elif account_status == "Delete" and expire_date > datetime.now() :
            return True
        elif account_status == "Delete" and expire_date < datetime.now() :
            return False
        else:
            return False
    except Exception as e :
        return False

def check_account_status_for_company_api(account_status, expire_date ) :
    try:
        if account_status is None and expire_date > datetime.now() :
            return True
        elif account_status is None  and expire_date < datetime.now() :
            return True
        elif account_status == "Canceled" and expire_date > datetime.now() :
            return True
        elif account_status == "Canceled" and expire_date < datetime.now() :
            return False
        elif account_status == "Delete":
            return False
        else:
            return False
    except Exception as e :
        return False


