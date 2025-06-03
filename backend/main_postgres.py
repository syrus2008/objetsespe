from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
import os
import uuid

from backend.config import get_settings
from backend.database.db import get_db, engine
from backend.database.models import User, FoundItem, LostItem, Base
from backend.database.repositories import UserRepository, FoundItemRepository, LostItemRepository, MatchingService
from backend.services.s3 import s3_service
from backend.services.auth import create_access_token, get_current_user, get_current_admin
from backend.schemas import (
    FoundItemCreate, FoundItemUpdate, FoundItemResponse,
    LostItemCreate, LostItemUpdate, LostItemResponse,
    Token, UserResponse, MessageResponse
)

# Créer les tables dans la base de données
Base.metadata.create_all(bind=engine)

# Obtenir les paramètres de configuration
settings = get_settings()

# Créer l'application FastAPI
app = FastAPI(
    title="API Objets Perdus et Trouvés",
    description="API pour gérer les objets perdus et trouvés lors de festivals",
    version="2.0.0"
)

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Événement de démarrage pour créer un admin par défaut
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    user_repo = UserRepository(db)
    user_repo.create_admin_if_not_exists()
    db.close()

# Endpoints d'authentification
@app.post("/api/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Obtient un token JWT en s'authentifiant avec un nom d'utilisateur et un mot de passe
    """
    user_repo = UserRepository(db)
    user = user_repo.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer un token JWT
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Obtient les informations de l'utilisateur connecté
    """
    return current_user

# Endpoints pour les objets trouvés
@app.get("/api/found", response_model=List[FoundItemResponse])
async def get_found_items(db: Session = Depends(get_db)):
    """
    Obtient la liste des objets trouvés
    """
    repo = FoundItemRepository(db)
    found_items = repo.get_all()
    
    # Formater les possible_matches pour la réponse
    result = []
    for item in found_items:
        item_dict = {
            "id": item.id,
            "description": item.description,
            "found_date": item.found_date,
            "found_time": item.found_time,
            "location": item.location,
            "content_info": item.content_info,
            "image_url": item.image_url,
            "image_filename": item.image_filename,
            "created_at": item.created_at,
            "possible_matches": [match.id for match in item.possible_lost_items]
        }
        result.append(item_dict)
    
    return result

@app.post("/api/found", response_model=FoundItemResponse)
async def create_found_item(
    description: str = Form(...),
    found_date: str = Form(...),
    found_time: str = Form(...),
    location: str = Form(...),
    content_info: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel objet trouvé avec une image
    """
    # Télécharger l'image sur S3
    image_url = await s3_service.upload_file(image)
    
    # Extraire le nom du fichier de l'URL
    image_filename = image_url.split("/")[-1]
    
    # Créer l'objet trouvé
    repo = FoundItemRepository(db)
    found_item = repo.create({
        "description": description,
        "found_date": found_date,
        "found_time": found_time,
        "location": location,
        "content_info": content_info,
        "image_url": image_url,
        "image_filename": image_filename
    })
    
    # Exécuter l'algorithme de correspondance
    matching_service = MatchingService(db)
    matching_service.find_matches()
    
    # Mettre à jour found_item avec les correspondances
    found_item = repo.get_by_id(found_item.id)
    
    # Formater la réponse
    response = {
        "id": found_item.id,
        "description": found_item.description,
        "found_date": found_item.found_date,
        "found_time": found_item.found_time,
        "location": found_item.location,
        "content_info": found_item.content_info,
        "image_url": found_item.image_url,
        "image_filename": found_item.image_filename,
        "created_at": found_item.created_at,
        "possible_matches": [match.id for match in found_item.possible_lost_items]
    }
    
    return response

@app.put("/api/found/{item_id}", response_model=FoundItemResponse)
async def update_found_item(
    item_id: str,
    description: Optional[str] = Form(None),
    found_date: Optional[str] = Form(None),
    found_time: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    content_info: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Met à jour un objet trouvé existant (admin seulement)
    """
    repo = FoundItemRepository(db)
    found_item = repo.get_by_id(item_id)
    
    if not found_item:
        raise HTTPException(status_code=404, detail="Objet trouvé non trouvé")
    
    # Préparer les données pour la mise à jour
    update_data = {}
    if description is not None:
        update_data["description"] = description
    if found_date is not None:
        update_data["found_date"] = found_date
    if found_time is not None:
        update_data["found_time"] = found_time
    if location is not None:
        update_data["location"] = location
    if content_info is not None:
        update_data["content_info"] = content_info
    
    # Si une nouvelle image est fournie, la télécharger sur S3
    if image and image.filename:
        image_url = await s3_service.upload_file(image)
        image_filename = image_url.split("/")[-1]
        update_data["image_url"] = image_url
        update_data["image_filename"] = image_filename
    
    # Mettre à jour l'objet trouvé
    found_item = repo.update(item_id, update_data)
    
    # Exécuter l'algorithme de correspondance
    matching_service = MatchingService(db)
    matching_service.find_matches()
    
    # Mettre à jour found_item avec les correspondances
    found_item = repo.get_by_id(item_id)
    
    # Formater la réponse
    response = {
        "id": found_item.id,
        "description": found_item.description,
        "found_date": found_item.found_date,
        "found_time": found_item.found_time,
        "location": found_item.location,
        "content_info": found_item.content_info,
        "image_url": found_item.image_url,
        "image_filename": found_item.image_filename,
        "created_at": found_item.created_at,
        "possible_matches": [match.id for match in found_item.possible_lost_items]
    }
    
    return response

@app.delete("/api/found/{item_id}", response_model=MessageResponse)
async def delete_found_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Supprime un objet trouvé existant (admin seulement)
    """
    repo = FoundItemRepository(db)
    success = repo.delete(item_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Objet trouvé non trouvé")
    
    return {"detail": "Objet trouvé supprimé avec succès"}

# Endpoints pour les objets perdus
@app.get("/api/lost", response_model=List[LostItemResponse])
async def get_lost_items(db: Session = Depends(get_db)):
    """
    Obtient la liste des objets perdus
    """
    repo = LostItemRepository(db)
    lost_items = repo.get_all()
    
    # Formater les possible_matches pour la réponse
    result = []
    for item in lost_items:
        item_dict = {
            "id": item.id,
            "description": item.description,
            "lost_date": item.lost_date,
            "lost_time": item.lost_time,
            "location": item.location,
            "content_info": item.content_info,
            "created_at": item.created_at,
            "possible_matches": [match.id for match in item.possible_found_items]
        }
        result.append(item_dict)
    
    return result

@app.post("/api/lost", response_model=LostItemResponse)
async def create_lost_item(
    description: str = Form(...),
    lost_date: str = Form(...),
    lost_time: str = Form(...),
    location: str = Form(...),
    content_info: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel objet perdu
    """
    repo = LostItemRepository(db)
    lost_item = repo.create({
        "description": description,
        "lost_date": lost_date,
        "lost_time": lost_time,
        "location": location,
        "content_info": content_info
    })
    
    # Exécuter l'algorithme de correspondance
    matching_service = MatchingService(db)
    matching_service.find_matches()
    
    # Mettre à jour lost_item avec les correspondances
    lost_item = repo.get_by_id(lost_item.id)
    
    # Formater la réponse
    response = {
        "id": lost_item.id,
        "description": lost_item.description,
        "lost_date": lost_item.lost_date,
        "lost_time": lost_item.lost_time,
        "location": lost_item.location,
        "content_info": lost_item.content_info,
        "created_at": lost_item.created_at,
        "possible_matches": [match.id for match in lost_item.possible_found_items]
    }
    
    return response

@app.put("/api/lost/{item_id}", response_model=LostItemResponse)
async def update_lost_item(
    item_id: str,
    description: Optional[str] = Form(None),
    lost_date: Optional[str] = Form(None),
    lost_time: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    content_info: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Met à jour un objet perdu existant (admin seulement)
    """
    repo = LostItemRepository(db)
    lost_item = repo.get_by_id(item_id)
    
    if not lost_item:
        raise HTTPException(status_code=404, detail="Objet perdu non trouvé")
    
    # Préparer les données pour la mise à jour
    update_data = {}
    if description is not None:
        update_data["description"] = description
    if lost_date is not None:
        update_data["lost_date"] = lost_date
    if lost_time is not None:
        update_data["lost_time"] = lost_time
    if location is not None:
        update_data["location"] = location
    if content_info is not None:
        update_data["content_info"] = content_info
    
    # Mettre à jour l'objet perdu
    lost_item = repo.update(item_id, update_data)
    
    # Exécuter l'algorithme de correspondance
    matching_service = MatchingService(db)
    matching_service.find_matches()
    
    # Mettre à jour lost_item avec les correspondances
    lost_item = repo.get_by_id(item_id)
    
    # Formater la réponse
    response = {
        "id": lost_item.id,
        "description": lost_item.description,
        "lost_date": lost_item.lost_date,
        "lost_time": lost_item.lost_time,
        "location": lost_item.location,
        "content_info": lost_item.content_info,
        "created_at": lost_item.created_at,
        "possible_matches": [match.id for match in lost_item.possible_found_items]
    }
    
    return response

@app.delete("/api/lost/{item_id}", response_model=MessageResponse)
async def delete_lost_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Supprime un objet perdu existant (admin seulement)
    """
    repo = LostItemRepository(db)
    success = repo.delete(item_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Objet perdu non trouvé")
    
    return {"detail": "Objet perdu supprimé avec succès"}
