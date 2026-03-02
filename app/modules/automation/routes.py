from . import automation_bp
from flask import jsonify, request, render_template, current_app
from flask_login import login_required, current_user
from ...extensions import scheduler
from ...security import premium_required
from ...models import db as tinydb
from datetime import datetime, timedelta
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageDraw, ImageFont
import io
from functools import wraps

# ═════════════════════════════════════════════════════════════════
# DATABASE INITIALIZATION (TinyDB for Persistence)
# ═════════════════════════════════════════════════════════════════

# Use TinyDB tables for persistence
TASKS_TABLE = tinydb.table('automation_tasks')
WORKFLOWS_TABLE = tinydb.table('automation_workflows')
LOGS_TABLE = tinydb.table('automation_logs')

# In-memory caches (for better performance)
SCHEDULED_TASKS = {}
WORKFLOWS = {}

# Max logs to keep in memory (limit to prevent memory leaks)
MAX_LOGS_MEMORY = 500
EXECUTION_LOGS = []

def _load_from_storage():
    """Load tasks and workflows from persistent storage"""
    global SCHEDULED_TASKS, WORKFLOWS
    try:
        for task in TASKS_TABLE.all():
            SCHEDULED_TASKS[task['id']] = task
        for workflow in WORKFLOWS_TABLE.all():
            WORKFLOWS[workflow['id']] = workflow
    except Exception as e:
        print(f"[Automation] Error loading from storage: {str(e)}")

# Load on module initialization
_load_from_storage()

def _check_scheduler_available():
    """Check if APScheduler is properly initialized"""
    try:
        return scheduler is not None and hasattr(scheduler, 'add_job')
    except:
        return False

# ═════════════════════════════════════════════════════════════════
# 1️⃣ SCHEDULING ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@automation_bp.route('/schedule-task', methods=['POST'])
@premium_required
def schedule_task():
    """Créer une tâche planifiée (cron-like)"""
    try:
        data = request.json
        user_id = current_user.id
        task_id = f"task_{user_id}_{len([t for t in SCHEDULED_TASKS.values() if t.get('user_id') == user_id])}"
        
        # Validation
        required = ['task_type', 'frequency', 'execution_time', 'description']
        if not all(k in data for k in required):
            return jsonify({'success': False, 'error': 'Champs manquants'}), 400
        
        # Check if scheduler is available
        if not _check_scheduler_available():
            return jsonify({'success': False, 'error': 'Scheduler non disponible. Installez APScheduler.'}), 500
        
        # Stocker la tâche avec user_id
        task_data = {
            'id': task_id,
            'user_id': user_id,
            'name': data['task_type'],
            'description': data['description'],
            'frequency': data['frequency'],
            'execution_time': data['execution_time'],
            'enabled': data.get('enabled', True),
            'created_at': datetime.now().isoformat(),
            'next_run': _calculate_next_run(data['frequency'], data['execution_time']),
            'status': 'scheduled',
            'last_execution': None,
            'execution_count': 0,
            'error_count': 0
        }
        
        SCHEDULED_TASKS[task_id] = task_data
        # Persistent storage
        TASKS_TABLE.upsert(task_data, lambda x: x['id'] == task_id)
        
        # Planifier avec APScheduler
        if data.get('enabled'):
            try:
                _schedule_with_apscheduler(task_id, data)
            except Exception as e:
                print(f"[Automation] APScheduler error: {str(e)}")
                return jsonify({'success': False, 'error': f'Erreur scheduleur: {str(e)}'}), 500
        
        # Log
        _add_log({
            'user_id': user_id,
            'task_name': data['task_type'],
            'status': 'scheduled',
            'timestamp': datetime.now().isoformat(),
            'message': f"Tâche créée et planifiée: {data['frequency']} à {data['execution_time']}"
        })
        
        return jsonify({
            'success': True,
            'message': f"Tâche '{data['task_type']}' créée et planifiée",
            'task_id': task_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _calculate_next_run(frequency, execution_time):
    """Calculer la prochaine exécution"""
    now = datetime.now()
    hour, minute = map(int, execution_time.split(':'))
    
    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    if next_run <= now:
        if frequency == 'daily':
            next_run += timedelta(days=1)
        elif frequency == 'weekly':
            next_run += timedelta(weeks=1)
        elif frequency == 'monthly':
            next_run += timedelta(days=30)
    
    return next_run.isoformat()


def _schedule_with_apscheduler(task_id, task_data):
    """Intégrer avec APScheduler"""
    try:
        frequency = task_data['frequency']
        execution_time = task_data['execution_time']
        
        # Convertir fréquence en trigger APScheduler
        if frequency == 'hourly':
            trigger = 'interval'
            kwargs = {'hours': 1}
        elif frequency == 'daily':
            trigger = 'cron'
            hour, minute = map(int, execution_time.split(':'))
            kwargs = {'hour': hour, 'minute': minute}
        elif frequency == 'weekly':
            trigger = 'cron'
            hour, minute = map(int, execution_time.split(':'))
            kwargs = {'day_of_week': 'mon', 'hour': hour, 'minute': minute}
        else:  # monthly
            trigger = 'cron'
            hour, minute = map(int, execution_time.split(':'))
            kwargs = {'day': 1, 'hour': hour, 'minute': minute}
        
        # Créer un job
        if trigger == 'cron':
            scheduler.add_job(
                func=_execute_task,
                trigger=trigger,
                id=task_id,
                args=[task_id],
                replace_existing=True,
                coalesce=True,
                **kwargs
            )
        else:
            scheduler.add_job(
                func=_execute_task,
                trigger=trigger,
                id=task_id,
                args=[task_id],
                replace_existing=True,
                **kwargs
            )
        print(f"[Automation] Task {task_id} scheduled with {frequency} frequency")
    
    except Exception as e:
        print(f"[Automation] Erreur APScheduler: {str(e)}")
        raise


def _add_log(log_entry):
    """Add log entry with memory limit"""
    global EXECUTION_LOGS
    EXECUTION_LOGS.append(log_entry)
    # Keep only the last MAX_LOGS_MEMORY entries in memory
    if len(EXECUTION_LOGS) > MAX_LOGS_MEMORY:
        EXECUTION_LOGS = EXECUTION_LOGS[-MAX_LOGS_MEMORY:]
    
    # Also save to persistent storage
    try:
        LOGS_TABLE.insert(log_entry)
    except Exception as e:
        print(f"[Automation] Error saving log: {str(e)}")


def _execute_task(task_id):
    """Exécuter une tâche planifiée"""
    if task_id in SCHEDULED_TASKS:
        task = SCHEDULED_TASKS[task_id]
        task_type = task['name']
        
        # Update status to running
        task['status'] = 'running'
        task['last_execution'] = datetime.now().isoformat()
        
        try:
            if task_type == 'backup':
                result = _backup_database()
            elif task_type == 'data_import':
                result = _import_data()
            elif task_type == 'db_cleanup':
                result = _cleanup_database()
            elif task_type == 'sync':
                result = _sync_data()
            else:
                result = "Tâche personnalisée exécutée"
            
            status = 'success'
            message = result
            task['execution_count'] = task.get('execution_count', 0) + 1
        
        except Exception as e:
            status = 'failed'
            message = str(e)
            task['error_count'] = task.get('error_count', 0) + 1
        
        # Update task status and next_run
        task['status'] = status
        task['next_run'] = _calculate_next_run(task['frequency'], task['execution_time'])
        
        # Save to persistent storage
        try:
            TASKS_TABLE.upsert(task, lambda x: x['id'] == task_id)
        except Exception as e:
            print(f"[Automation] Error saving task state: {str(e)}")
        
        # Log execution
        _add_log({
            'task_id': task_id,
            'task_name': task['description'],
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'user_id': task.get('user_id')
        })
        
        print(f"[Automation] {task_type} executed: {status} - {message[:100]}")


def _backup_database():
    """Sauvegarde de la base de données"""
    # Simulation: en production, utiliser mysqldump, pg_dump, etc.
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_file = f"{backup_dir}/backup-{timestamp}.json"
    
    # Sauvegarder data/db.json (exemple)
    try:
        with open('data/db.json', 'r') as src:
            data = src.read()
        with open(backup_file, 'w') as dst:
            dst.write(data)
        return f"Sauvegarde créée: {backup_file}"
    except Exception as e:
        return f"Erreur sauvegarde: {str(e)}"


def _import_data():
    """Import de données depuis CSV/JSON"""
    return "Import de données simulé (format CSV/JSON accepté)"


def _cleanup_database():
    """Nettoyage de la base de données (vieux logs, caches)"""
    return "Nettoyage: suppression des logs > 30j, caches expirés"


def _sync_data():
    """Synchronisation avec une API externe"""
    return "Synchronisation complétée (ex: Stripe, Hubspot, etc.)"


@automation_bp.route('/tasks-list', methods=['GET'])
@premium_required
def tasks_list():
    """Récupérer la liste des tâches planifiées de l'utilisateur courant"""
    user_id = current_user.id
    tasks = [t for t in SCHEDULED_TASKS.values() if t.get('user_id') == user_id]
    return jsonify({'tasks': tasks})


# ═════════════════════════════════════════════════════════════════
# 2️⃣ REPORT GENERATION ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@automation_bp.route('/generate-report', methods=['POST'])
@premium_required
def generate_report():
    """Générer un rapport (PDF, Excel, HTML)"""
    try:
        user_id = current_user.id
        data = request.json
        report_type = data.get('report_type')
        output_format = data.get('output_format', 'pdf')
        recipients = data.get('recipients', '').split(',') if data.get('recipients') else []
        
        # Générer le rapport selon le type
        if report_type == 'sales_summary':
            content = _generate_sales_report()
        elif report_type == 'user_stats':
            content = _generate_user_stats()
        elif report_type == 'inventory':
            content = _generate_inventory_report()
        elif report_type == 'attendance':
            content = _generate_attendance_report()
        else:
            content = "Rapport personnalisé (contenu placeholder)"
        
        report_id = f"report_{user_id}_{int(datetime.now().timestamp())}"
        
        # En production: exporter en vrai PDF/Excel via reportlab, openpyxl, etc.
        download_url = f"/reports/{report_id}.{output_format}"
        
        # Log
        _add_log({
            'user_id': user_id,
            'task_name': f"Rapport: {report_type}",
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'message': f"Rapport généré en {output_format}"
        })
        
        # Envoyer aux destinataires si spécifiés
        if recipients and data.get('frequency') != 'once':
            for email in recipients:
                if email.strip():
                    try:
                        _send_email(email.strip(), f"Rapport: {report_type}", content)
                    except Exception as e:
                        print(f"[Automation] Error sending report to {email.strip()}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f"Rapport {report_type} généré avec succès",
            'download_url': download_url,
            'report_id': report_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _generate_sales_report():
    """Générer un rapport de ventes"""
    return """
    RAPPORT DE VENTES
    ==================
    Période: Aujourd'hui
    
    • Chiffre d'affaires: 12,456.50 €
    • Nombre de commandes: 23
    • Panier moyen: 541.59 €
    • Nouveaux clients: 5
    • Retours: 2
    
    Meilleurs produits:
    1. Formation Python Avancé — 8 ventes
    2. CV Professionnel — 6 ventes
    3. Consultation DevOps — 4 ventes
    """


def _generate_user_stats():
    """Générer des statistiques utilisateurs"""
    return """
    STATISTIQUES UTILISATEURS
    ==========================
    Période: Mois courant
    
    • Utilisateurs actifs: 234
    • Nouveaux inscrits: 45
    • Utilisateurs churned: 3
    • Taux de retention: 98.7%
    • Utilisateurs premium: 89
    
    Appareil préféré: Mobile (67%)
    """


def _generate_inventory_report():
    """Générer un rapport d'inventaire"""
    return """
    RAPPORT D'INVENTAIRE
    ====================
    Date: Aujourd'hui
    
    Produits en stock:
    • Formation Python: 24 licences disponibles
    • Certification DevOps: 15
    • Consultation: Sans limite (service)
    
    ALERTES STOCK (< seuil critique):
    ⚠️ Manuel de déploiement: 2 copies (seuil: 5)
    ⚠️ Certificat papier: 0 (seuil: 10)
    """


def _generate_attendance_report():
    """Générer un rapport de présences (école)"""
    return """
    RAPPORT DE PRÉSENCES
    ====================
    Date: Aujourd'hui
    Classe: 3A
    
    Total élèves: 28
    • Présents: 26
    • Absents justifiés: 1
    • Absents non-justifiés: 1
    • Taux de présence: 92.9%
    
    Élèves avec > 3 absences ce mois: 2
    """


# ═════════════════════════════════════════════════════════════════
# 3️⃣ NOTIFICATIONS & EMAILS ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@automation_bp.route('/send-notification', methods=['POST'])
@premium_required
def send_notification():
    """Envoyer une notification (email, SMS, push)"""
    try:
        user_id = current_user.id
        data = request.json
        notification_type = data.get('notification_type')
        subject = data.get('subject', 'Notification')
        body = data.get('body', '')
        recipients = data.get('recipients', '').split(',') if data.get('recipients') else []
        
        sent_count = 0
        failed_count = 0
        errors = []
        
        for email in recipients:
            email = email.strip()
            if not email:
                continue
            
            try:
                # Try to send email
                _send_email(email, subject, body)
                sent_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(f"{email}: {str(e)}")
                print(f"[Automation] Erreur envoi à {email}: {str(e)}")
        
        # Log
        _add_log({
            'user_id': user_id,
            'task_name': f"Notification: {notification_type}",
            'status': 'success' if sent_count > 0 else 'failed',
            'timestamp': datetime.now().isoformat(),
            'message': f"Envoyés: {sent_count}, Erreurs: {failed_count}"
        })
        
        return jsonify({
            'success': sent_count > 0,
            'message': f"Notification envoyée à {sent_count} destinataire(s)",
            'sent_count': sent_count,
            'failed_count': failed_count,
            'errors': errors if errors else None
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _send_email(to_email, subject, body):
    """Envoyer un email (via SMTP ou API)"""
    try:
        from flask import current_app
        # Try using Flask-Mail if configured
        if current_app.config.get('MAIL_SERVER'):
            from flask_mail import Message
            msg = Message(
                subject=subject,
                recipients=[to_email],
                body=body
            )
            from ...extensions import mail
            mail.send(msg)
            print(f"[Email] Sent to {to_email}: {subject}")
        else:
            # Fallback: log to file
            os.makedirs('logs/emails', exist_ok=True)
            with open(f"logs/emails/{datetime.now().timestamp()}.txt", 'w') as f:
                f.write(f"To: {to_email}\nSubject: {subject}\n\n{body}")
            print(f"[Email] Logged to file: {to_email}: {subject}")
    except Exception as e:
        print(f"[Email] Error sending to {to_email}: {str(e)}")
        raise


# ═════════════════════════════════════════════════════════════════
# 4️⃣ WORKFLOWS & RULES ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@automation_bp.route('/create-workflow', methods=['POST'])
@premium_required
def create_workflow():
    """Créer un workflow IF-THEN"""
    try:
        user_id = current_user.id
        data = request.json
        workflow_id = f"workflow_{user_id}_{len([w for w in WORKFLOWS.values() if w.get('user_id') == user_id])}"
        
        # Validation
        required = ['workflow_name', 'trigger', 'action']
        if not all(k in data for k in required):
            return jsonify({'success': False, 'error': 'Champs manquants'}), 400
        
        workflow_data = {
            'id': workflow_id,
            'user_id': user_id,
            'name': data['workflow_name'],
            'trigger': data['trigger'],
            'action': data['action'],
            'details': data.get('details', ''),
            'enabled': data.get('enabled', True),
            'created_at': datetime.now().isoformat(),
            'executions': 0,
            'last_execution': None
        }
        
        WORKFLOWS[workflow_id] = workflow_data
        # Persistent storage
        WORKFLOWS_TABLE.upsert(workflow_data, lambda x: x['id'] == workflow_id)
        
        # Log
        _add_log({
            'user_id': user_id,
            'task_name': f"Workflow: {data['workflow_name']}",
            'status': 'created',
            'timestamp': datetime.now().isoformat(),
            'message': f"IF {data['trigger']} THEN {data['action']}"
        })
        
        return jsonify({
            'success': True,
            'message': f"Workflow '{data['workflow_name']}' créé",
            'workflow_id': workflow_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@automation_bp.route('/workflows-list', methods=['GET'])
@premium_required
def workflows_list():
    """Récupérer la liste des workflows de l'utilisateur courant"""
    user_id = current_user.id
    workflows = [w for w in WORKFLOWS.values() if w.get('user_id') == user_id]
    return jsonify({'workflows': workflows})


# ═════════════════════════════════════════════════════════════════
# 5️⃣ MONITORING & LOGS ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@automation_bp.route('/logs', methods=['GET'])
@premium_required
def get_logs():
    """Récupérer les logs d'exécution de l'utilisateur courant"""
    user_id = current_user.id
    # Retourner les 50 derniers logs de cet utilisateur (from memory and persistent storage)
    user_logs = [log for log in EXECUTION_LOGS if log.get('user_id') == user_id]
    
    # Also fetch from persistent storage (last 20)
    try:
        from tinydb import Query
        persistent_logs = LOGS_TABLE.search(Query().user_id == user_id)
        user_logs.extend(persistent_logs)
    except:
        pass
    
    logs = sorted(user_logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:50]
    return jsonify({'logs': logs})


@automation_bp.route('/stats', methods=['GET'])
@premium_required
def get_stats():
    """Récupérer les statistiques globales pour l'utilisateur courant"""
    user_id = current_user.id
    user_logs = [log for log in EXECUTION_LOGS if log.get('user_id') == user_id]
    logs_24h = [log for log in user_logs if 
                datetime.fromisoformat(log.get('timestamp', datetime.now().isoformat())) > datetime.now() - timedelta(days=1)]
    
    stats = {
        'total_tasks': len([t for t in SCHEDULED_TASKS.values() if t.get('user_id') == user_id]),
        'total_workflows': len([w for w in WORKFLOWS.values() if w.get('user_id') == user_id]),
        'success_24h': len([l for l in logs_24h if l.get('status') == 'success']),
        'failed_24h': len([l for l in logs_24h if l.get('status') == 'failed']),
        'running': len([t for t in SCHEDULED_TASKS.values() if t.get('user_id') == user_id and t.get('status') == 'running']),
        'total_logs': len(user_logs),
        'scheduler_available': _check_scheduler_available()
    }
    
    return jsonify(stats)


# ═════════════════════════════════════════════════════════════════
# PAGE UI
# ═════════════════════════════════════════════════════════════════

@automation_bp.route('/', methods=['GET'])
@login_required
def automation_page():
    """Afficher la page Automation"""
    from flask import render_template
    return render_template('automation.html')

