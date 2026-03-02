from tinydb import TinyDB, Query
from flask_login import current_user
from pathlib import Path

# Créer ou pointer sur une base TinyDB dans /data/progress.json
db_path = Path(__file__).resolve().parent.parent / "data" / "progress.json"
db_path.parent.mkdir(exist_ok=True)  # créer dossier /data si absent
db = TinyDB(db_path)

def get_progress(module_id: str) -> int:
    """
    Retourne le niveau actuel atteint par l'utilisateur pour un module donné.
    Si aucune donnée, retourne 0.
    """
    if not current_user.is_authenticated:
        return 0

    Progress = Query()
    result = db.get((Progress.user_id == current_user.get_id()) & (Progress.module_id == module_id))
    if result:
        return result.get("level", 0)
    return 0

def set_progress(module_id: str, level: int):
    """
    Enregistre ou met à jour le niveau atteint par l'utilisateur pour un module.
    """
    if not current_user.is_authenticated:
        return

    Progress = Query()
    existing = db.get((Progress.user_id == current_user.get_id()) & (Progress.module_id == module_id))
    if existing:
        # Mise à jour seulement si niveau plus élevé
        if level > existing.get("level", 0):
            db.update({"level": level}, doc_ids=[existing.doc_id])
    else:
        # Ajouter nouvelle entrée
        db.insert({"user_id": current_user.get_id(), "module_id": module_id, "level": level})