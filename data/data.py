from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from .progress import get_progress, set_progress

data_bp = Blueprint("data", __name__)

modules_data = [
    {
        "id": "cleaning",
        "title": "Data Cleaning",
        "lessons": [
            {"title": "Introduction au nettoyage de données",
             "content": "Comprendre les données sales, valeurs manquantes, doublons, types incorrects.",
             "quiz": {"type":"text","question":"Donnez un exemple de données manquantes."},
             "example":"Exemple : une colonne 'âge' avec des cellules vides."},
            {"title": "Techniques de nettoyage",
             "content": "Supprimer ou imputer valeurs manquantes, corriger types, détecter doublons.",
             "quiz": {"type":"radio","question":"Quelle technique supprime les lignes avec valeurs manquantes ?","options":["Dropna","Fillna","Replace"],"answer":"Dropna"},
             "example":"Ex: df.dropna() supprime toutes les lignes avec NaN."},
            {"title": "Validation & Qualité",
             "content": "Vérifier la cohérence des données après nettoyage.",
             "quiz": {"type":"text","question":"Comment vérifier des doublons dans un dataframe ?"},
             "example":"Ex: df.duplicated() retourne un booléen pour chaque ligne."}
        ]
    },
    {
        "id": "viz",
        "title": "Visualisation & Dashboard",
        "lessons": [
            {"title": "Introduction à la visualisation",
             "content": "Graphiques basiques : histogrammes, barres, scatterplots.",
             "quiz": {"type":"text","question":"Donnez un exemple de graphique pour distribuer des données."},
             "example":"Ex: plt.hist(data['age'])"},
            {"title": "Dashboard interactif",
             "content": "Créer des dashboards avec Plotly/Dash ou Streamlit.",
             "quiz": {"type":"radio","question":"Quel outil est pour dashboard web interactif ?","options":["Matplotlib","Dash","Seaborn"],"answer":"Dash"},
             "example":"Ex: fig = px.bar(df, x='année', y='ventes')"},
            {"title": "Storytelling & KPI",
             "content": "Présenter les insights avec visualisation et indicateurs pertinents.",
             "quiz": {"type":"text","question":"Donnez un KPI important pour un site e-commerce."},
             "example":"Ex: Taux de conversion, panier moyen."}
        ]
    },
    {
        "id": "ml",
        "title": "Modèles & Machine Learning",
        "lessons": [
            {"title": "Introduction au ML",
             "content": "Supervisé, non supervisé, régression, classification.",
             "quiz": {"type":"text","question":"Quel est un exemple de problème supervisé ?"},
             "example":"Ex: Prédire le prix d’une maison."},
            {"title": "Construction & évaluation de modèles",
             "content": "Split train/test, métriques (accuracy, RMSE).",
             "quiz": {"type":"radio","question":"Quelle métrique pour régression ?","options":["Accuracy","RMSE","F1"],"answer":"RMSE"},
             "example":"Ex: sklearn.metrics.mean_squared_error(y_true, y_pred)"},
            {"title": "Feature Engineering",
             "content": "Créer, transformer ou encoder des variables pour améliorer modèles.",
             "quiz": {"type":"text","question":"Comment encoder une variable catégorielle ?"},
             "example":"Ex: pd.get_dummies(df['ville'])"}
        ]
    },
    {
        "id": "prod",
        "title": "Production & Déploiement",
        "lessons": [
            {"title": "Préparer le modèle",
             "content": "Sauvegarder et versionner les modèles ML.",
             "quiz": {"type":"text","question":"Comment sauvegarder un modèle sklearn ?"},
             "example":"Ex: joblib.dump(model, 'model.pkl')"},
            {"title": "API & Webservice",
             "content": "Déployer modèle via Flask/FastAPI.",
             "quiz": {"type":"radio","question":"Quel framework pour API ML ?","options":["Django","Flask","Tkinter"],"answer":"Flask"},
             "example":"Ex: @app.route('/predict') pour endpoint de prédiction"},
            {"title": "Monitoring & Maintenance",
             "content": "Surveiller la performance et les dérives des modèles.",
             "quiz": {"type":"text","question":"Comment détecter un drift de données ?"},
             "example":"Ex: Comparer distribution de nouvelles données vs train."}
        ]
    }
]

@data_bp.route("/")
@login_required
def data_index():
    modules_with_progress = []
    for module in modules_data:
        level = get_progress(module['id'])
        modules_with_progress.append({**module, 'current_level': level})
    return render_template("data.html", modules=modules_with_progress)

@data_bp.route("/update_progress", methods=["POST"])
@login_required
def update_progress():
    data = request.json
    module_id = data.get("module_id")
    new_level = data.get("new_level")
    set_progress(module_id, new_level)
    return jsonify({"success": True})