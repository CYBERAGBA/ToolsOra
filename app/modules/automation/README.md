# 🤖 Module Automation - OraHub

Système complet d'automatisation pour planifier des tâches, générer des rapports, envoyer des notifications et orchestrer des workflows sans intervention humaine.

## 🎯 Objectives

✓ **Planification de tâches** — Sauvegardes, imports, syncs 24h/24  
✓ **Génération de rapports** — PDF, Excel, HTML générés automatiquement  
✓ **Notifications & Emails** — Envois massifs avec templates et retry logic  
✓ **Workflows IF-THEN** — Orchestration d'événements et d'actions  
✓ **Monitoring temps réel** — Logs traçables, dashboards, alertes  

## 🚀 Features implémentées

### 1. Planification de tâches (Task Scheduling)
- **Endpoints**: `POST /modules/automation/schedule-task`, `GET /modules/automation/tasks-list`
- **Fréquences**: hourly, daily, weekly, monthly
- **Backend**: APScheduler (cron-like)
- **Exemple d'utilisation**:
  ```bash
  curl -X POST http://localhost:5000/modules/automation/schedule-task \
    -H "Content-Type: application/json" \
    -d '{
      "task_type": "backup",
      "frequency": "daily",
      "execution_time": "02:00",
      "description": "Sauvegarde quotidienne",
      "enabled": true
    }'
  ```

### 2. Génération de rapports (Report Generation)
- **Endpoints**: `POST /modules/automation/generate-report`
- **Types**: sales_summary, user_stats, inventory, attendance, custom
- **Formats**: PDF, Excel, HTML
- **Envoi automatique** aux destinataires spécifiés
- **Exemple**:
  ```bash
  curl -X POST http://localhost:5000/modules/automation/generate-report \
    -H "Content-Type: application/json" \
    -d '{
      "report_type": "sales_summary",
      "output_format": "pdf",
      "recipients": "manager@company.com",
      "frequency": "daily"
    }'
  ```

### 3. Notifications & Emails (Notifications)
- **Endpoints**: `POST /modules/automation/send-notification`
- **Types**: welcome, course_reminder, payment_reminder, newsletter, alert, custom
- **Support de templates** avec variables `{{user_name}}`, `{{course_title}}`, etc.
- **Retry logic** intégré
- **Exemple**:
  ```bash
  curl -X POST http://localhost:5000/modules/automation/send-notification \
    -H "Content-Type: application/json" \
    -d '{
      "notification_type": "welcome",
      "subject": "Bienvenue sur OraHub!",
      "body": "Bonjour {{user_name}}, bienvenue...",
      "recipients": "newuser@example.com",
      "schedule_send": false
    }'
  ```

### 4. Workflows & Règles (Workflows IF-THEN)
- **Endpoints**: `POST /modules/automation/create-workflow`, `GET /modules/automation/workflows-list`
- **Déclencheurs** (IF): new_user, new_file, payment_missed, inventory_low, time_event, api_request
- **Actions** (THEN): send_email, create_task, update_record, trigger_backup, call_webhook, generate_report
- **Exemple**:
  ```bash
  curl -X POST http://localhost:5000/modules/automation/create-workflow \
    -H "Content-Type: application/json" \
    -d '{
      "workflow_name": "Auto-invoice on new order",
      "trigger": "new_user",
      "action": "send_email",
      "details": "Send welcome email with invoice",
      "enabled": true
    }'
  ```

### 5. Monitoring & Logs (Monitoring)
- **Endpoints**: `GET /modules/automation/logs`, `GET /modules/automation/stats`
- **Logs traçables**: task_id, status, timestamp, message, error
- **Statistiques**: succès/erreurs 24h, tâches en cours d'exécution
- **Exemple**:
  ```bash
  # Récupérer les logs
  curl http://localhost:5000/modules/automation/logs
  
  # Récupérer les statistiques
  curl http://localhost:5000/modules/automation/stats
  ```

## 📁 Structure des fichiers

```
app/modules/automation/
├── __init__.py              # Blueprint registration
├── routes.py                # All API endpoints and logic
└── templates/
    └── (none - UI is in templates/automation.html)

templates/
├── automation.html          # Main UI (5 tabs: scheduling, reports, notifications, workflows, monitoring)
└── (linked from index.html)

docs/
└── automation_architecture.md  # Complete technical documentation
```

## 🔧 Configuration

### Variables d'environnement (optionnelles)
```bash
# SMTP pour envois d'emails
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# API externes (Mailgun, Twilio, etc.)
MAILGUN_API_KEY=...
TWILIO_API_KEY=...
```

### Installation des dépendances
```bash
pip install apscheduler reportlab openpyxl pillow
```

## 📊 Cas d'usage réels

### 🎓 École / Université
- ✓ Rappels d'inscription automatiques
- ✓ Rapport de présences quotidien
- ✓ Génération de bulletins mensuels
- ✓ Rappel paiement scolarité
- ✓ Sauvegarde base de données

Voir [docs/automation_architecture.md#école](./docs/automation_architecture.md#41--école--université) pour détails.

### 💼 PME / Commerce
- ✓ Rapport de ventes quotidien
- ✓ Alerte stock critique
- ✓ Relance facture impayée (3 niveaux)
- ✓ Export comptabilité auto
- ✓ Backup et archivage

Voir [docs/automation_architecture.md#pme](./docs/automation_architecture.md#42--pme--commerce) pour détails.

### 👨‍💼 Freelance / Consultant
- ✓ Facturation automatique (1e du mois)
- ✓ Rappel paiement après 7/15j
- ✓ Rapport hebdomadaire productivité
- ✓ Backup cloud projet
- ✓ Génération devis auto

Voir [docs/automation_architecture.md#freelance](./docs/automation_architecture.md#43--freelance--consultant) pour détails.

## 🧪 Tests

Lancer la suite de tests complète :
```bash
python test_automation.py
```

Ou tester manuellement via curl/Postman :
```bash
# 1. Créer une tâche
curl -X POST http://localhost:5000/modules/automation/schedule-task \
  -H "Content-Type: application/json" \
  -d '{"task_type":"backup","frequency":"daily","execution_time":"02:00","description":"Test","enabled":true}'

# 2. Lister les tâches
curl http://localhost:5000/modules/automation/tasks-list

# 3. Générer un rapport
curl -X POST http://localhost:5000/modules/automation/generate-report \
  -H "Content-Type: application/json" \
  -d '{"report_type":"sales_summary","output_format":"pdf","recipients":"test@example.com","frequency":"once"}'

# 4. Envoyer une notification
curl -X POST http://localhost:5000/modules/automation/send-notification \
  -H "Content-Type: application/json" \
  -d '{"notification_type":"welcome","subject":"Hi","body":"Welcome!","recipients":"user@example.com"}'

# 5. Créer un workflow
curl -X POST http://localhost:5000/modules/automation/create-workflow \
  -H "Content-Type: application/json" \
  -d '{"workflow_name":"Test","trigger":"new_user","action":"send_email","enabled":true}'

# 6. Voir les logs
curl http://localhost:5000/modules/automation/logs

# 7. Voir les stats
curl http://localhost:5000/modules/automation/stats
```

## 📈 Évolution future

### Phase 1: Dashboards temps réel (3-6 mois)
- WebSockets pour live updates
- Grafana/Chart.js pour visualisation
- Real-time error tracking

### Phase 2: IA & Intelligence (6-12 mois)
- Anomaly detection (détecte taux erreur anormaux)
- Optimisation de la planification
- Recommandations d'automatisation auto
- LLM pour générer des workflows

### Phase 3: Autonomie (12-18 mois)
- Auto-scaling des ressources
- Auto-healing en cas d'erreur
- Chatbot pour exécuter des commandes (Slack)
- Entités intelligentes autonomes

Voir [docs/automation_architecture.md#évolution](./docs/automation_architecture.md#9-évolution-vers-ia-et-dashboards) pour détails.

## 🔐 Sécurité

✓ **Secrets**: Variables d'environnement, jamais en dur  
✓ **Encryption**: TLS/HTTPS en transit, données sensibles chiffrées  
✓ **Audit**: Trace complète (user_id, action, timestamp, IP)  
✓ **Rate limiting**: Max 10 requêtes/heure par endpoint  
✓ **Isolation**: Chaque tâche isolée, rollback en cas d'erreur  

Voir [docs/automation_architecture.md#sécurité](./docs/automation_architecture.md#6-sécurité) pour guide complet.

## 💰 Monétisation

### SaaS Pricing
```
Starter      $29/mois   — 10 tâches, 1k emails/mois
Professional $99/mois   — Illimité, workflows custom
Enterprise   $299/mois  — Everything, SLA 99.9%
```

### Usage-Based
- Email: $0.01/envoi
- SMS: $0.05/SMS
- Rapport: $0.50
- Workflow: $0.10

### Services managés
Consulter pour automatiser leurs processus: 500€ → 2000€ par projet.

Voir [docs/automation_architecture.md#monétisation](./docs/automation_architecture.md#8-stratégie-de-monétisation) pour détails.

## 🤝 Support & Contribution

Pour toute question ou bug, ouvrir une issue ou contacter le support.

---

**Created with ❤️ by OraHub**  
Documentation: [docs/automation_architecture.md](./docs/automation_architecture.md)
