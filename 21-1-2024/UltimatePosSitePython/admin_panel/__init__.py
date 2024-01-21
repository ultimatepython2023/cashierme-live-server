from flask import Flask, Blueprint
admin_panel = Blueprint(__name__, "admin_panel")
from . import dashboard
from . import check_token_expired
from . import get_database_records