from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from .progress import get_progress, set_progress

business_bp = Blueprint("business", __name__)

modules_data = [
    {
        "id": "management",
        "title": "Management & Leadership",
        "lessons": [
            {"title":"Introduction au management",
             "content":"Principes de gestion d'équipe, leadership, motivation.",
             "quiz":{"type":"text","question":"Citez un exemple de bonne pratique en leadership."},
             "example":"Ex: Communiquer régulièrement avec son équipe."},
            {"title":"Gestion de projet",
             "content":"Méthodes Agile, Scrum, Kanban.",
             "quiz":{"type":"radio","question":"Quelle méthode utilise des sprints courts ?","options":["Waterfall","Scrum","Lean"],"answer":"Scrum"},
             "example":"Ex: Sprint de 2 semaines pour livrer une fonctionnalité."},
            {"title":"Prise de décision",
             "content":"Analyse, priorisation, gestion des risques.",
             "quiz":{"type":"text","question":"Comment prioriser les tâches importantes ?"},
             "example":"Ex: Matrice Eisenhower."}
        ]
    },
    {
        "id": "productivity",
        "title": "Productivité & Organisation",
        "lessons": [
            {"title":"Gestion du temps",
             "content":"Pomodoro, GTD, planification efficace.",
             "quiz":{"type":"text","question":"Qu'est-ce qu'une technique Pomodoro ?"},
             "example":"Ex: 25min de travail concentré + 5min pause."},
            {"title":"Outils collaboratifs",
             "content":"Slack, Trello, Notion pour équipe et projets.",
             "quiz":{"type":"radio","question":"Quel outil est pour la gestion de tâches ?","options":["Slack","Trello","Zoom"],"answer":"Trello"},
             "example":"Ex: Créer un board Trello avec cartes et checklist."},
            {"title":"Automatisation & flux de travail",
             "content":"Raccourcis, scripts, macros pour gagner du temps.",
             "quiz":{"type":"text","question":"Donnez un exemple d'automatisation simple."},
             "example":"Ex: Script qui renomme automatiquement des fichiers."}
        ]
    },
    {
        "id": "marketing",
        "title": "Marketing & Communication",
        "lessons": [
            {"title":"Bases du marketing",
             "content":"Segmentation, ciblage, positionnement.",
             "quiz":{"type":"text","question":"Citez un exemple de segmentation client."},
             "example":"Ex: Segmenter par âge ou localisation."},
            {"title":"Marketing digital",
             "content":"SEO, réseaux sociaux, email marketing.",
             "quiz":{"type":"radio","question":"Quel canal améliore le référencement naturel ?","options":["Email","SEO","Facebook Ads"],"answer":"SEO"},
             "example":"Ex: Optimiser titres et meta description."},
            {"title":"Analyse des campagnes",
             "content":"KPI, ROI, dashboards.",
             "quiz":{"type":"text","question":"Qu'est-ce qu'un KPI important pour un site web ?"},
             "example":"Ex: Taux de conversion ou trafic unique."}
        ]
    },
    {
        "id": "finance",
        "title": "Finance & Gestion",
        "lessons": [
            {"title":"Comptabilité de base",
             "content":"Bilan, compte de résultat, trésorerie.",
             "quiz":{"type":"text","question":"Qu'est-ce qu'un bilan ?"},
             "example":"Ex: Actif = Passif + Capitaux propres."},
            {"title":"Analyse financière",
             "content":"Ratios, marge, rentabilité.",
             "quiz":{"type":"radio","question":"Quel ratio mesure la rentabilité ?","options":["ROE","ROI","EPS"],"answer":"ROI"},
             "example":"Ex: ROI = profit / investissement."},
            {"title":"Budgets & prévisions",
             "content":"Prévoir dépenses et revenus, planifier investissement.",
             "quiz":{"type":"text","question":"Pourquoi établir un budget prévisionnel ?"},
             "example":"Ex: Pour anticiper les besoins en trésorerie."}
        ]
    }
]

@business_bp.route("/")
@login_required
def business_index():
    modules_with_progress = []
    for module in modules_data:
        level = get_progress(module['id'])
        modules_with_progress.append({**module, 'current_level': level})
    return render_template("business.html", modules=modules_with_progress)

@business_bp.route("/update_progress", methods=["POST"])
@login_required
def update_progress():
    data = request.json
    module_id = data.get("module_id")
    new_level = data.get("new_level")
    set_progress(module_id, new_level)
    return jsonify({"success": True})