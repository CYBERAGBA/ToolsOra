from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from .progress import get_progress, set_progress

from app.models import User

technologie_bp = Blueprint('technologie', __name__, url_prefix='/technologie')

# Données des modules enrichies
modules_data = [
    {
        "id": "ia",
        "title": "Intelligence Artificielle",
        "lessons": [
            {"title": "Introduction à l’IA",
             "content": "Découverte de l'IA : assistants vocaux, recommandations Netflix, voitures autonomes. Concepts clés : algorithmes, données, modèles.",
             "quiz": {"type": "text", "question": "Donnez un exemple concret d'IA dans la vie quotidienne."},
             "example": "Exemple : Netflix recommande des films selon vos habitudes."},
            {"title": "Machine Learning",
             "content": "Apprentissage supervisé, non supervisé et renforcement. Exemple : prédiction de prix, clustering client.",
             "quiz": {"type": "radio", "question": "Quel type d'apprentissage utilise des données étiquetées ?", "options":["Supervisé","Non supervisé","Renforcement"], "answer":"Supervisé"},
             "example": "Exemple : Prédire le prix d’une maison selon ses caractéristiques."},
            {"title": "Deep Learning",
             "content": "Réseaux neuronaux, NLP et Computer Vision. Exemple : reconnaissance d’images, génération de texte.",
             "quiz": {"type": "text", "question": "Qu'est-ce qu'un réseau convolutif ?"},
             "example": "Exemple : Détection de chiens et chats dans des images."}
        ]
    },
    {
        "id": "devweb",
        "title": "Développement Web",
        "lessons": [
            {"title": "HTML & CSS",
             "content": "Structure et style des pages web. Ex: balises <div>, <section>, CSS Flexbox et Grid.",
             "quiz": {"type":"text", "question":"À quoi sert 'display:flex' en CSS ?"},
             "example": "Ex: Disposer des cartes côte à côte facilement."},
            {"title": "JavaScript",
             "content": "Interaction côté client : DOM, événements, fonctions. Ex: changer le contenu d’un div dynamiquement.",
             "quiz": {"type":"radio", "question":"Comment ajouter un événement click sur un bouton ?", "options":["onclick HTML","addEventListener JS","Aucune"], "answer":"addEventListener JS"},
             "example": "Ex: Afficher un message quand l’utilisateur clique."},
            {"title": "Flask & Backend",
             "content": "Création de routes, templates, formulaires et TinyDB. Exemple : créer un blog simple.",
             "quiz": {"type":"text", "question":"Quelle fonction Flask rend un template HTML ?"},
             "example": "Ex: render_template('page.html', data=...) pour envoyer des données."}
        ]
    },
    {
        "id": "cyber",
        "title": "Cybersécurité",
        "lessons": [
            {"title": "Réseaux & Sécurité",
             "content": "TCP/IP, firewall, VPN. Exemple: protéger un réseau d'entreprise.",
             "quiz": {"type":"text","question":"Qu'est-ce qu'un firewall ?"},
             "example": "Ex: Bloquer le trafic suspect vers un serveur."},
            {"title": "Tests d’intrusion",
             "content": "Identifier les failles et vulnérabilités. Ex: test XSS sur formulaire web.",
             "quiz": {"type":"text","question":"Donnez un exemple d'attaque XSS."},
             "example": "Ex: injecter <script>alert('XSS')</script> pour tester."},
            {"title": "Ethical Hacking",
             "content": "Audit avancé et reporting. Exemple: pentest complet serveur web.",
             "quiz": {"type":"radio","question":"Hacker éthique ou malveillant ?", "options":["Éthique","Malveillant"], "answer":"Éthique"},
             "example": "Ex: Signaler une faille trouvée au responsable du serveur."}
        ]
    },
    {
        "id": "cloud",
        "title": "Cloud Computing & DevOps",
        "lessons": [
            {"title": "Concepts Cloud & Virtualisation",
             "content": "IaaS, PaaS, SaaS, VM, containers.",
             "quiz": {"type":"text","question":"Donnez un exemple de service PaaS."},
             "example": "Ex: Heroku ou AWS Elastic Beanstalk."},
            {"title": "AWS, Docker & CI/CD",
             "content": "Déploiement cloud avec Docker et pipelines CI/CD.",
             "quiz": {"type":"radio","question":"À quoi sert Docker ?","options":["Virtualiser","Compiler","Analyser logs"],"answer":"Virtualiser"},
             "example": "Ex: Conteneuriser une application pour la déployer sur AWS."},
            {"title": "Kubernetes & Architecture Scalable",
             "content": "Orchestration containers, scaling, haute disponibilité.",
             "quiz": {"type":"text","question":"Qu'est-ce qu'un pod Kubernetes ?"},
             "example": "Ex: Un pod contient une ou plusieurs instances d’un container en cluster."}
        ]
    }
]

@technologie_bp.route("/")
@login_required
def technologie():
    modules_with_progress = []
    for module in modules_data:
        level = get_progress(module['id'])
        modules_with_progress.append({**module, 'current_level': level})
    return render_template("technologie.html", modules=modules_with_progress)

# ===============================
# API UPDATE PROGRESS
# ===============================

@technologie_bp.route('/update-progress', methods=['POST'])
@login_required
def update_progress():
    data = request.get_json()

    module = data.get("module")
    section = data.get("section")
    level = data.get("level")

    current_user.update_progress(module, section, level)

    return jsonify({"status": "success"})