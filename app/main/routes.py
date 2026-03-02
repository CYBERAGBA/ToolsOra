from flask import render_template, request, redirect, session, url_for, jsonify, abort
from flask_login import login_required, current_user
from . import main_bp
from app.models import User, Subscription, Payment
from app.security import admin_required


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/test-edutools')
def test_edutools():
    return render_template('test_edutools.html')


@main_bp.route('/test-button')
def test_button():
    return render_template('test_simple_button.html')


@main_bp.route('/set-language/<lang>')
def set_language(lang):
    supported_languages = ['fr', 'en']
    if lang in supported_languages:
        session['lang'] = lang

    next_url = request.args.get('next')
    if next_url and next_url.startswith('/'):
        return redirect(next_url)

    return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Example dashboard; modules will extend this
    return render_template('dashboard.html', user=current_user)


@main_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with subscription and payment management."""
    # Get summary data
    all_users = User.get_all()
    all_subscriptions = Subscription.get_all()
    pending_payments = Payment.list_pending_manual(limit=200)
    active_subscriptions = [s for s in all_subscriptions if s.get('active')]
    pending_subscriptions = [s for s in all_subscriptions if s.get('status') == 'pending_validation']
    
    # Calculate stats
    total_users = len(all_users)
    total_subscriptions = len(all_subscriptions)
    active_count = len(active_subscriptions)
    pending_count = len(pending_subscriptions)
    pending_payments_count = len(pending_payments)
    
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_subscriptions=total_subscriptions,
        active_subscriptions_count=active_count,
        pending_subscriptions_count=pending_count,
        pending_payments_count=pending_payments_count,
        all_users=all_users,
        pending_payments=pending_payments,
        pending_subscriptions=pending_subscriptions,
        all_subscriptions=all_subscriptions
    )
