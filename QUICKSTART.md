# 🚀 Quick Start Guide - OraHub

Bienvenue sur OraHub! Voici comment démarrer en 2 minutes.

## Installation & Démarrage

### 1. Installation des dépendances
```bash
cd c:\Users\Monsieur AGBA\Desktop\orahub
pip install -r requirements.txt
pip install reportlab openpyxl  # Packages Automation
```

### 2. Lancer le serveur
```bash
python run.py
```

Ou double-cliquer sur `run_server.bat`

### 3. Ouvrir dans le navigateur
```
http://localhost:5000
```

---

## 📍 Navigation rapide

| Page | URL | Fonction |
|------|-----|----------|
| **Accueil** | `/` | Aperçu avec cartes des 3 modules |
| **Education** | `/modules/education/` | Programme de formation (5 domaines) |
| **SaaS Tools** | `/modules/saas/` | Outils productivité (code, QR, CV, calc) |
| **Automation** | `/modules/automation/` | Plannification, rapports, workflows, monitoring |

---

## 🎯 Premières actions

### ✅ Tester Automation (recommandé)

1. Allez sur: http://localhost:5000/modules/automation/

2. **Onglet 1: Planification**
   - Type: "Sauvegarde de données"
   - Fréquence: "Quotidien"
   - Heure: 02:00
   - Cliquer "Créer la tâche"
   - ✓ Tâche créée et affichée dans la liste

3. **Onglet 2: Rapports**
   - Type: "Résumé ventes (CA, commandes, clients)"
   - Format: "PDF"
   - Email: votre_email@example.com
   - Cliquer "Créer le rapport"
   - ✓ Rapport généré

4. **Onglet 3: Notifications**
   - Sujet: "Bienvenue sur OraHub"
   - Contenu: "Content du message..."
   - Emails: email1@example.com, email2@example.com
   - Cliquer "Envoyer"
   - ✓ Notif envoyée (logs affichés)

5. **Onglet 5: Monitoring**
   - Voir l'historique des exécutions
   - Cliquer "Rafraîchir logs"
   - ✓ Tous vos tests s'affichent

### ✅ Tester SaaS Tools

1. Allez sur: http://localhost:5000/modules/saas/

2. **Code Generator**
   - Langage: Python
   - Nom: "HelloWorld"
   - Générer → Reçoit template boilerplate

3. **QR Generator**
   - URL: https://orahub.com
   - Générer → QR code créé

4. **CV Professional**
   - Remplir formulaire (photo optionnelle)
   - Générer → DOCX stylisé créé + tentative PDF

5. **Calculator**
   - Opération: 100 + 25 =
   - = Résultat: 125

### ✅ Visiter Education

1. Allez sur: http://localhost:5000/modules/education/

2. Voir 5 domaines (cartes numérotées)

3. Cliquer "Structure & progression" pour détails

---

## 🔧 Configuration

### SMTP pour emails réels
Éditez `config.py`:
```python
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'
```

### Chemin LibreOffice (PDF export)
Windows:
```
LIBREOFFICE_PATH = C:\Program Files\LibreOffice\program\soffice.exe
```

Linux:
```
LIBREOFFICE_PATH = /usr/bin/soffice
```

### API externes
Définissez dans variables d'environnement:
```
MAILGUN_API_KEY=...
STRIPE_API_KEY=...
```

---

## 📚 Documentation

- **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** — Résumé complet de ce qui a été fait
- **[docs/automation_architecture.md](./docs/automation_architecture.md)** — Guide complet Automation (1500+ lignes)
- **[app/modules/automation/README.md](./app/modules/automation/README.md)** — Guide technique Automation
- **[app/modules/saas/README.md](./app/modules/saas/README.md)** — Guide technique SaaS (si exists)
- **[app/modules/education/README.md](./app/modules/education/README.md)** — Guide Education (si exists)

---

## 🧪 Tests

Lancer la suite de tests Automation:
```bash
python test_automation.py
```

Ou tester manuellement avec curl:
```bash
# Créer tâche
curl -X POST http://localhost:5000/modules/automation/schedule-task \
  -H "Content-Type: application/json" \
  -d '{"task_type":"backup","frequency":"daily","execution_time":"02:00","description":"Test","enabled":true}'

# Lister tâches
curl http://localhost:5000/modules/automation/tasks-list

# Voir logs
curl http://localhost:5000/modules/automation/logs
```

---

## ❓ Troubleshooting

### "ModuleNotFoundError: No module named 'X'"
**Solution:** 
```bash
pip install -r requirements.txt
```

### "Port 5000 already in use"
**Solution:** 
```bash
# Option 1: Tuer le processus
lsof -ti:5000 | xargs kill -9

# Option 2: Changer le port dans run.py
app.run(host='0.0.0.0', port=5001, debug=False)
```

### "LibreOffice not found (PDF export échoue)"
**Solution:**
- Installer LibreOffice depuis libreoffice.org
- OU définir `LIBREOFFICE_PATH` en variable d'env
- CV export tombe back sur pdf2docx library

### "Email not sending"
**Solution:**
- Vérifier config SMTP dans `config.py`
- Utiliser 2FA app password (pas password direct) pour Gmail
- Logs d'email créés dans `logs/emails/`

### Erreur d'encodage UTF-8 sur Windows
**Solution:** Ajouter au top de routes.py:
```python
# -*- coding: utf-8 -*-
```

---

## 🚀 Déploiement

### Local → Production (simple)

1. **Installer gunicorn** (WSGI server):
   ```bash
   pip install gunicorn
   ```

2. **Lancer avec gunicorn** (4 workers):
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

3. **Config reverse proxy nginx**:
   ```nginx
   server {
       listen 80;
       server_name orahub.com;
       
       location / {
           proxy_pass http://localhost:5000;
       }
   }
   ```

4. **Lancer avec supervisor** (auto-restart):
   ```bash
   pip install supervisor
   supervisord -c supervisord.conf
   ```

---

## 👥 Support & Ressources

- **Forum/Chat:** [Slack workspace - si disponible]
- **Email:** support@orahub.com
- **Docs:** /docs/automation_architecture.md
- **Issues:** Ouvrir ticket sur GitHub

---

## 🎁 Prochaines étapes

1. ✅ **Aujourd'hui:** Tester les 3 modules (Education, SaaS, Automation)
2. 📅 **Cette semaine:** Configurer SMTP réel, déployer en staging
3. 📅 **Ce mois:** Ajouter authentification utilisateurs, analytics
4. 📅 **Prochain mois:** Lancer MVP commercial, pricing SaaS

---

## 🎉 Bienvenue!

Vous avez accès à une plateforme **modulaire, sécurisée et scalable** prête pour production.

💡 **Conseil:** Commencez par tester Automation (c'est la partie la plus cool!) 🤖

Bon développement! 🚀

---

**OraHub — Éducation, Outils & Automatisation**
