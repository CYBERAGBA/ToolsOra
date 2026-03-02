from . import plugins_bp
from flask import request, jsonify
from ...models import Plugin


@plugins_bp.route('/publish', methods=['POST'])
def publish_plugin():
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description', '')
    repo = data.get('repository', '')
    if not name:
        return jsonify({'error': 'name required'}), 400
    p = Plugin.create(name=name, description=description, repository=repo, published=True)
    return jsonify({'published': True, 'id': p['id']})
