from app import *

def check_token_expired_for_admin_panel(access_token, session_token):
    try:
        with app.test_request_context():
            get_access_token = access_token
            get_session_token = session_token
            check_user = Sessions.query.filter_by(access_token=get_access_token).first()
            if check_user:
                check_session = Sessions.query.filter_by(session_token=get_session_token).first()
                if check_session:
                    return {"status":"success",
                            "user_id":check_session.user_id}
                else:
                    return {"status":"invalid session"}
            else:
                return {"status": "invalid_user_authentication"}
    except Exception as error:
        print(error)
        return {"status":"Failed"}