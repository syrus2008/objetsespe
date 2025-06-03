from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Settings(BaseSettings):
    # Configuration de la base de données
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/lost_found_db")
    
    # Configuration AWS S3
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "eu-west-3")
    s3_bucket_name: str = os.getenv("S3_BUCKET_NAME", "festival-objets-perdus")
    
    # Secret pour JWT
    secret_key: str = os.getenv("SECRET_KEY", "secret_key_for_development_only")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 jours
    
    # Mode debug
    debug: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # Préfixe pour les URLs des objets sur S3
    s3_url_prefix: str = f"https://{os.getenv('S3_BUCKET_NAME', 'festival-objets-perdus')}.s3.{os.getenv('AWS_REGION', 'eu-west-3')}.amazonaws.com/"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
