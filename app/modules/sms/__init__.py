from flask import Blueprint

sms_bp = Blueprint('sms', __name__)

from . import routes

