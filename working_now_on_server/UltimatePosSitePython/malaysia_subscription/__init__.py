from flask import Blueprint
malaysia_sub = Blueprint('malaysia_sub', __name__)

from malaysia_subscription import enterprise_subscription
from malaysia_subscription import upgrade_demo_to_enterprise
from malaysia_subscription import upgrade_monthly_to_annually
from malaysia_subscription import upgrade_point_of_sale

