"""
📱 SMS & WhatsApp Broadcast Module
- Envoi de SMS et WhatsApp en masse
- Intégration Twilio, Vonage
- Segmentation de contacts
- Tracking de livraison et analytics
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from ...security import premium_required
from datetime import datetime
import os
import json
from . import sms_bp

# Try importing SMS providers
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

try:
    from vonage import Client as VonageClient
    VONAGE_AVAILABLE = True
except ImportError:
    VONAGE_AVAILABLE = False

# In-memory storage (use TinyDB in production)
SMS_CAMPAIGNS = {}
SMS_LOGS = []

def get_active_sms_provider():
    """Déterminer le provider SMS disponible"""
    if TWILIO_AVAILABLE and os.getenv('TWILIO_ACCOUNT_SID'):
        return 'twilio'
    elif VONAGE_AVAILABLE and os.getenv('VONAGE_API_KEY'):
        return 'vonage'
    else:
        return 'none'


# ═════════════════════════════════════════════════════════════════
# SMS ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@sms_bp.route('/send-sms', methods=['POST'])
@premium_required
def send_sms():
    """
    Envoyer des SMS en masse
    Body: {
        "message": "texte du SMS",
        "recipients": ["06...", "07..."],
        "campaign_name": "string",
        "schedule_time": "ISO datetime (optional)",
        "provider": "twilio|vonage" (optional)
    }
    """
    try:
        user_id = current_user.id
        data = request.json
        message = data.get('message', '')
        recipients = data.get('recipients', [])
        campaign_name = data.get('campaign_name', 'SMS Campaign')
        provider = data.get('provider') or get_active_sms_provider()
        
        if not message or not recipients:
            return jsonify({'success': False, 'error': 'Message et recipients requis'}), 400
        
        if provider == 'none':
            return jsonify({'success': False, 'error': 'Aucun provider SMS disponible'}), 500
        
        # Valider les numéros
        valid_recipients = [r for r in recipients if r and len(r) >= 10]
        if not valid_recipients:
            return jsonify({'success': False, 'error': 'Aucun numéro valide'}), 400
        
        campaign_id = f"sms_{user_id}_{int(datetime.now().timestamp())}"
        sent_count = 0
        failed_count = 0
        
        # Envoyer les SMS
        for phone in valid_recipients:
            try:
                if provider == 'twilio':
                    _send_via_twilio(phone, message)
                elif provider == 'vonage':
                    _send_via_vonage(phone, message)
                sent_count += 1
            except Exception as e:
                failed_count += 1
                print(f"[SMS] Error sending to {phone}: {str(e)}")
        
        # Enregistrer la campagne
        SMS_CAMPAIGNS[campaign_id] = {
            'id': campaign_id,
            'user_id': user_id,
            'campaign_name': campaign_name,
            'message': message,
            'total_recipients': len(valid_recipients),
            'sent': sent_count,
            'failed': failed_count,
            'created_at': datetime.now().isoformat(),
            'provider': provider,
            'status': 'completed'
        }
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'sent': sent_count,
            'failed': failed_count,
            'total': len(valid_recipients)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sms_bp.route('/send-whatsapp', methods=['POST'])
@premium_required
def send_whatsapp():
    """
    Envoyer des messages WhatsApp
    Body: {
        "message": "texte du message",
        "recipients": ["+33...", "+33..."],
        "media_url": "url (optional)",
        "campaign_name": "string"
    }
    """
    try:
        user_id = current_user.id
        data = request.json
        message = data.get('message', '')
        recipients = data.get('recipients', [])
        media_url = data.get('media_url')
        campaign_name = data.get('campaign_name', 'WhatsApp Campaign')
        
        if not message or not recipients:
            return jsonify({'success': False, 'error': 'Message et recipients requis'}), 400
        
        campaign_id = f"whatsapp_{user_id}_{int(datetime.now().timestamp())}"
        sent_count = 0
        
        # Intégration Twilio WhatsApp (method d'envoi)
        for phone in recipients:
            try:
                if TWILIO_AVAILABLE:
                    client = Client(
                        os.getenv('TWILIO_ACCOUNT_SID'),
                        os.getenv('TWILIO_AUTH_TOKEN')
                    )
                    msg = client.messages.create(
                        from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
                        to=f"whatsapp:{phone}",
                        body=message,
                        media_url=media_url if media_url else None
                    )
                    sent_count += 1
            except Exception as e:
                print(f"[WhatsApp] Error: {str(e)}")
        
        SMS_CAMPAIGNS[campaign_id] = {
            'id': campaign_id,
            'user_id': user_id,
            'campaign_name': campaign_name,
            'message': message,
            'total_recipients': len(recipients),
            'sent': sent_count,
            'created_at': datetime.now().isoformat(),
            'provider': 'twilio',
            'type': 'whatsapp',
            'status': 'completed'
        }
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'sent': sent_count,
            'total': len(recipients)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sms_bp.route('/campaigns', methods=['GET'])
@premium_required
def list_campaigns():
    """Lister les campagnes SMS/WhatsApp de l'utilisateur"""
    user_id = current_user.id
    campaigns = [c for c in SMS_CAMPAIGNS.values() if c.get('user_id') == user_id]
    return jsonify({'campaigns': sorted(campaigns, key=lambda x: x['created_at'], reverse=True)})


@sms_bp.route('/status', methods=['GET'])
@premium_required
def sms_status():
    """Vérifier l'état des providers SMS"""
    return jsonify({
        'active_provider': get_active_sms_provider(),
        'available_providers': {
            'twilio': TWILIO_AVAILABLE and bool(os.getenv('TWILIO_ACCOUNT_SID')),
            'vonage': VONAGE_AVAILABLE and bool(os.getenv('VONAGE_API_KEY'))
        }
    })


# ═════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════

def _send_via_twilio(phone, message):
    """Envoyer un SMS via Twilio"""
    client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    msg = client.messages.create(
        body=message,
        from_=os.getenv('TWILIO_PHONE_NUMBER'),
        to=phone
    )
    return msg.sid


def _send_via_vonage(phone, message):
    """Envoyer un SMS via Vonage"""
    client = VonageClient(
        api_key=os.getenv('VONAGE_API_KEY'),
        api_secret=os.getenv('VONAGE_API_SECRET')
    )
    response = client.sms.send_message({
        "to": phone,
        "from": "OraHub",
        "text": message
    })
    return response


@sms_bp.route('/', methods=['GET'])
@login_required
def sms_page():
    """Redirect to consolidated automation page"""
    from flask import redirect, url_for
    return redirect(url_for('automation.automation_page') + '#sms', code=302)
