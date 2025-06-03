from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

# Table d'association pour les correspondances possibles entre objets perdus et trouvés
possible_matches = Table(
    'possible_matches',
    Base.metadata,
    Column('found_item_id', String, ForeignKey('found_items.id')),
    Column('lost_item_id', String, ForeignKey('lost_items.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username}>"

class FoundItem(Base):
    __tablename__ = 'found_items'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    description = Column(String, index=True)
    found_date = Column(String)
    found_time = Column(String)
    location = Column(String)
    content_info = Column(Text, nullable=True)
    image_filename = Column(String, nullable=True)
    image_url = Column(String, nullable=True)  # URL de l'image sur S3
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec les objets perdus qui pourraient correspondre
    possible_lost_items = relationship(
        "LostItem",
        secondary=possible_matches,
        back_populates="possible_found_items"
    )
    
    def __repr__(self):
        return f"<FoundItem {self.description}>"

class LostItem(Base):
    __tablename__ = 'lost_items'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    description = Column(String, index=True)
    lost_date = Column(String)
    lost_time = Column(String)
    location = Column(String)
    content_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec les objets trouvés qui pourraient correspondre
    possible_found_items = relationship(
        "FoundItem",
        secondary=possible_matches,
        back_populates="possible_lost_items"
    )
    
    def __repr__(self):
        return f"<LostItem {self.description}>"
