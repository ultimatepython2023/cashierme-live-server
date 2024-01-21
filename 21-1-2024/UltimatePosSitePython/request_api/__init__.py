from flask import Flask , Blueprint


req_api = Blueprint("req_api", __name__)
from request_api import check_and_create_sub