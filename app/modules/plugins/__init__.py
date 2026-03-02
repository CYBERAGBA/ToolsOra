from flask import Blueprint

plugins_bp = Blueprint('plugins', __name__, template_folder='templates')

from . import routes
