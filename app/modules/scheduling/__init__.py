from flask import Blueprint

scheduling_bp = Blueprint('scheduling', __name__)

from . import routes

