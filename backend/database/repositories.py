from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.models import User, FoundItem, LostItem
from passlib.context import CryptContext
import uuid
from datetime import datetime
from ..services.cloud_storage import cloud_storage_service

# Configuration du hachage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_user(self, username: str, password: str, is_admin: bool = False) -> User:
        hashed_password = self.get_password_hash(password)
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()
    
    def create_admin_if_not_exists(self):
        # Créer un utilisateur admin par défaut s'il n'existe pas
        admin = self.get_user_by_username("admin")
        if not admin:
            self.create_user("admin", "admin123", True)


class FoundItemRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[FoundItem]:
        return self.db.query(FoundItem).order_by(FoundItem.created_at.desc()).all()
    
    def get_by_id(self, item_id: str) -> Optional[FoundItem]:
        return self.db.query(FoundItem).filter(FoundItem.id == item_id).first()
    
    def create(self, item_data: dict) -> FoundItem:
        item = FoundItem(
            id=str(uuid.uuid4()),
            **item_data
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def update(self, item_id: str, item_data: dict) -> Optional[FoundItem]:
        item = self.get_by_id(item_id)
        if not item:
            return None
        
        # Si l'URL de l'image change et qu'il y avait une ancienne image, supprimer l'ancienne
        if "image_url" in item_data and item.image_url and item.image_url != item_data["image_url"]:
            cloud_storage_service.delete_file(item.image_url)
        
        # Mettre à jour les champs
        for key, value in item_data.items():
            setattr(item, key, value)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete(self, item_id: str) -> bool:
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        # Supprimer l'image de S3 si elle existe
        if item.image_url:
            cloud_storage_service.delete_file(item.image_url)
        
        self.db.delete(item)
        self.db.commit()
        return True


class LostItemRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[LostItem]:
        return self.db.query(LostItem).order_by(LostItem.created_at.desc()).all()
    
    def get_by_id(self, item_id: str) -> Optional[LostItem]:
        return self.db.query(LostItem).filter(LostItem.id == item_id).first()
    
    def create(self, item_data: dict) -> LostItem:
        item = LostItem(
            id=str(uuid.uuid4()),
            **item_data
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def update(self, item_id: str, item_data: dict) -> Optional[LostItem]:
        item = self.get_by_id(item_id)
        if not item:
            return None
        
        # Mettre à jour les champs
        for key, value in item_data.items():
            setattr(item, key, value)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete(self, item_id: str) -> bool:
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True


class MatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.found_repo = FoundItemRepository(db)
        self.lost_repo = LostItemRepository(db)
    
    def find_matches(self):
        """
        Trouve des correspondances potentielles entre objets perdus et trouvés
        basées sur des mots clés dans les descriptions et la proximité des dates
        """
        # Récupérer tous les objets
        found_items = self.found_repo.get_all()
        lost_items = self.lost_repo.get_all()
        
        # Pour chaque objet trouvé, chercher des correspondances
        for found_item in found_items:
            # Réinitialiser les correspondances
            found_item.possible_lost_items = []
            
            # Extraire les mots clés de la description (mots de plus de 3 lettres)
            found_keywords = set([
                word.lower() for word in found_item.description.split()
                if len(word) > 3
            ])
            
            # Chercher des correspondances parmi les objets perdus
            for lost_item in lost_items:
                # Extraire les mots clés de la description de l'objet perdu
                lost_keywords = set([
                    word.lower() for word in lost_item.description.split()
                    if len(word) > 3
                ])
                
                # Calculer l'intersection des mots clés
                common_keywords = found_keywords.intersection(lost_keywords)
                
                # Si au moins 2 mots clés en commun, considérer comme une correspondance potentielle
                if len(common_keywords) >= 2:
                    found_item.possible_lost_items.append(lost_item)
        
        # Pour chaque objet perdu, chercher des correspondances
        for lost_item in lost_items:
            # Réinitialiser les correspondances
            lost_item.possible_found_items = []
            
            # Extraire les mots clés de la description
            lost_keywords = set([
                word.lower() for word in lost_item.description.split()
                if len(word) > 3
            ])
            
            # Chercher des correspondances parmi les objets trouvés
            for found_item in found_items:
                # Extraire les mots clés de la description de l'objet trouvé
                found_keywords = set([
                    word.lower() for word in found_item.description.split()
                    if len(word) > 3
                ])
                
                # Calculer l'intersection des mots clés
                common_keywords = lost_keywords.intersection(found_keywords)
                
                # Si au moins 2 mots clés en commun, considérer comme une correspondance potentielle
                if len(common_keywords) >= 2:
                    lost_item.possible_found_items.append(found_item)
        
        self.db.commit()
