"""
📅 Smart Scheduling & Conflicts Module
- Détection automatique des conflits
- Suggestion des meilleurs créneaux
- Calendrier intégré
- Invitations & RSVP
- Timezone handling
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from ...security import premium_required
from datetime import datetime, timedelta
import json
from . import scheduling_bp

# In-memory storage (use TinyDB in production)
CALENDAR_EVENTS = {}
MEETINGS = {}
MEETING_INVITATIONS = {}
BUSY_SLOTS = {}

# Try importing calendar providers
try:
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials
    from google.auth.oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GCAL_AVAILABLE = True
except ImportError:
    GCAL_AVAILABLE = False

try:
    import caldav
    CALDAV_AVAILABLE = True
except ImportError:
    CALDAV_AVAILABLE = False


# ═════════════════════════════════════════════════════════════════
# SMART SCHEDULING ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@scheduling_bp.route('/schedule-meeting', methods=['POST'])
@premium_required
def schedule_meeting():
    """
    Planifier une réunion intelligente
    Body: {
        "title": "string",
        "description": "string",
        "participants": ["user_id_1", "user_id_2"],
        "duration_minutes": 60,
        "preferred_time": "morning|afternoon|evening",
        "date_range": {"start": "ISO", "end": "ISO"},
        "auto_suggest": true,
        "timezone": "Europe/Paris"
    }
    """
    try:
        user_id = current_user.id
        data = request.json
        
        title = data.get('title')
        description = data.get('description', '')
        participants = data.get('participants', []) + [user_id]
        duration = data.get('duration_minutes', 60)
        preferred_time = data.get('preferred_time', 'morning')
        timezone = data.get('timezone', 'Europe/Paris')
        auto_suggest = data.get('auto_suggest', True)
        date_range = data.get('date_range', {
            'start': datetime.now().isoformat(),
            'end': (datetime.now() + timedelta(days=7)).isoformat()
        })
        
        if not title or not participants:
            return jsonify({'success': False, 'error': 'Title et participants requis'}), 400
        
        # Vérifier les conflits
        conflicts = _detect_conflicts(participants, date_range, duration)
        
        if not conflicts and auto_suggest:
            # Suggérer le meilleur créneau
            best_slot = _find_best_slot(participants, duration, date_range, preferred_time, timezone)
        elif conflicts:
            best_slot = None
        else:
            best_slot = datetime.fromisoformat(date_range['start'])
        
        # Créer la réunion
        meeting_id = f"meeting_{user_id}_{int(datetime.now().timestamp())}"
        MEETINGS[meeting_id] = {
            'id': meeting_id,
            'organizer': user_id,
            'title': title,
            'description': description,
            'participants': list(set(participants)),
            'scheduled_time': best_slot.isoformat() if best_slot else None,
            'duration_minutes': duration,
            'timezone': timezone,
            'status': 'pending',
            'has_conflicts': bool(conflicts),
            'conflicts': conflicts,
            'created_at': datetime.now().isoformat()
        }
        
        # Envoyer les invitations
        for participant_id in participants:
            if participant_id != user_id:
                _send_invitation(participant_id, meeting_id, title, best_slot)
        
        return jsonify({
            'success': True,
            'meeting_id': meeting_id,
            'scheduled_time': best_slot.isoformat() if best_slot else None,
            'has_conflicts': bool(conflicts),
            'conflicts': conflicts,
            'participants_invited': len([p for p in participants if p != user_id])
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@scheduling_bp.route('/find-meeting-slot', methods=['POST'])
@premium_required
def find_meeting_slot():
    """
    Trouver le meilleur créneau pour une réunion
    Body: {
        "participants": ["user_id_1", "user_id_2"],
        "duration_minutes": 60,
        "date_range": {"start": "ISO", "end": "ISO"},
        "working_hours": {"start": "09:00", "end": "18:00"},
        "timezone": "Europe/Paris",
        "number_of_suggestions": 5
    }
    """
    try:
        data = request.json
        
        participants = data.get('participants', [])
        duration = data.get('duration_minutes', 60)
        date_range = data.get('date_range')
        working_hours = data.get('working_hours', {'start': '09:00', 'end': '18:00'})
        timezone = data.get('timezone', 'Europe/Paris')
        num_suggestions = data.get('number_of_suggestions', 5)
        
        if not participants or not date_range:
            return jsonify({'success': False, 'error': 'Participants et date_range requis'}), 400
        
        # Trouver les meilleurs créneaux
        suggestions = _find_available_slots(
            participants, duration, date_range, working_hours, timezone, num_suggestions
        )
        
        # Classifier par score
        suggestions = sorted(suggestions, key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'total_suggestions': len(suggestions)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@scheduling_bp.route('/check-conflicts', methods=['POST'])
@premium_required
def check_conflicts():
    """
    Vérifier les conflits pour un créneau donné
    Body: {
        "participants": ["user_id_1", "user_id_2"],
        "start_time": "ISO",
        "duration_minutes": 60
    }
    """
    try:
        data = request.json
        participants = data.get('participants', [])
        start_time = data.get('start_time')
        duration = data.get('duration_minutes', 60)
        
        if not participants or not start_time:
            return jsonify({'success': False, 'error': 'Participants et start_time requis'}), 400
        
        conflicts = _check_time_conflicts(participants, start_time, duration)
        
        return jsonify({
            'success': True,
            'has_conflicts': bool(conflicts),
            'conflicts': conflicts
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@scheduling_bp.route('/meeting/<meeting_id>/respond/<response>', methods=['POST'])
@login_required
def respond_to_invitation(meeting_id, response):
    """
    Répondre à une invitation de réunion
    Response: accept|decline|tentative
    """
    try:
        user_id = current_user.id
        
        if response not in ['accept', 'decline', 'tentative']:
            return jsonify({'success': False, 'error': 'Response invalide'}), 400
        
        if meeting_id not in MEETINGS:
            return jsonify({'success': False, 'error': 'Meeting non trouvé'}), 404
        
        # Enregistrer la réponse
        invitation_key = f"invitation_{user_id}_{meeting_id}"
        MEETING_INVITATIONS[invitation_key] = {
            'meeting_id': meeting_id,
            'user_id': user_id,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        # Mettre à jour le statut de la réunion
        meeting = MEETINGS[meeting_id]
        if response == 'decline':
            meeting['declined_by'] = meeting.get('declined_by', []) + [user_id]
        elif response == 'accept':
            meeting['accepted_by'] = meeting.get('accepted_by', []) + [user_id]
        
        return jsonify({
            'success': True,
            'response': response,
            'meeting_id': meeting_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@scheduling_bp.route('/meetings', methods=['GET'])
@login_required
def list_meetings():
    """Lister les réunions de l'utilisateur"""
    user_id = current_user.id
    
    user_meetings = [m for m in MEETINGS.values() 
                     if user_id in m.get('participants', []) or m.get('organizer') == user_id]
    
    return jsonify({
        'meetings': sorted(user_meetings, key=lambda x: x.get('scheduled_time', ''), reverse=True),
        'total': len(user_meetings)
    })


# ═════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════

def _detect_conflicts(participants, date_range, duration_minutes):
    """Détecter les conflits de calendrier"""
    conflicts = []
    
    start = datetime.fromisoformat(date_range['start'])
    end = start + timedelta(minutes=duration_minutes)
    
    for participant_id in participants:
        # Vérifier contre les événements du calendrier
        participant_events = [e for e in CALENDAR_EVENTS.values() 
                             if e.get('organizer') == participant_id or participant_id in e.get('attendees', [])]
        
        for event in participant_events:
            event_start = datetime.fromisoformat(event['start_time'])
            event_end = datetime.fromisoformat(event['end_time'])
            
            # Vérifieray overlap
            if start < event_end and end > event_start:
                conflicts.append({
                    'participant': participant_id,
                    'event': event['title'],
                    'time': event['start_time']
                })
    
    return conflicts


def _find_best_slot(participants, duration, date_range, preferred_time, timezone):
    """Trouver le meilleur créneau pour une réunion"""
    start_date = datetime.fromisoformat(date_range['start'])
    end_date = datetime.fromisoformat(date_range['end'])
    
    # Préférences horaires
    time_preferences = {
        'morning': (8, 12),
        'afternoon': (12, 17),
        'evening': (17, 20)
    }
    
    pref_start, pref_end = time_preferences.get(preferred_time, (9, 18))
    
    # Itérer sur les jours
    current = start_date
    while current <= end_date:
        slot_start = current.replace(hour=pref_start, minute=0)
        slot_end = slot_start + timedelta(minutes=duration)
        
        # Vérifieregion conflits
        if not _check_time_conflicts(participants, slot_start.isoformat(), duration):
            return slot_start
        
        current += timedelta(days=1)
    
    # Fallback: premier créneau disponible
    return start_date.replace(hour=9, minute=0)


def _find_available_slots(participants, duration, date_range, working_hours, timezone, num_suggestions):
    """Trouver les slots disponibles"""
    suggestions = []
    
    start_date = datetime.fromisoformat(date_range['start'])
    end_date = datetime.fromisoformat(date_range['end'])
    
    work_start_hour = int(working_hours['start'].split(':')[0])
    work_end_hour = int(working_hours['end'].split(':')[0])
    
    current = start_date
    count = 0
    
    while current <= end_date and count < num_suggestions * 3:  # Buffer de recherche
        for hour in range(work_start_hour, work_end_hour):
            slot_start = current.replace(hour=hour, minute=0)
            
            conflicts = _check_time_conflicts(participants, slot_start.isoformat(), duration)
            if not conflicts:
                # Calculer un score (preference morning > afternoon > evening)
                score = 100 - (abs(hour - 10) * 10)  # 10h est idéal
                suggestions.append({
                    'start_time': slot_start.isoformat(),
                    'end_time': (slot_start + timedelta(minutes=duration)).isoformat(),
                    'score': score,
                    'day': current.strftime('%A'),
                    'available_for_all': True
                })
                count += 1
                
                if count >= num_suggestions:
                    return suggestions
        
        current += timedelta(days=1)
    
    return suggestions


def _check_time_conflicts(participants, start_time, duration_minutes):
    """Vérifier les conflits pour un créneau spécifique"""
    start = datetime.fromisoformat(start_time)
    end = start + timedelta(minutes=duration_minutes)
    
    conflicts = []
    
    for participant_id in participants:
        participant_events = [e for e in CALENDAR_EVENTS.values() 
                             if e.get('user_id') == participant_id]
        
        for event in participant_events:
            event_start = datetime.fromisoformat(event['start_time'])
            event_end = datetime.fromisoformat(event['end_time'])
            
            if start < event_end and end > event_start:
                conflicts.append({
                    'participant': participant_id,
                    'event': event.get('title', 'Unknown')
                })
    
    return conflicts


@scheduling_bp.route('/', methods=['GET'])
@login_required
def scheduling_page():
    """Redirect to consolidated automation page"""
    from flask import redirect, url_for
    return redirect(url_for('automation.automation_page') + '#scheduling', code=302)


def _send_invitation(participant_id, meeting_id, title, scheduled_time):
    """Envoyer une invitation de réunion"""
    invitation = {
        'id': f"invite_{meeting_id}_{participant_id}",
        'meeting_id': meeting_id,
        'to_user': participant_id,
        'title': title,
        'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
        'sent_at': datetime.now().isoformat(),
        'status': 'pending'
    }
    
    key = f"invitation_{participant_id}_{meeting_id}"
    MEETING_INVITATIONS[key] = invitation
    
    print(f"[Scheduling] Invitation sent to {participant_id} for {title}")
