# 🚀 Guide de Déploiement OraHub sur Render

Ce guide explique comment déployer votre application Flask OraHub en production sur [Render.com](https://render.com).

---

## 📋 Pré-requis

- ✅ Compte GitHub avec votre code versionné
- ✅ Compte Render.com (inscription gratuite)
- ✅ Fichiers de configuration préparés:
  - `Procfile` (définit la commande de démarrage)
  - `runtime.txt` (version Python 3.11.9)
  - `requirements.txt` (dépendances + gunicorn)
  - `run.py` (point d'entrée adapté)

---

## 📦 Étape 1: Préparer le Code pour Production

### A. Vérifier les fichiers de déploiement

```bash
# Assurez-vous que ces fichiers existent à la racine du projet:
ls -la Procfile runtime.txt requirements.txt run.py
```

**Contenu requis:**

**Procfile**
```
web: gunicorn app:app
```

**runtime.txt**
```
python-3.11.9
```

**requirements.txt** *(doit inclure gunicorn)*
```
Flask==2.2.5
gunicorn==21.2.0
tinydb==4.7.0
... (autres dépendances)
```

### B. Mettre à jour `config.py`

✅ Notre version mise à jour inclut:
- Gestion `DATABASE_PATH` pour TinyDB
- Environnements multiples (dev, prod, test)
- Sécurité hardened pour HTTPS/HTTPS Secure cookies

### C. Vérifier les chemins des fichiers

TinyDB utilise des fichiers JSON. En production (Render), utilisez `/tmp` ou configurez un path writable:

```python
# Dans .env Render:
DATABASE_PATH=/tmp/db.json
```

---

## 🔐 Étape 2: Préparer les Variables d'Environnement

### Sur Render Dashboard:

1. Allez à votre service (ou créez-en un nouveau)
2. **Settings → Environment**
3. Ajoutez ces variables:

#### Variables Essentielles

```env
# Environnement
FLASK_ENV=production
FLASK_DEBUG=False

# Sécurité CRITIQUE
SECRET_KEY=<générez une clé longue et aléatoire>
# Exemple: openssl rand -hex 32

# Database (TinyDB)
DATABASE_PATH=/tmp/db.json

# Email (si utilisé)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-app-password
MAIL_DEFAULT_SENDER=votre-email@gmail.com

# Sessions sécurisés (production)
SESSION_COOKIE_SECURE=True
REMEMBER_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=Strict

# Paypal (si utilisé)
PAYPAL_CLIENT_ID=votre-client-id
PAYPAL_SECRET=votre-secret

# Mobile Money
MOBILE_MONEY_PROVIDER=orange_money
MOBILE_MONEY_API_KEY=votre-clé
MOBILE_MONEY_API_SECRET=votre-secret

# Twilio (SMS/WhatsApp)
TWILIO_ACCOUNT_SID=votre-sid
TWILIO_AUTH_TOKEN=votre-token
```

#### Comment générer SECRET_KEY sécurisée:

```bash
# Sur votre machine locale:
openssl rand -hex 32
# Sortie: a3f9e2b1c4d6e8f0... (copier dans Render)

# Ou en Python:
python -c "import secrets; print(secrets.token_hex(32))"
```

⚠️ **JAMAIS de SECRET_KEY dure dans le code!**

---

## 🌐 Étape 3: Connecter GitHub à Render

### A. Pousser votre code sur GitHub

```bash
git add .
git commit -m "Préparation pour déploiement Render"
git push origin main
```

### B. Sur Render.com:

1. **Dashboard → New → Web Service**
2. **Connectez GitHub**
3. Sélectionnez votre repo `orahub`
4. Configurez:
   - **Name:** `orahub` (ou le nom de votre app)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Starter` (gratuit) ou supérieur

---

## 🔨 Étape 4: Configuration Avancée sur Render

### Logs et Diagnostiques

Pour vérifier les logs en temps réel:
```
Render Dashboard → Logs → Voir les erreurs
```

### Health Check

Render vérifie automatiquement si votre app démarre correctement.
Assurez-vous:
- ✅ Pas d'erreurs lors de l'import (`from app import create_app`)
- ✅ Base de données TinyDB accessible
- ✅ Pas de fichiers manquants

### Base de Données - Solutions

**Problème:** TinyDB est file-based, Render efface `/app` à chaque déploiement

**Solutions:**

#### Option 1: Utiliser Render Disk (Recommandé)
```
Render Dashboard → Disks → Attach Persistent Disk
Mount path: /var/data
```

Puis dans `.env`:
```
DATABASE_PATH=/var/data/db.json
```

#### Option 2: Utiliser une BDD Cloud
```
# PostgreSQL sur Render
DATABASE_URL=postgresql://user:pass@host/dbname

# MongoDB sur MongoDB Atlas
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname
```

#### Option 3: Accepter la perte de données (développement uniquement)
```
DATABASE_PATH=/tmp/db.json
```
Les données seront réinitialisées à chaque redémarrage.

---

## ✅ Étape 5: Test et Validation

### A. Après le déploiement

1. Render construit automatiquement votre app
2. Attendez la fin du build (status = "Live")
3. Visitez votre URL: `https://orahub.onrender.com` (exemple)

### B. Vérifier que tout fonctionne

```bash
# Tester la page d'accueil
curl https://votre-app.onrender.com/

# Tester une route API
curl https://votre-app.onrender.com/api/health

# Vérifier les logs
# Render Dashboard → Logs
```

### C. Erreurs Courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `Build failed` | Dépendance manquante | Vérifier `requirements.txt` |
| `Import error: app` | Structure de dossiers | Vérifier que `app/__init__.py` existe |
| `Secret key not defined` | SECRET_KEY manquante | Ajouter en variables env Render |
| `Port binding failed` | PORT en dur dans code | Utiliser `os.environ.get('PORT', 5000)` |
| `Database not found` | Chemin TinyDB incorrect | Vérifier `DATABASE_PATH` |

---

## 🔄 Déploiements Futurs

Chaque `git push` déclenche un redéploiement automatique:

```bash
# Développer localement
git add .
git commit -m "Nouvelle feature"
git push origin main

# Render détecte automatiquement → rebuild → live en ~2-3 min
```

---

## 📊 Monitoring Production

### Vérifier la santé de l'app

```bash
# Depuis votre terminal
curl -I https://votre-app.onrender.com

# Réponse attendue: HTTP/1.1 200 OK
```

### Lire les logs Render

```
Render Dashboard → Your App → Logs
```

Cherchez:
- ✅ `[OraHub] Starting server in PRODUCTION mode`
- ✅ `Running on all addresses (0.0.0.0)`
- ❌ Erreurs Python/Database

---

## 🚨 Sécurité - Checklist Pre-Production

- [ ] SECRET_KEY définie et complexe (32+ caractères)
- [ ] DEBUG = False en production
- [ ] SESSION_COOKIE_SECURE = True
- [ ] MAIL_USERNAME/PASSWORD configurés
- [ ] Base de données accessible (Disk ou Cloud DB)
- [ ] HTTPS forcé (Render le fait automatiquement)
- [ ] Pas de secrets en dur dans le code

---

## 📞 Dépannage

### Problème: App redémarre constamment

**Cause:** Erreur non gérée
**Solution:**
```bash
# Vérifier les logs Render
# Corriger l'erreur localement
# git push pour redéployer
```

### Problème: Lent au démarrage

**Cause:** Imports lourds (torch, transformers)
**Solution:**
```python
# Dans app/__init__.py: charger lazy les imports IA/ML
try:
    import torch
    from transformers import pipeline
except ImportError:
    print("⚠️ AI/ML dependencies not available")
```

### Problème: Erreurs de permission sur fichiers

**Cause:** TinyDB ne peut pas créer `data/db.json`
**Solution:**
```python
# config.py: créer le dossier s'il n'existe pas
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
```

---

## 🎉 Succès!

Votre app est maintenant en production sur Render! 🚀

**URL:** `https://orahub.onrender.com` (remplacez par le vrai nom)

Pour les mises à jour: `git push origin main` déclenche automatiquement un redéploiement.

---

## 📚 Ressources

- [Render Docs - Python](https://render.com/docs/deploy-python)
- [Flask Production Deployment](https://flask.palletsprojects.com/en/2.2.x/deploying/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/latest/)
- [TinyDB Best Practices](https://tinydb.readthedocs.io/)

