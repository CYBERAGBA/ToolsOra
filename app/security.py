import hmac
import secrets
from functools import wraps
from flask import request, session, redirect, url_for, abort, flash
from flask_login import current_user


def get_csrf_token() -> str:
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return token


def validate_csrf() -> bool:
    session_token = session.get('_csrf_token')
    request_token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
    if not session_token or not request_token:
        return False
    return hmac.compare_digest(session_token, request_token)


def _t(fr_text, en_text):
    """Helper for bilingual messages."""
    return en_text if session.get('lang') == 'en' else fr_text


def login_required_custom(f):
    """Decorator that requires user to be logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user or not current_user.is_authenticated:
            flash(_t('Veuillez vous connecter pour accéder à cette page.', 'Please sign in to access this page.'))
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def premium_required(f):
    """
    Decorator that requires user to be logged in AND have premium status.
    Use this to protect premium content that paying users should access.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user or not current_user.is_authenticated:
            flash(_t('Veuillez vous connecter pour accéder à cette page.', 'Please sign in to access this page.'))
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_premium() and not current_user.is_admin_user():
            flash(_t(
                'Cette fonctionnalité est réservée aux abonnés premium. Souscrivez à un plan pour y accéder.',
                'This feature is for premium subscribers only. Subscribe to a plan to access it.'
            ))
            return redirect(url_for('saas.index'))  # Redirect to subscription page
        
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator that requires user to be logged in AND be admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user or not current_user.is_authenticated:
            flash(_t('Veuillez vous connecter pour accéder à cette page.', 'Please sign in to access this page.'))
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_admin_user():
            abort(403)
        
        return f(*args, **kwargs)
    return decorated
