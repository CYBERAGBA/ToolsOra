from flask import Blueprint

aiml_bp = Blueprint('aiml', __name__)

from . import routes

