"""
OraHub Application Entry Point
Adaptée pour développement local ET production (Render)
"""

from dotenv import load_dotenv
from app import create_app
import os
import traceback
import sys

# Charger les variables d'environnement depuis .env (développement local uniquement)
load_dotenv()

# Créer l'instance Flask
app = create_app()

if __name__ == '__main__':
    # Configuration pour différents environnements
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    # DEBUG mode: actif seulement en développement
    is_production = os.environ.get('FLASK_ENV') == 'production'
    debug_mode = not is_production and os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Messages d'information
    env_name = 'PRODUCTION' if is_production else 'DEVELOPMENT'
    print(f"\n[OraHub] Starting server in {env_name} mode", flush=True)
    print(f"[OraHub] Host: {host}:{port}", flush=True)
    print(f"[OraHub] Debug: {debug_mode}", flush=True)
    print(f"[OraHub] URL: http://127.0.0.1:{port}\n", flush=True)
    
    try:
        # En production, utilisez gunicorn: gunicorn app:app
        # En développement, utilisez: python run.py
        app.run(host=host, port=port, debug=debug_mode, use_reloader=debug_mode)
    except Exception as e:
        print('[OraHub] ❌ Server failed to start. See traceback below:\n', flush=True)
        traceback.print_exc()
        sys.exit(1)
