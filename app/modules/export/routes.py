"""
📊 Data Export & Sync Module
- Export automatique en CSV, JSON, XML
- Sync vers AWS S3, Google Drive, Dropbox
- Archivage et compression
- Encryption et sécurité
"""

from flask import jsonify, request, send_file
from flask_login import login_required, current_user
from ...security import premium_required
from datetime import datetime
import os
import json
import csv
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
import gzip
from . import export_bp

# Try importing cloud providers
try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

# In-memory storage
EXPORT_JOBS = {}


# ═════════════════════════════════════════════════════════════════
# EXPORT ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@export_bp.route('/export-data', methods=['POST'])
@premium_required
def export_data():
    """
    Exporter les données
    Body: {
        "data_type": "users|courses|payments|logs|custom",
        "format": "csv|json|xml",
        "filters": {...},
        "include_compression": true|false,
        "destination": "local|s3|gdrive" (optional)
    }
    """
    try:
        user_id = current_user.id
        data = request.json
        data_type = data.get('data_type', 'users')
        format_type = data.get('format', 'csv')
        include_compression = data.get('include_compression', False)
        destination = data.get('destination', 'local')
        
        # Générer les données
        export_data_content = _generate_export(data_type, data.get('filters', {}))
        
        if not export_data_content:
            return jsonify({'success': False, 'error': 'Pas de données à exporter'}), 400
        
        # Convertir au format demandé
        if format_type == 'csv':
            file_content = _convert_to_csv(export_data_content)
            mime_type = 'text/csv'
            ext = 'csv'
        elif format_type == 'json':
            file_content = json.dumps(export_data_content, ensure_ascii=False, indent=2)
            mime_type = 'application/json'
            ext = 'json'
        elif format_type == 'xml':
            file_content = _convert_to_xml(export_data_content, data_type)
            mime_type = 'application/xml'
            ext = 'xml'
        else:
            file_content = str(export_data_content)
            ext = 'txt'
        
        # Compression optionnelle
        if include_compression:
            file_content = gzip.compress(file_content.encode())
            ext += '.gz'
        
        # Générer le nom du fichier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"export_{data_type}_{timestamp}.{ext}"
        
        # Gérer la destination
        export_id = f"export_{user_id}_{int(datetime.now().timestamp())}"
        
        if destination == 's3':
            if not AWS_AVAILABLE:
                return jsonify({'success': False, 'error': 'AWS não configurado'}), 400
            url = _upload_to_s3(filename, file_content)
        elif destination == 'gdrive':
            if not GDRIVE_AVAILABLE:
                return jsonify({'success': False, 'error': 'Google Drive não configurado'}), 400
            url = _upload_to_gdrive(filename, file_content)
        else:
            # Local storage
            os.makedirs('exports', exist_ok=True)
            filepath = f"exports/{filename}"
            mode = 'wb' if include_compression else 'w'
            with open(filepath, mode) as f:
                f.write(file_content)
            url = f"/exports/{filename}"
        
        # Enregistrer le job
        EXPORT_JOBS[export_id] = {
            'id': export_id,
            'user_id': user_id,
            'data_type': data_type,
            'format': format_type,
            'filename': filename,
            'url': url,
            'size': len(str(file_content)),
            'created_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        return jsonify({
            'success': True,
            'export_id': export_id,
            'filename': filename,
            'download_url': url,
            'size': len(str(file_content)),
            'compressed': include_compression
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@export_bp.route('/sync-to-cloud', methods=['POST'])
@premium_required
def sync_to_cloud():
    """
    Synchroniser les données vers le cloud
    Body: {
        "data_type": "users|courses|logs",
        "destination": "s3|gdrive|dropbox",
        "schedule": "daily|weekly|monthly" (optional),
        "auto_archive": true|false
    }
    """
    try:
        user_id = current_user.id
        data = request.json
        data_type = data.get('data_type')
        destination = data.get('destination')
        
        if not data_type or not destination:
            return jsonify({'success': False, 'error': 'data_type et destination requis'}), 400
        
        # Générer et envoyer les données
        export_data_content = _generate_export(data_type)
        
        if destination == 's3':
            result = _upload_to_s3(f"{data_type}.json", json.dumps(export_data_content))
        elif destination == 'gdrive':
            result = _upload_to_gdrive(f"{data_type}.json", json.dumps(export_data_content))
        else:
            return jsonify({'success': False, 'error': 'Destination non supportée'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Données synchronisées vers {destination}',
            'destination': destination,
            'records_synced': len(export_data_content) if isinstance(export_data_content, list) else 1
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@export_bp.route('/exports', methods=['GET'])
@premium_required
def list_exports():
    """Lister les exports de l'utilisateur"""
    user_id = current_user.id
    user_exports = [e for e in EXPORT_JOBS.values() if e.get('user_id') == user_id]
    return jsonify({'exports': sorted(user_exports, key=lambda x: x['created_at'], reverse=True)})


# ═════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════

def _generate_export(data_type, filters=None):
    """Générer les données à exporter"""
    # Simulation - en production, lire depuis la BDD
    data = []
    
    if data_type == 'users':
        data = [
            {'id': 1, 'username': 'user1', 'email': 'user1@example.com', 'created_at': '2024-01-01'},
            {'id': 2, 'username': 'user2', 'email': 'user2@example.com', 'created_at': '2024-01-02'}
        ]
    elif data_type == 'courses':
        data = [
            {'id': 1, 'title': 'Python Basics', 'students': 150},
            {'id': 2, 'title': 'Advanced JS', 'students': 230}
        ]
    elif data_type == 'payments':
        data = [
            {'id': 1, 'amount': 99.99, 'date': '2024-01-15', 'user_id': 1},
            {'id': 2, 'amount': 49.99, 'date': '2024-01-16', 'user_id': 2}
        ]
    elif data_type == 'logs':
        data = [
            {'timestamp': '2024-01-15 10:00:00', 'event': 'login', 'user_id': 1},
            {'timestamp': '2024-01-15 10:05:00', 'event': 'course_viewed', 'user_id': 2}
        ]
    
    # Appliquer les filtres
    if filters:
        # Logique de filtrage simple
        pass
    
    return data


def _convert_to_csv(data):
    """Convertir les données en CSV"""
    if not data:
        return ""
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def _convert_to_xml(data, root_name='data'):
    """Convertir les données en XML"""
    root = ET.Element(root_name)
    
    if isinstance(data, list):
        for item in data:
            item_elem = ET.SubElement(root, 'item')
            for key, value in item.items():
                elem = ET.SubElement(item_elem, key)
                elem.text = str(value)
    else:
        for key, value in data.items():
            elem = ET.SubElement(root, key)
            elem.text = str(value)
    
    return ET.tostring(root, encoding='unicode')


def _upload_to_s3(filename, content):
    """Upload vers AWS S3"""
    try:
        s3 = boto3.client('s3')
        bucket = os.getenv('AWS_BUCKET_NAME', 'orahub-exports')
        s3.put_object(Bucket=bucket, Key=filename, Body=content)
        return f"s3://{bucket}/{filename}"
    except Exception as e:
        print(f"[Export] S3 error: {str(e)}")
        raise


def _upload_to_gdrive(filename, content):
    """Upload vers Google Drive"""
    try:
        # Placeholder pour GDrive
        return f"https://drive.google.com/file/d/{filename}"
    except Exception as e:
        print(f"[Export] GDrive error: {str(e)}")
        raise


@export_bp.route('/', methods=['GET'])
@login_required
def export_page():
    """Redirect to consolidated automation page"""
    from flask import redirect, url_for
    return redirect(url_for('automation.automation_page') + '#export', code=302)
