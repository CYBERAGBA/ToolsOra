from flask import Blueprint

content_bp = Blueprint('content', __name__, template_folder='templates')

from . import routes
