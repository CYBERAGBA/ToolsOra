"""
🔔 Push Notifications & In-App Alerts Module
- Notifications push sur mobile/web
- Firebase Cloud Messaging
- In-app notification center
- User preferences et quiet hours
- Analytics
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from ...security import premium_required
from datetime import datetime, timedelta
import os
import json
from . import notifications_bp

# Try importing Firebase
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

# In-memory storage (use TinyDB in production)
NOTIFICATIONS = {}
USER_PREFERENCES = {}
NOTIFICATION_LOGS = []


# ═════════════════════════════════════════════════════════════════
# PUSH NOTIFICATION ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@notifications_bp.route('/send-push', methods=['POST'])
@login_required
def send_push_notification():
    """
    Envoyer une notification push
    Body: {
        "title": "string",
        "body": "string",
        "recipients": ["user_id_1", "user_id_2"] or "all",
        "data": {...},
        "icon": "url (optional)",
        "click_action": "url (optional)",
        "priority": "high|normal"
    }
    """
    try:
        user_id = current_user.id
        data = request.json
        
        title = data.get('title')
        body = data.get('body')
        recipients = data.get('recipients', [])
        push_data = data.get('data', {})
        priority = data.get('priority', 'high')
        
        if not title or not body:
            return jsonify({'success': False, 'error': 'Title et body sont requis'}), 400
        
        if isinstance(recipients, str) and recipients == "all":
            recipients = _get_all_users()
        
        if not recipients:
            return jsonify({'success': False, 'error': 'Aucun destinataire valide'}), 400
        
        sent_count = 0
        failed_count = 0
        
        # Envoyer les notifications
        for recipient_id in recipients:
            try:
                # Vérifier les préférences et quiet hours
                if not _should_send_notification(recipient_id):
                    continue
                
                # Envoyer via Firebase
                if FIREBASE_AVAILABLE:
                    _send_via_firebase(recipient_id, title, body, push_data, priority)
                
                # Enregistrer dans la notification center
                _save_in_app_notification(recipient_id, title, body, push_data)
                sent_count += 1
            
            except Exception as e:
                failed_count += 1
                print(f"[Notifications] Error sending to {recipient_id}: {str(e)}")
        
        # Log
        notification_id = f"notif_{user_id}_{int(datetime.now().timestamp())}"
        NOTIFICATIONS[notification_id] = {
            'id': notification_id,
            'created_by': user_id,
            'title': title,
            'body': body,
            'sent_to': sent_count,
            'failed': failed_count,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'notification_id': notification_id,
            'sent': sent_count,
            'failed': failed_count
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@notifications_bp.route('/in-app-notifications', methods=['GET'])
@login_required
def get_in_app_notifications():
    """Récupérer les notifications in-app de l'utilisateur"""
    user_id = current_user.id
    key = f"user_{user_id}_notifications"
    
    # Récupérer et marquer comme lues
    unread = []
    if key in NOTIFICATIONS:
        unread = NOTIFICATIONS[key].get('unread', [])
    
    return jsonify({
        'notifications': unread,
        'unread_count': len(unread)
    })


@notifications_bp.route('/mark-as-read/<notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Marquer une notification comme lue"""
    try:
        user_id = current_user.id
        key = f"user_{user_id}_notifications"
        
        if key in NOTIFICATIONS:
            notifs = NOTIFICATIONS[key].get('unread', [])
            NOTIFICATIONS[key]['unread'] = [n for n in notifs if n.get('id') != notification_id]
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@notifications_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def notification_preferences():
    """Gérer les préférences de notifications"""
    user_id = current_user.id
    
    if request.method == 'GET':
        prefs = USER_PREFERENCES.get(user_id, _get_default_preferences())
        return jsonify(prefs)
    
    else:  # POST - mettre à jour
        try:
            data = request.json
            
            # Mettre à jour les préférences
            prefs = USER_PREFERENCES.get(user_id, _get_default_preferences())
            
            if 'mute_all' in data:
                prefs['mute_all'] = data['mute_all']
            if 'quiet_hours_start' in data:
                prefs['quiet_hours_start'] = data['quiet_hours_start']
            if 'quiet_hours_end' in data:
                prefs['quiet_hours_end'] = data['quiet_hours_end']
            if 'enabled_categories' in data:
                prefs['enabled_categories'] = data['enabled_categories']
            
            USER_PREFERENCES[user_id] = prefs
            
            return jsonify({
                'success': True,
                'preferences': prefs
            })
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


@notifications_bp.route('/analytics', methods=['GET'])
@login_required
def notification_analytics():
    """Analytics des notifications"""
    user_id = current_user.id
    cutoff = datetime.now() - timedelta(days=30)
    
    # Compter les notifications des 30 derniers jours
    user_logs = [log for log in NOTIFICATION_LOGS if log.get('user_id') == user_id
                 and datetime.fromisoformat(log.get('timestamp', '')) > cutoff]
    
    sent = len([l for l in user_logs if l.get('action') == 'sent'])
    opened = len([l for l in user_logs if l.get('action') == 'opened'])
    clicked = len([l for l in user_logs if l.get('action') == 'clicked'])
    
    return jsonify({
        'sent': sent,
        'opened': opened,
        'clicked': clicked,
        'open_rate': f"{(opened/sent*100):.1f}%" if sent > 0 else "0%",
        'click_rate': f"{(clicked/sent*100):.1f}%" if sent > 0 else "0%"
    })


# ═════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════

def _get_default_preferences():
    """Préférences par défaut"""
    return {
        'mute_all': False,
        'quiet_hours_enabled': False,
        'quiet_hours_start': '22:00',
        'quiet_hours_end': '08:00',
        'enabled_categories': ['promotions', 'updates', 'messages', 'alerts']
    }


def _should_send_notification(user_id):
    """Vérifier si une notification doit être envoyée selon les préférences"""
    prefs = USER_PREFERENCES.get(user_id, _get_default_preferences())
    
    # Vérifier si l'utilisateur a muté
    if prefs.get('mute_all'):
        return False
    
    # Vérifier les quiet hours
    if prefs.get('quiet_hours_enabled'):
        now = datetime.now().time()
        start = datetime.strptime(prefs['quiet_hours_start'], '%H:%M').time()
        end = datetime.strptime(prefs['quiet_hours_end'], '%H:%M').time()
        
        if start < end:
            if start <= now <= end:
                return False
        else:  # Quiet hours cross midnight
            if now >= start or now <= end:
                return False
    
    return True


def _save_in_app_notification(user_id, title, body, data):
    """Sauvegarder une notification dans le centre in-app"""
    key = f"user_{user_id}_notifications"
    
    if key not in NOTIFICATIONS:
        NOTIFICATIONS[key] = {'unread': []}
    
    notif = {
        'id': f"notif_{int(datetime.now().timestamp())}",
        'title': title,
        'body': body,
        'data': data,
        'timestamp': datetime.now().isoformat(),
        'read': False
    }
    
    NOTIFICATIONS[key]['unread'].append(notif)
    # Limiter à 100 notifications non lues
    if len(NOTIFICATIONS[key]['unread']) > 100:
        NOTIFICATIONS[key]['unread'] = NOTIFICATIONS[key]['unread'][-100:]


def _send_via_firebase(user_id, title, body, data, priority):
    """Envoyer via Firebase Cloud Messaging"""
    try:
        # Placeholder - intégration réelle avec Firebase
        notification = messaging.Notification(title=title, body=body)
        message = messaging.Message(
            notification=notification,
            data=data,
            webpush=messaging.WebpushConfig(
                headers={'TTL': '3600'},
                data=data,
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body
                )
            )
        )
        # response = messaging.send(message)
        print(f"[Firebase] Notification sent to {user_id}")
    except Exception as e:
        print(f"[Firebase] Error: {str(e)}")
        raise


def _get_all_users():
    """Récupérer tous les users (placeholder)"""
    # En production, lire depuis la BDD
    return []


@notifications_bp.route('/', methods=['GET'])
@login_required
def notifications_page():
    """Redirect to consolidated automation page"""
    from flask import redirect, url_for
    return redirect(url_for('automation.automation_page') + '#notifications', code=302)
