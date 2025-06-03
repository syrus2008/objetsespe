import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# Chemins des fichiers JSON
FOUND_ITEMS_FILE = "found_items.json"
LOST_ITEMS_FILE = "lost_items.json"
USERS_FILE = "users.json"


def _ensure_file_exists(file_path: str, default_content: Any = None):
    """Assure que le fichier existe, le crée si nécessaire avec un contenu par défaut"""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            if default_content is None:
                default_content = []
            json.dump(default_content, f, ensure_ascii=False, indent=2, default=str)


def _load_json(file_path: str) -> List[Dict]:
    """Charge les données d'un fichier JSON"""
    _ensure_file_exists(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Si le fichier est vide ou mal formaté, retourner une liste vide
        return []


def _save_json(file_path: str, data: List[Dict]):
    """Sauvegarde des données dans un fichier JSON"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def get_found_items() -> List[Dict]:
    """Récupère tous les objets trouvés"""
    return _load_json(FOUND_ITEMS_FILE)


def get_lost_items() -> List[Dict]:
    """Récupère tous les objets perdus"""
    return _load_json(LOST_ITEMS_FILE)


def add_found_item(item_data: Dict) -> Dict:
    """Ajoute un nouvel objet trouvé"""
    items = get_found_items()
    
    # Générer un ID unique
    item_data["id"] = str(uuid.uuid4())
    item_data["created_at"] = datetime.now().isoformat()
    item_data["possible_matches"] = []
    
    items.append(item_data)
    _save_json(FOUND_ITEMS_FILE, items)
    
    # Trouver d'éventuelles correspondances avec des objets perdus
    find_matches()
    
    return item_data


def add_lost_item(item_data: Dict) -> Dict:
    """Ajoute un nouvel objet perdu"""
    items = get_lost_items()
    
    # Générer un ID unique
    item_data["id"] = str(uuid.uuid4())
    item_data["created_at"] = datetime.now().isoformat()
    item_data["possible_matches"] = []
    
    items.append(item_data)
    _save_json(LOST_ITEMS_FILE, items)
    
    # Trouver d'éventuelles correspondances avec des objets trouvés
    find_matches()
    
    return item_data


def delete_item(item_id: str, item_type: str) -> bool:
    """Supprime un objet (perdu ou trouvé)"""
    file_path = FOUND_ITEMS_FILE if item_type == "found" else LOST_ITEMS_FILE
    items = _load_json(file_path)
    
    # Trouver et supprimer l'élément
    for i, item in enumerate(items):
        if item.get("id") == item_id:
            del items[i]
            _save_json(file_path, items)
            
            # Mettre à jour les correspondances
            find_matches()
            return True
    
    return False


def update_item(item_id: str, item_type: str, updated_data: Dict) -> Optional[Dict]:
    """Met à jour un objet (perdu ou trouvé)"""
    file_path = FOUND_ITEMS_FILE if item_type == "found" else LOST_ITEMS_FILE
    items = _load_json(file_path)
    
    for i, item in enumerate(items):
        if item.get("id") == item_id:
            # Préserver l'ID et la date de création
            updated_data["id"] = item_id
            updated_data["created_at"] = item.get("created_at")
            
            # Mettre à jour l'élément
            items[i] = updated_data
            _save_json(file_path, items)
            
            # Mettre à jour les correspondances
            find_matches()
            return updated_data
    
    return None


def find_matches():
    """
    Cherche des correspondances entre les objets perdus et trouvés
    basées sur des mots-clés dans la description et la proximité de date
    """
    lost_items = get_lost_items()
    found_items = get_found_items()
    
    # Réinitialiser les correspondances existantes
    for item in lost_items:
        item["possible_matches"] = []
    
    for item in found_items:
        item["possible_matches"] = []
    
    # Analyser et comparer chaque paire d'objets
    for found in found_items:
        found_desc = found.get("description", "").lower().split()
        found_date = found.get("found_date", "")
        
        for lost in lost_items:
            lost_desc = lost.get("description", "").lower().split()
            lost_date = lost.get("lost_date", "")
            
            # Compter les mots communs dans les descriptions
            common_words = set(found_desc) & set(lost_desc)
            
            # Si les dates sont proches et il y a des mots en commun
            if common_words and found_date and lost_date:
                # Ajouter l'ID de l'objet perdu aux correspondances de l'objet trouvé
                found["possible_matches"].append(lost["id"])
                
                # Ajouter l'ID de l'objet trouvé aux correspondances de l'objet perdu
                lost["possible_matches"].append(found["id"])
    
    # Sauvegarder les mises à jour
    _save_json(FOUND_ITEMS_FILE, found_items)
    _save_json(LOST_ITEMS_FILE, lost_items)


def get_users() -> List[Dict]:
    """Récupère la liste des utilisateurs"""
    return _load_json(USERS_FILE)


def add_user(username: str, hashed_password: str) -> Dict:
    """Ajoute un nouvel utilisateur"""
    users = get_users()
    
    # Vérifier si l'utilisateur existe déjà
    for user in users:
        if user.get("username") == username:
            return None
    
    new_user = {
        "username": username,
        "password": hashed_password
    }
    
    users.append(new_user)
    _save_json(USERS_FILE, users)
    
    return new_user


def authenticate_user(username: str, password: str) -> bool:
    """Authentifie un utilisateur"""
    users = get_users()
    
    for user in users:
        if user.get("username") == username and user.get("password") == password:
            return True
    
    return False


# Initialisation des fichiers au démarrage
def init_db():
    """Initialise la base de données si elle n'existe pas"""
    # Créer les fichiers de données s'ils n'existent pas
    _ensure_file_exists(FOUND_ITEMS_FILE)
    _ensure_file_exists(LOST_ITEMS_FILE)
    
    # Créer un utilisateur admin par défaut si le fichier n'existe pas
    if not os.path.exists(USERS_FILE):
        default_users = [
            {
                "username": "admin",
                # Mot de passe: admin123
                "password": "admin123"
            }
        ]
        _save_json(USERS_FILE, default_users)
