from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Settings(BaseSettings):
    # Configuration de la base de données
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/lost_found_db")
    
    # Configuration Cloudinary
    cloudinary_cloud_name: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY", "")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    # Secret pour JWT
    secret_key: str = os.getenv("SECRET_KEY", "secret_key_for_development_only")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 jours
    
    # Mode debug
    debug: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
