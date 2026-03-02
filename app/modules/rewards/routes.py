"""
🏆 Points & Rewards System Module
- Attribution automatique de points pour actions
- Conversion points → coupons/discounts
- Leaderboards
- Badges et achievements
- Paliers et tiers
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from ...security import premium_required
from datetime import datetime, timedelta
import os
import json
from . import rewards_bp

# In-memory storage (use TinyDB in production)
USER_POINTS = {}
ACHIEVEMENTS = {}
LEADERBOARD = {}
REDEMPTIONS = {}

# Configuration des points
POINTS_CONFIG = {
    'course_completed': 100,
    'quiz_passed': 50,
    'content_created': 75,
    'comment_liked': 5,
    'course_rated': 25,
    'referral': 200,
    'daily_login': 10,
    'weekly_challenge': 150
}

# Configuration des récompenses
REWARDS_CONFIG = {
    'bronze': {'min_points': 0, 'benefits': ['Basic support', '10% discount']},
    'silver': {'min_points': 1000, 'benefits': ['Priority support', '15% discount', 'Exclusive content']},
    'gold': {'min_points': 5000, 'benefits': ['VIP support', '25% discount', 'All premium content', 'Personal mentor']},
    'platinum': {'min_points': 10000, 'benefits': ['24/7 Concierge', '30% discount', 'Custom learning path']}
}


# ═════════════════════════════════════════════════════════════════
# POINTS ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@rewards_bp.route('/award-points', methods=['POST'])
@premium_required
def award_points():
    """
    Attribuer des points à un utilisateur pour une action
    Body: {
        "user_id": "int or 'current'",
        "action": "course_completed|quiz_passed|...",
        "points": 100 (optional - override config),
        "description": "string"
    }
    """
    try:
        data = request.json
        target_user_id = data.get('user_id')
        
        if target_user_id == 'current':
            target_user_id = current_user.id
        else:
            # Only admins can award points to others
            if not current_user.is_admin_user():
                target_user_id = current_user.id
        
        action = data.get('action')
        points = data.get('points') or POINTS_CONFIG.get(action, 0)
        description = data.get('description', action)
        
        if points <= 0:
            return jsonify({'success': False, 'error': 'Points doit être > 0'}), 400
        
        # Initialiser si résent
        if target_user_id not in USER_POINTS:
            USER_POINTS[target_user_id] = {
                'total': 0,
                'history': [],
                'tier': 'bronze',
                'redemptions': 0
            }
        
        # Ajouter les points
        user_data = USER_POINTS[target_user_id]
        user_data['total'] += points
        user_data['history'].append({
            'action': action,
            'points': points,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'awarded_by': current_user.id
        })
        
        # Mettre à jour le tier
        new_tier = _calculate_tier(user_data['total'])
        old_tier = user_data['tier']
        user_data['tier'] = new_tier
        
        # Vérifier les achievements
        achievements = _check_achievements(target_user_id, user_data)
        
        return jsonify({
            'success': True,
            'user_id': target_user_id,
            'points_awarded': points,
            'total_points': user_data['total'],
            'tier': new_tier,
            'tier_changed': old_tier != new_tier,
            'achievements_unlocked': achievements
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@rewards_bp.route('/user-points/<user_id>', methods=['GET'])
@login_required
def get_user_points(user_id):
    """Récupérer les points d'un utilisateur"""
    if user_id == 'current':
        user_id = current_user.id
    
    user_data = USER_POINTS.get(user_id, {
        'total': 0,
        'tier': 'bronze',
        'history': [],
        'redemptions': 0
    })
    
    return jsonify({
        'user_id': user_id,
        'total_points': user_data.get('total', 0),
        'tier': user_data.get('tier', 'bronze'),
        'recent_actions': user_data.get('history', [])[-10:],
        'benefits': REWARDS_CONFIG[user_data.get('tier', 'bronze')].get('benefits', [])
    })


@rewards_bp.route('/redeem-points', methods=['POST'])
@premium_required
def redeem_points():
    """
    Convertir les points en coupon/discount
    Body: {
        "reward_type": "coupon|discount|course_access|cash",
        "points_to_redeem": 500,
        "description": "string"
    }
    """
    try:
        user_id = current_user.id
        data = request.json
        
        reward_type = data.get('reward_type')
        points_to_redeem = data.get('points_to_redeem', 0)
        description = data.get('description', '')
        
        if points_to_redeem <= 0:
            return jsonify({'success': False, 'error': 'Points doit être > 0'}), 400
        
        user_data = USER_POINTS.get(user_id, {'total': 0})
        
        if user_data.get('total', 0) < points_to_redeem:
            return jsonify({'success': False, 'error': 'Points insuffisants'}), 400
        
        # Déduire les points
        user_data['total'] -= points_to_redeem
        
        # Créer la rédemption
        redemption_id = f"redeem_{user_id}_{int(datetime.now().timestamp())}"
        REDEMPTIONS[redemption_id] = {
            'id': redemption_id,
            'user_id': user_id,
            'reward_type': reward_type,
            'points_used': points_to_redeem,
            'description': description,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'coupon_code': _generate_coupon_code()
        }
        
        return jsonify({
            'success': True,
            'redemption_id': redemption_id,
            'points_used': points_to_redeem,
            'remaining_points': user_data.get('total', 0),
            'reward': REDEMPTIONS[redemption_id]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@rewards_bp.route('/leaderboard', methods=['GET'])
@login_required
def get_leaderboard():
    """
    Récupérer le leaderboard
    Query params:
    - period: all|monthly|weekly
    - limit: 10-100
    """
    try:
        period = request.args.get('period', 'all')
        limit = int(request.args.get('limit', 50))
        
        # Filtrer par période
        leaderboard_data = []
        for user_id, user_data in USER_POINTS.items():
            total_points = user_data.get('total', 0)
            
            # Si period != 'all', filter history
            if period != 'all':
                cutoff_days = 7 if period == 'weekly' else 30
                cutoff = datetime.now() - timedelta(days=cutoff_days)
                period_points = sum(
                    h['points'] for h in user_data.get('history', [])
                    if datetime.fromisoformat(h['timestamp']) > cutoff
                )
                display_points = period_points
            else:
                display_points = total_points
            
            leaderboard_data.append({
                'user_id': user_id,
                'points': display_points,
                'tier': user_data.get('tier', 'bronze')
            })
        
        # Trier et limiter
        leaderboard_data = sorted(leaderboard_data, key=lambda x: x['points'], reverse=True)[:limit]
        
        # Ajouter le rang
        for idx, entry in enumerate(leaderboard_data, 1):
            entry['rank'] = idx
        
        return jsonify({
            'period': period,
            'leaderboard': leaderboard_data
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@rewards_bp.route('/achievements', methods=['GET'])
@login_required
def get_achievements():
    """Récupérer les achievements de l'utilisateur"""
    user_id = current_user.id
    key = f"user_{user_id}_achievements"
    
    user_achievements = ACHIEVEMENTS.get(key, [])
    
    return jsonify({
        'achievements': user_achievements,
        'total_count': len(user_achievements),
        'progress': {
            'tasks_completed': len([a for a in user_achievements if a['type'] == 'task']),
            'milestones_reached': len([a for a in user_achievements if a['type'] == 'milestone'])
        }
    })


# ═════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════

def _calculate_tier(total_points):
    """Calculer le tier selon les points"""
    tiers = list(REWARDS_CONFIG.items())
    tiers.sort(key=lambda x: x[1]['min_points'], reverse=True)
    
    for tier_name, tier_config in tiers:
        if total_points >= tier_config['min_points']:
            return tier_name
    
    return 'bronze'


def _check_achievements(user_id, user_data):
    """Vérifier les achievements débloqués"""
    key = f"user_{user_id}_achievements"
    if key not in ACHIEVEMENTS:
        ACHIEVEMENTS[key] = []
    
    unlocked = []
    
    # Achievement: 1000 points
    if user_data['total'] >= 1000 and not any(a['id'] == 'points_1000' for a in ACHIEVEMENTS[key]):
        achievement = {
            'id': 'points_1000',
            'name': '1000 Points Club',
            'description': 'Atteindre 1000 points',
            'timestamp': datetime.now().isoformat()
        }
        ACHIEVEMENTS[key].append(achievement)
        unlocked.append(achievement)
    
    # Achievement: Silver tier
    if user_data['tier'] == 'silver' and not any(a['id'] == 'tier_silver' for a in ACHIEVEMENTS[key]):
        achievement = {
            'id': 'tier_silver',
            'name': 'Silver Member',
            'description': 'Atteindre le tier Silver',
            'timestamp': datetime.now().isoformat()
        }
        ACHIEVEMENTS[key].append(achievement)
        unlocked.append(achievement)
    
    return unlocked


def _generate_coupon_code():
    """Générer un code coupon unique"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


@rewards_bp.route('/', methods=['GET'])
@login_required
def rewards_page():
    """Redirect to consolidated automation page"""
    from flask import redirect, url_for
    return redirect(url_for('automation.automation_page') + '#rewards', code=302)
