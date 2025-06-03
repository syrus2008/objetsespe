from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import get_settings

settings = get_settings()

# Création de l'engine SQLAlchemy
engine = create_engine(settings.database_url)

# Création d'une session SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fonction pour obtenir une instance de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
