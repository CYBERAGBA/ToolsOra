from flask import Blueprint, jsonify, request

api_bp = Blueprint('api', __name__)


@api_bp.route('/status')
def status():
    return jsonify({'status': 'ok', 'service': 'EduTools Hub'})


@api_bp.route('/health')
def health():
    return jsonify({'healthy': True})
