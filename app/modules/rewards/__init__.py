from flask import Blueprint

rewards_bp = Blueprint('rewards', __name__)

from . import routes

