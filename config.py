"""
Configuration Flask pour OraHub
Supporte: Développement, Test, Production
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """
    Configuration de base partagée par tous les environnements
    """
    
    # ========================================================================
    # SECRET KEY - CRITIQUE POUR SÉCURITÉ
    # ========================================================================
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # En développement local, génère une clé temporaire
        # EN PRODUCTION: TOUJOURS définir via variable d'environnement!
        SECRET_KEY = os.urandom(32).hex()
    
    # ========================================================================
    # DATABASE - TinyDB (JSON file-based)
    # ========================================================================
    DATABASE_PATH = os.environ.get('DATABASE_PATH')
    if not DATABASE_PATH:
        # Chemin par défaut: data/db.json (répertoire writable)
        DATABASE_PATH = str(BASE_DIR / 'data' / 'db.json')
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Ancienne config SQLAlchemy (conservée pour compatibilité)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{BASE_DIR / 'edutools.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ========================================================================
    # FLASK ENVIRONMENT
    # ========================================================================
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # ========================================================================
    # UPLOAD & CONTENT
    # ========================================================================
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH_MB', 16)) * 1024 * 1024
    
    # ========================================================================
    # SESSIONS & COOKIES - SÉCURITÉ
    # ========================================================================
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = os.environ.get('REMEMBER_COOKIE_SAMESITE', 'Lax')
    REMEMBER_COOKIE_SECURE = os.environ.get('REMEMBER_COOKIE_SECURE', 'False').lower() == 'true'
    
    # En production (HTTPS): activez ces paramètres via variables d'env
    # Exemple: SESSION_COOKIE_SECURE=True, REMEMBER_COOKIE_SECURE=True
    
    # ========================================================================
    # EMAIL - MAIL SERVER
    # ========================================================================
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@orahub.com')
    NOTIFICATION_FALLBACK_EMAIL = os.environ.get('NOTIFICATION_FALLBACK_EMAIL', 'admin@orahub.com')
    
    # ========================================================================
    # WHATSAPP & COMMUNICATIONS
    # ========================================================================
    WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL')
    WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN')
    WHATSAPP_TIMEOUT = int(os.environ.get('WHATSAPP_TIMEOUT', 8))
    
    # Admin WhatsApp via CallMeBot (free API)
    ADMIN_WHATSAPP_PHONE = os.environ.get('ADMIN_WHATSAPP_PHONE', '+2250768962233')
    CALLMEBOT_APIKEY = os.environ.get('CALLMEBOT_APIKEY', ' ')
    
    # ========================================================================
    # SCHEDULER
    # ========================================================================
    SCHEDULER_API_ENABLED = True
    
    # ========================================================================
    # PAYMENT PROVIDERS
    # ========================================================================
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
    PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET')
    
    # Mobile Money (Orange Money, Moov, MTN, etc.)
    MOBILE_MONEY_PROVIDER = os.environ.get('MOBILE_MONEY_PROVIDER', 'orange_money')
    MOBILE_MONEY_API_KEY = os.environ.get('MOBILE_MONEY_API_KEY')
    MOBILE_MONEY_API_SECRET = os.environ.get('MOBILE_MONEY_API_SECRET')
    
    # ========================================================================
    # LOGGING - Production
    # ========================================================================
    LOG_DIR = os.environ.get('LOG_DIR', str(BASE_DIR / 'logs'))
    os.makedirs(LOG_DIR, exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration pour développement local"""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(Config):
    """
    Configuration pour PRODUCTION (Render, AWS, etc.)
    """
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # En production: TOUJOURS utiliser HTTPS
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    REMEMBER_COOKIE_SAMESITE = 'Strict'
    
    # SECRET_KEY DOIT être défini via variable d'env (ne jamais en dur)
    if not Config.SECRET_KEY or Config.SECRET_KEY == os.urandom(32).hex():
        raise ValueError(
            "❌ ERREUR CRITIQUE: SECRET_KEY non définie ou générée à l'exécution!\n"
            "En production, définissez SECRET_KEY dans les variables d'environnement Render:\n"
            "RENDER Dashboard > Environment > Add environment variable > SECRET_KEY=<votre-clé>"
        )


class TestingConfig(Config):
    """Configuration pour tests"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Sélectionner la bonne config selon l'environnement
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}

# Config par défaut
Config = production_config = config_by_name.get(os.environ.get('FLASK_ENV', 'development'))

# Optional: full path to the LibreOffice `soffice` executable.
# On Windows this may be: C:\\Program Files\\LibreOffice\\program\\soffice.exe
LIBREOFFICE_PATH = os.environ.get('LIBREOFFICE_PATH', r'C:\Program Files\LibreOffice\program\soffice.exe')
