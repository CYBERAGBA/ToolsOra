from flask import current_app
from flask_mail import Message
import requests
import urllib.parse
import threading

from app.extensions import mail


def send_email(to, subject, body, cc=None):
    """Send an email using Flask-Mail and return a delivery status dict."""
    if not to:
        return {'ok': False, 'channel': 'email', 'reason': 'missing_recipient'}

    try:
        sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        message = Message(subject=subject, recipients=[to], body=body, sender=sender)
        if cc:
            message.cc = [cc]
        mail.send(message)
        return {'ok': True, 'channel': 'email', 'recipient': to}
    except Exception as exc:
        current_app.logger.warning(f'Email not sent to {to}: {exc}')
        return {'ok': False, 'channel': 'email', 'recipient': to, 'reason': str(exc)}


def send_whatsapp_message(to, message):
    """
    Send WhatsApp message through a configurable provider endpoint.

    Required config/environment:
    - WHATSAPP_API_URL: provider endpoint
    Optional:
    - WHATSAPP_API_TOKEN: bearer token
    - WHATSAPP_TIMEOUT: request timeout in seconds
    """
    if not to:
        return {'ok': False, 'channel': 'whatsapp', 'reason': 'missing_recipient'}

    api_url = current_app.config.get('WHATSAPP_API_URL')
    api_token = current_app.config.get('WHATSAPP_API_TOKEN')
    timeout = current_app.config.get('WHATSAPP_TIMEOUT', 8)

    if not api_url:
        current_app.logger.info('WhatsApp API not configured; message skipped')
        return {'ok': False, 'channel': 'whatsapp', 'reason': 'not_configured'}

    payload = {'to': to, 'message': message}
    headers = {'Content-Type': 'application/json'}
    if api_token:
        headers['Authorization'] = f'Bearer {api_token}'

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        is_ok = 200 <= response.status_code < 300
        if not is_ok:
            current_app.logger.warning(
                f'WhatsApp send failed ({response.status_code}): {response.text[:300]}'
            )
        return {
            'ok': is_ok,
            'channel': 'whatsapp',
            'recipient': to,
            'status_code': response.status_code
        }
    except Exception as exc:
        current_app.logger.warning(f'WhatsApp not sent to {to}: {exc}')
        return {'ok': False, 'channel': 'whatsapp', 'recipient': to, 'reason': str(exc)}


def notify_admin_new_subscription(user_name, plan_code, amount, provider, transaction_ref, payer_phone):
    """
    Alert the admin on WhatsApp (via CallMeBot free API) that a new
    subscription payment is waiting for manual confirmation.
    Runs in a background thread to avoid blocking the request.
    """
    admin_phone = current_app.config.get('ADMIN_WHATSAPP_PHONE', '+2250768962233')
    apikey = current_app.config.get('CALLMEBOT_APIKEY', '')

    message = (
        f"🔔 *Nouvelle souscription ToolsOra*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 Utilisateur: {user_name}\n"
        f"📦 Plan: {plan_code.upper()}\n"
        f"💰 Montant: ${amount} USD\n"
        f"📱 Via: {provider.replace('_', ' ').title()}\n"
        f"🔖 Ref: {transaction_ref}\n"
        f"📞 Tel payeur: {payer_phone}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Connectez-vous pour valider ce paiement."
    )

    # --- Method 1: CallMeBot free API (preferred) ---
    if apikey:
        encoded_msg = urllib.parse.quote_plus(message)
        url = (
            f"https://api.callmebot.com/whatsapp.php"
            f"?phone={urllib.parse.quote_plus(admin_phone)}"
            f"&text={encoded_msg}"
            f"&apikey={apikey}"
        )

        def _send():
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    current_app.logger.info(f'Admin WhatsApp alert sent (CallMeBot) for ref {transaction_ref}')
                else:
                    current_app.logger.warning(
                        f'CallMeBot returned {resp.status_code}: {resp.text[:200]}'
                    )
            except Exception as exc:
                current_app.logger.warning(f'CallMeBot WhatsApp failed: {exc}')

        # Use app context in thread
        app = current_app._get_current_object()
        def _threaded_send():
            with app.app_context():
                _send()
        threading.Thread(target=_threaded_send, daemon=True).start()
        return {'ok': True, 'channel': 'whatsapp_callmebot', 'recipient': admin_phone}

    # --- Method 2: Generic WhatsApp API (if configured) ---
    api_url = current_app.config.get('WHATSAPP_API_URL')
    if api_url:
        return send_whatsapp_message(admin_phone, message)

    # --- Fallback: log only ---
    current_app.logger.info(
        f'[ADMIN ALERT] New subscription pending validation:\n{message}'
    )
    return {'ok': False, 'channel': 'none', 'reason': 'no_whatsapp_api_configured'}


def send_subscription_status_notification(user, payment, status, note=''):
    """Notify user by email and WhatsApp when admin confirms or rejects manual payment."""
    plan = (payment or {}).get('plan', 'pro').upper()
    amount = int((payment or {}).get('amount', 0))
    tx_ref = (payment or {}).get('transaction_ref', '')
    merchant_phone = (payment or {}).get('merchant_phone', '+225 0768962233')

    if status == 'confirmed':
        subject = '✅ Abonnement activé - ToolsOra'
        body = (
            f"Bonjour {user.username},\n\n"
            f"Votre paiement ({tx_ref}) a été confirmé.\n"
            f"Plan: {plan}\n"
            f"Montant: ${amount} USD\n"
            "Votre abonnement est maintenant actif.\n\n"
            "Merci pour votre confiance,\n"
            "Équipe ToolsOra"
        )
        whatsapp_text = (
            f"ToolsOra ✅ Paiement confirmé ({tx_ref}). "
            f"Plan {plan} actif. Merci !"
        )
    else:
        subject = '❌ Paiement non validé - ToolsOra'
        body = (
            f"Bonjour {user.username},\n\n"
            f"Votre paiement ({tx_ref}) n’a pas pu être validé pour le moment.\n"
            f"Plan: {plan} - ${amount} USD\n"
            f"Motif: {note or 'Veuillez vérifier la référence puis réessayer.'}\n"
            f"Numéro marchand: {merchant_phone}\n\n"
            "Vous pouvez soumettre une nouvelle référence depuis votre espace SaaS.\n"
            "Équipe ToolsOra"
        )
        whatsapp_text = (
            f"ToolsOra ❌ Paiement non validé ({tx_ref}). "
            f"Motif: {note or 'Vérifiez la référence et réessayez.'}"
        )

    fallback_email = current_app.config.get('NOTIFICATION_FALLBACK_EMAIL')
    email_result = send_email(user.email, subject, body, cc=fallback_email)
    whatsapp_result = send_whatsapp_message((payment or {}).get('payer_phone'), whatsapp_text)

    return {
        'email': email_result,
        'whatsapp': whatsapp_result,
        'status': status
    }
