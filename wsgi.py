"""
WSGI Entry Point for Gunicorn
Production-ready application instance for Render deployment
"""

from run import app

if __name__ == "__main__":
    app.run()
