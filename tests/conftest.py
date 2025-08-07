import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Configurer l'environnement de test
os.environ["ENVIRONMENT"] = "test"

from app.main import app
from app.database import get_db
from app.models import Base

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def db():
    """Créer une session de base de données de test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """Créer un client de test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c

@pytest.fixture
def admin_token(client):
    """Créer un admin et retourner son token"""
    # Créer un admin
    admin_data = {
        "email": "admin@test.com",
        "password": "testpassword",
        "first_name": "Admin",
        "last_name": "Test",
        "role": "admin"
    }
    
    # Créer l'admin via l'API (nécessite d'avoir un admin existant, donc on utilise directement la DB)
    from app.database import SessionLocal
    from app import crud, schemas
    
    db = TestingSessionLocal()
    try:
        user = crud.create_user(db, schemas.UserCreate(**admin_data))
        db.commit()
    finally:
        db.close()
    
    # Se connecter
    response = client.post("/token", data={"username": admin_data["email"], "password": admin_data["password"]})
    token = response.json()["access_token"]
    return token

@pytest.fixture
def user_token(client, admin_token):
    """Créer un utilisateur normal et retourner son token"""
    user_data = {
        "email": "user@test.com",
        "password": "testpassword",
        "first_name": "User",
        "last_name": "Test",
        "role": "user"
    }
    
    # Créer l'utilisateur via l'API
    response = client.post(
        "/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Se connecter
    response = client.post("/token", data={"username": user_data["email"], "password": user_data["password"]})
    token = response.json()["access_token"]
    return token 