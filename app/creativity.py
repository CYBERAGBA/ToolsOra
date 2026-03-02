from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from .progress import get_progress, set_progress

creativity_bp = Blueprint("creativity", __name__)

modules_data = [
    {
        "id":"graphic",
        "title":"Design Graphique",
        "lessons":[
            {"title":"Bases du design",
             "content":"Couleurs, typographie, mise en page.",
             "quiz":{"type":"text","question":"Donnez un exemple de combinaison de couleurs harmonieuse."},
             "example":"Ex: Bleu clair + Gris foncé."},
            {"title":"Outils de design",
             "content":"Figma, Canva, Photoshop.",
             "quiz":{"type":"radio","question":"Quel outil est collaboratif en ligne ?","options":["Photoshop","Figma","Illustrator"],"answer":"Figma"},
             "example":"Ex: Créer une maquette interactive dans Figma."},
            {"title":"Principes avancés",
             "content":"Grille, hiérarchie visuelle, contraste.",
             "quiz":{"type":"text","question":"Pourquoi utiliser la hiérarchie visuelle ?"},
             "example":"Ex: Pour guider l'œil sur les éléments importants."}
        ]
    },
    {
        "id":"uxui",
        "title":"UX / UI Design",
        "lessons":[
            {"title":"Introduction UX/UI",
             "content":"Comprendre expérience utilisateur et interface.",
             "quiz":{"type":"text","question":"Qu'est-ce qu'un wireframe ?"},
             "example":"Ex: Schéma de la page avant développement."},
            {"title":"Prototypage",
             "content":"Créer des prototypes interactifs.",
             "quiz":{"type":"radio","question":"Quel outil est utilisé pour prototypage rapide ?","options":["Axure","Excel","Word"],"answer":"Axure"},
             "example":"Ex: Tester un parcours utilisateur avant codage."},
            {"title":"Tests utilisateurs",
             "content":"Collecter feedback, améliorer UI.",
             "quiz":{"type":"text","question":"Pourquoi faire un test utilisateur ?"},
             "example":"Ex: Identifier les points de friction dans l'application."}
        ]
    },
    {
        "id":"motion",
        "title":"Motion Design & Vidéo",
        "lessons":[
            {"title":"Bases du motion design",
             "content":"Animation 2D, timing, easing.",
             "quiz":{"type":"text","question":"Citez un principe d'animation en motion design."},
             "example":"Ex: Ease-in / Ease-out pour fluidité."},
            {"title":"Outils animation",
             "content":"After Effects, Blender, Lottie.",
             "quiz":{"type":"radio","question":"Quel outil est utilisé pour animation vectorielle web ?","options":["After Effects","Lottie","Photoshop"],"answer":"Lottie"},
             "example":"Ex: Créer un loader animé pour une application."},
            {"title":"Optimisation vidéo",
             "content":"Compression, formats web, intégration.",
             "quiz":{"type":"text","question":"Pourquoi compresser une vidéo pour le web ?"},
             "example":"Ex: Réduire le temps de chargement des pages."}
        ]
    },
    {
        "id":"creativecoding",
        "title":"Creative Coding",
        "lessons":[
            {"title":"Introduction",
             "content":"Programmer pour créer visuels interactifs et art génératif.",
             "quiz":{"type":"text","question":"Donnez un exemple d'art génératif."},
             "example":"Ex: Visualisation dynamique en JS avec p5.js."},
            {"title":"Bibliothèques",
             "content":"p5.js, Processing, Three.js.",
             "quiz":{"type":"radio","question":"Quel outil est pour 3D Web ?","options":["p5.js","Three.js","Processing"],"answer":"Three.js"},
             "example":"Ex: Créer un cube 3D interactif."},
            {"title":"Projets avancés",
             "content":"Combiner code et design pour des installations interactives.",
             "quiz":{"type":"text","question":"Comment rendre une œuvre interactive ?"},
             "example":"Ex: Détecter souris ou capteurs pour changer visuel."}
        ]
    }
]

@creativity_bp.route("/")
@login_required
def creativity_index():
    modules_with_progress = []
    for module in modules_data:
        level = get_progress(module['id'])
        modules_with_progress.append({**module, 'current_level': level})
    return render_template("creativity.html", modules=modules_with_progress)

@creativity_bp.route("/update_progress", methods=["POST"])
@login_required
def update_progress():
    data = request.json
    module_id = data.get("module_id")
    new_level = data.get("new_level")
    set_progress(module_id, new_level)
    return jsonify({"success": True})