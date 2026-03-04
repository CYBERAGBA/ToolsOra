# app/__init__.py
import inspect
from flask import Flask, request, session, Response, flash, redirect, url_for
from .extensions import db, login_manager, mail, scheduler, babel
from .security import get_csrf_token
from config import Config
from pathlib import Path


if 'partitioned' not in inspect.signature(Response.set_cookie).parameters:
    _original_set_cookie = Response.set_cookie

    def _set_cookie_compat(self, *args, partitioned=None, **kwargs):
        return _original_set_cookie(self, *args, **kwargs)

    Response.set_cookie = _set_cookie_compat


def create_app(config_class=Config):
    """
    Crée et configure l'application Flask avec toutes les extensions et blueprints.
    """
    # Assure que Flask utilise les dossiers statiques et templates à la racine du projet
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        static_folder=str(project_root / 'static'),
        template_folder=str(project_root / 'templates')
    )
    app.config.from_object(config_class)
    
    # Définir la fonction get_locale dans le contexte de l'app
    def get_locale():
        """
        Détecte la langue active pour Flask-Babel >=4.0
        1. Vérifie le paramètre GET ?lang=XX
        2. Sinon, utilise la meilleure correspondance du navigateur
        """
        supported_languages = ['fr', 'en']
        lang = request.args.get('lang')
        if lang in supported_languages:
            session['lang'] = lang
            return lang

        session_lang = session.get('lang')
        if session_lang in supported_languages:
            return session_lang

        return request.accept_languages.best_match(supported_languages) or 'fr'

    # --- Initialisation des extensions ---
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = None

    @login_manager.unauthorized_handler
    def unauthorized_handler():
        message = 'Please sign in to access this page.' if session.get('lang') == 'en' else 'Veuillez vous connecter pour accéder à cette page.'
        flash(message)
        return redirect(url_for('auth.login', next=request.path))
    mail.init_app(app)
    
    # Babel configuration for Flask-Babel 4.0+
    babel.init_app(app, locale_selector=get_locale)

    # Démarrage du scheduler (BackgroundScheduler)
    try:
        scheduler.start()
    except Exception:
        pass  # Ignore si le scheduler est déjà en cours

    # --- Enregistrement des Blueprints ---
    from .auth import auth_bp
    from .main import main_bp
    from .api import api_bp
    from .modules.education import education_bp
    from .modules.saas import saas_bp
    from .modules.automation import automation_bp
    from .modules.aiml import aiml_bp
    from .modules.sms import sms_bp
    from .modules.export import export_bp
    from .modules.notifications import notifications_bp
    from .modules.rewards import rewards_bp
    from .modules.scheduling import scheduling_bp
    from .payments import payments_bp
    from .technologie import technologie_bp
    from .business import business_bp
    from .creativity import creativity_bp

    # Register Core Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register Module Blueprints
    app.register_blueprint(education_bp, url_prefix='/modules/education')
    app.register_blueprint(saas_bp, url_prefix='/modules/saas')
    app.register_blueprint(automation_bp, url_prefix='/modules/automation')
    app.register_blueprint(technologie_bp, url_prefix='/modules/technologie')
    app.register_blueprint(business_bp, url_prefix='/modules/business')
    app.register_blueprint(creativity_bp, url_prefix='/modules/creativity')
    
    # Register NEW Automation & Enhanced Modules
    app.register_blueprint(aiml_bp, url_prefix='/modules/aiml')
    app.register_blueprint(sms_bp, url_prefix='/modules/sms')
    app.register_blueprint(export_bp, url_prefix='/modules/export')
    app.register_blueprint(notifications_bp, url_prefix='/modules/notifications')
    app.register_blueprint(rewards_bp, url_prefix='/modules/rewards')
    app.register_blueprint(scheduling_bp, url_prefix='/modules/scheduling')
    
    # Register Payment Blueprint
    app.register_blueprint(payments_bp, url_prefix='/payments')
    

    @app.context_processor
    def inject_locale_context():
        active_lang = get_locale()
        return {
            'current_lang': active_lang,
            'is_en': active_lang == 'en',
            'csrf_token': get_csrf_token
        }

    return app