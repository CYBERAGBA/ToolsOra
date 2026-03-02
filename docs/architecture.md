**Architecture**

- Noyau central (Flask app factory) : gère la configuration, extensions, et l'enregistrement des modules.
- Modules indépendants : chaque module est un blueprint (education, saas, automation, content, plugins).
- Base de données : SQLite via SQLAlchemy (modèles dans `app/models.py`).
- Auth : gestion basique d'inscription/connexion avec `Flask-Login`.
- Tâches planifiées : `APScheduler` pour cron jobs et automatisation.
- API interne : blueprint `/api` pour endpoints internes et états.

- Paiements: le module `app/payments` contient des endpoints placeholders pour PayPal et Mobile Money. En production, remplacer par intégration SDK/API et validation webhook.
- Notifications: utilitaires dans `app/utils/notifications.py` pour emails et SMS (Twilio).
- NLP: `app/modules/content` supporte désormais `transformers` pour génération automatique si installé; sinon fallback.

Extensions principales
- `SQLAlchemy` : ORM
- `Flask-Login` : sessions utilisateurs
- `Flask-Mail` : notifications par email
- `APScheduler` : jobs planifiés

Déploiement
- Pour la production, utiliser un WSGI server (gunicorn/uwsgi) + reverse-proxy (nginx).
- Configurer variables d'environnement pour secrets et services externes.

Ajout de nouveaux modules
1. Créer un sous-dossier `app/modules/mon_module`.
2. Définir un `Blueprint` et des routes/rest API.
3. Enregistrer le blueprint dans `app/__init__.py`.
4. Documenter l'API du module.
