from . import payments_bp
from flask import request, jsonify, current_app, url_for, render_template, redirect, flash, session
from flask_login import login_required, current_user
try:
    import requests
except Exception:
    requests = None
import os

from app.models import Payment, Subscription, User
from app.payments.services import MERCHANT_PHONE, get_plan_rows
from app.utils.notifications import send_subscription_status_notification
from app.security import validate_csrf


def _t(fr_text, en_text):
    return en_text if session.get('lang') == 'en' else fr_text


def _require_admin():
    if not current_user.is_authenticated:
        return False
    return current_user.is_admin_user()


@payments_bp.route('/paypal/create', methods=['POST'])
def paypal_create():
    """
    Create a PayPal payment (placeholder). In production, use PayPal SDK or OAuth2 flows,
    store orders and verify webhooks.
    """
    data = request.get_json() or {}
    amount = data.get('amount', 1.0)
    currency = data.get('currency', 'USD')

    # Placeholder: return a simulated approval URL
    approval_url = url_for('payments.paypal_execute', _external=True) + '?token=simulated'
    return jsonify({'created': True, 'approval_url': approval_url, 'amount': amount, 'currency': currency})


@payments_bp.route('/paypal/execute', methods=['GET', 'POST'])
def paypal_execute():
    # In production validate and capture the payment with PayPal API
    token = request.args.get('token') or request.form.get('token')
    if not token:
        return jsonify({'error': 'missing token'}), 400
    # Simulate success
    return jsonify({'executed': True, 'token': token})


@payments_bp.route('/mobilemoney/pay', methods=['POST'])
def mobile_money_pay():
    """
    Placeholder endpoint for Mobile Money payments (Wave / local provider).
    Use provider SDK or API in production and secure callbacks/webhooks.
    """
    data = request.get_json() or {}
    amount = data.get('amount')
    phone = data.get('phone') or os.environ.get('MM_DEFAULT_PHONE')
    provider = data.get('provider', 'mobilemoney')
    # For demo, echo back the request
    return jsonify({'initiated': True, 'provider': provider, 'phone': phone, 'amount': amount})


@payments_bp.route('/manual/instructions', methods=['GET'])
def manual_instructions():
    return jsonify(
        {
            'merchant_phone': MERCHANT_PHONE,
            'channels': ['orange_money', 'wave'],
            'plans': get_plan_rows(),
            'next_step': 'Soumettre la référence de transaction pour validation admin.'
        }
    )


@payments_bp.route('/admin/manual', methods=['GET'])
@login_required
def admin_manual_dashboard():
    if not _require_admin():
        return jsonify({'error': 'forbidden'}), 403
    pending_payments = Payment.list_pending_manual(limit=200)
    return render_template('admin_payments.html', pending_payments=pending_payments)


@payments_bp.route('/admin/manual/<int:payment_id>/confirm', methods=['POST'])
@login_required
def admin_confirm_manual_payment(payment_id):
    if not _require_admin():
        return jsonify({'error': 'forbidden'}), 403
    if not validate_csrf():
        flash(_t('Session expirée. Veuillez réessayer.', 'Session expired. Please try again.'))
        return redirect(url_for('payments.admin_manual_dashboard'))

    note = request.form.get('note', '').strip()
    payment = Payment.confirm_manual(payment_id, current_user.id, note)
    if not payment:
        flash(_t('Paiement introuvable.', 'Payment not found.'))
        return redirect(url_for('payments.admin_manual_dashboard'))

    user = User.get_by_id(payment['user_id'])
    subscription = Subscription.get_by_payment_id(payment_id)
    if subscription:
        Subscription.cancel_user_active_subscriptions(subscription['user_id'])
        Subscription.activate(subscription['id'])
        if user:
            user.upgrade_to_premium()

    if user:
        notify_result = send_subscription_status_notification(
            user=user,
            payment=payment,
            status='confirmed',
            note=note
        )
        current_app.logger.info(f'Confirmation notifications: {notify_result}')

    flash(_t('Paiement confirmé. Abonnement activé automatiquement.', 'Payment confirmed. Subscription activated automatically.'))
    return redirect(url_for('payments.admin_manual_dashboard'))


@payments_bp.route('/admin/manual/<int:payment_id>/reject', methods=['POST'])
@login_required
def admin_reject_manual_payment(payment_id):
    if not _require_admin():
        return jsonify({'error': 'forbidden'}), 403
    if not validate_csrf():
        flash(_t('Session expirée. Veuillez réessayer.', 'Session expired. Please try again.'))
        return redirect(url_for('payments.admin_manual_dashboard'))

    note = request.form.get('note', '').strip()
    payment = Payment.reject_manual(payment_id, current_user.id, note)
    if not payment:
        flash(_t('Paiement introuvable.', 'Payment not found.'))
        return redirect(url_for('payments.admin_manual_dashboard'))

    user = User.get_by_id(payment['user_id'])
    subscription = Subscription.mark_rejected_by_payment(payment_id)
    if user:
        notify_result = send_subscription_status_notification(
            user=user,
            payment=payment,
            status='rejected',
            note=note
        )
        current_app.logger.info(f'Rejection notifications: {notify_result}')

    flash(_t('Paiement rejeté. L’abonnement reste inactif.', 'Payment rejected. Subscription remains inactive.'))
    return redirect(url_for('payments.admin_manual_dashboard'))


@payments_bp.route('/webhook/<provider>', methods=['POST'])
def payment_webhook(provider):
    # Generic webhook receiver for payment providers. Validate signatures in production.
    expected_token = current_app.config.get('WHATSAPP_API_TOKEN')
    if expected_token:
        received_token = request.headers.get('X-Webhook-Token') or request.args.get('token')
        if received_token != expected_token:
            return jsonify({'error': 'unauthorized webhook'}), 401

    payload = request.get_json() or {}
    # Log payload for manual verification in this scaffold
    current_app.logger.info(f"Received webhook from {provider}: {payload}")
    return jsonify({'received': True, 'provider': provider})
