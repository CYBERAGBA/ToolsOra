# EduTools Hub

Plateforme modulaire en Python (Flask) pour l'éducation, outils SaaS, automatisation et monétisation.

Installation rapide

1. Créez un virtualenv et installez les dépendances:

```bash
python -m venv .venv
source .venv/bin/activate   # ou .venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

2. Configurer les variables d'environnement (optionnel):
- `SECRET_KEY`, `MAIL_*`, `DATABASE_URL`, `PAYPAL_CLIENT_ID`, etc.

3. Lancer l'application:

```bash
python run.py
```

Notes importantes
- Les intégrations de paiement (PayPal, Mobile Money, Wave, WhatsApp Business) sont représentées par des points d'entrée et placeholders. Pour un déploiement en production, vous devez intégrer les SDK/API officiels et gérer les callbacks sécurisés.
- Conversion de fichiers (pdf/docx/excel) nécessite des dépendances externes comme LibreOffice/pandoc/wkhtmltopdf selon la méthode choisie.
- Pour la génération de contenu avancée (NLP), vous pouvez brancher des modèles `transformers` ou des APIs externes.

Intégrations supplémentaires ajoutées

- Paiements: endpoints placeholders pour PayPal (`/payments/paypal/*`) et Mobile Money (`/payments/mobilemoney/pay`). Configurez les identifiants PayPal et endpoints réels en production et validez les webhooks.
- Notifications: wrappers pour email (`app/utils/notifications.py` utilisant `Flask-Mail`) et SMS via Twilio (`send_sms_via_twilio`). Configurez `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, et `TWILIO_FROM`.
- NLP avancé: endpoint `/modules/content/generate_article` tente d'utiliser `transformers` (ex: `distilgpt2`) si installé, sinon retourne un article template.

Variables d'environnement recommandées
- `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM`
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`
- `NOTIFICATION_FALLBACK_EMAIL` (par défaut `cyberagba6@gmail.com`)
- `WHATSAPP_API_URL`, `WHATSAPP_API_TOKEN`, `WHATSAPP_TIMEOUT`

Notifications abonnement (confirm/reject admin)
- Lorsqu'un admin confirme un paiement manuel, le système envoie automatiquement:
	- Un email à l'utilisateur
	- Un message WhatsApp au numéro payeur (si `WHATSAPP_API_URL` est configuré)
- Lorsqu'un admin rejette, le système envoie également ces 2 notifications avec le motif.
- Route admin de validation: `/payments/admin/manual`


Structure principale
- `app/` : code applicatif (blueprints, modèles, extensions)
- `templates/`, `static/` : assets front-end
- `run.py` : point d'entrée
- `config.py` : configuration

Contact et infos de paiement (à configurer):
- Mobile Money (exemple) : 0768962233
- WhatsApp Business : 0500072323
- Email: cyberagba6@gmail.com
