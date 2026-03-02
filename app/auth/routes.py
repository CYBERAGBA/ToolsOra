from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlsplit
from . import auth_bp
from ..models import User, Subscription
from ..payments.services import get_plan
from ..security import validate_csrf


def _t(fr_text, en_text):
    return en_text if session.get('lang') == 'en' else fr_text


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not validate_csrf():
            flash(_t('Session expirée. Veuillez réessayer.', 'Session expired. Please try again.'))
            return redirect(url_for('auth.register'))

        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        password2 = request.form.get('password2') or ''

        if not username or not email or not password:
            flash(_t('Veuillez remplir tous les champs requis.', 'Please fill in all required fields.'))
            return redirect(url_for('auth.register'))

        if password != password2:
            flash(_t('Les mots de passe ne correspondent pas.', 'Passwords do not match.'))
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash(_t('Le mot de passe doit contenir au moins 6 caractères.', 'Password must contain at least 6 characters.'))
            return redirect(url_for('auth.register'))

        if User.get_by_email(email):
            flash(_t('Email déjà utilisé', 'Email already in use'))
            return redirect(url_for('auth.register'))

        user = User.create(username=username, email=email, password=password)
        flash(_t('Inscription réussie. Connectez-vous.', 'Registration successful. Please sign in.'))
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not validate_csrf():
            flash(_t('Session expirée. Veuillez réessayer.', 'Session expired. Please try again.'))
            return redirect(url_for('auth.login'))

        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        if not email or not password:
            flash(_t('Veuillez saisir votre email et votre mot de passe.', 'Please enter your email and password.'))
            return redirect(url_for('auth.login'))

        user = User.get_by_email(email)
        if user is None or not user.check_password(password):
            flash(_t('Identifiants invalides', 'Invalid credentials'))
            return redirect(url_for('auth.login'))

        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc:
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_t('Déconnecté', 'Logged out'))
    return redirect(url_for('main.index'))


@auth_bp.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    if not validate_csrf():
        flash(_t('Session expirée. Veuillez réessayer.', 'Session expired. Please try again.'))
        return redirect(url_for('main.dashboard'))

    plan_key = request.form.get('plan', 'pro')
    if plan_key == 'monthly':
        plan_key = 'starter'
    elif plan_key == 'yearly':
        plan_key = 'elite'
    plan = get_plan(plan_key)
    Subscription.cancel_user_active_subscriptions(current_user.id)
    Subscription.create(
        user_id=current_user.id,
        plan=plan.code,
        amount=plan.amount_fcfa,
        provider='legacy_simulation',
        active=True,
        status='active',
        duration_days=30,
        features=plan.highlights
    )
    current_user.upgrade_to_premium()
    flash(_t('Abonnement activé (mode simulation).', 'Subscription activated (simulation mode).'))
    return redirect(url_for('main.dashboard'))
