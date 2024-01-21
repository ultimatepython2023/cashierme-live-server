from flask import Blueprint

sqsRoute = Blueprint('sqsRoute', __name__)
from sqs_system import sqs_requests_receive
