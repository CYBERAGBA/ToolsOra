from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel  # <-- Ajout de Babel

try:
	from apscheduler.schedulers.background import BackgroundScheduler
except Exception:
	BackgroundScheduler = None


class _NoOpScheduler:
	def start(self):
		return None

	def add_job(self, *args, **kwargs):
		return None

# --- Extensions existantes ---
login_manager = LoginManager()
mail = Mail()

# Utilisation de BackgroundScheduler directement
scheduler = BackgroundScheduler() if BackgroundScheduler else _NoOpScheduler()

# Placeholder pour TinyDB (le projet utilise TinyDB dans app/models.py)
db = None

# --- Nouvelle extension Babel pour le multilingue ---
babel = Babel()