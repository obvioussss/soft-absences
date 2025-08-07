import pytest
from datetime import date
from sqlalchemy.orm import Session
from unittest.mock import patch

from app.crud import (
    get_sickness_declaration,
    get_sickness_declarations,
    create_sickness_declaration,
    update_sickness_declaration_file,
    mark_sickness_declaration_email_sent,
    mark_sickness_declaration_viewed
)
from app.models import User, SicknessDeclaration, UserRole
from app.auth import get_password_hash

def test_create_sickness_declaration(db: Session):
    """Test de création d'une déclaration de maladie"""
    # Créer un utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer une déclaration
    from app import schemas
    declaration_data = schemas.SicknessDeclarationCreate(
        start_date=date(2024, 1, 15),
        end_date=date(2024, 1, 17),
        description="Grippe"
    )
    
    declaration = create_sickness_declaration(db, declaration_data, user.id)
    
    assert declaration.user_id == user.id
    assert declaration.start_date == date(2024, 1, 15)
    assert declaration.end_date == date(2024, 1, 17)
    assert declaration.description == "Grippe"
    assert declaration.email_sent == False
    assert declaration.viewed_by_admin == False

def test_get_sickness_declaration(db: Session):
    """Test de récupération d'une déclaration de maladie"""
    # Créer un utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer une déclaration
    declaration = SicknessDeclaration(
        user_id=user.id,
        start_date=date(2024, 1, 15),
        end_date=date(2024, 1, 17),
        description="Grippe"
    )
    db.add(declaration)
    db.commit()
    db.refresh(declaration)
    
    # Récupérer la déclaration
    retrieved = get_sickness_declaration(db, declaration.id)
    
    assert retrieved.id == declaration.id
    assert retrieved.user_id == user.id
    assert retrieved.description == "Grippe"

def test_get_sickness_declarations(db: Session):
    """Test de récupération des déclarations de maladie"""
    # Créer un utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer plusieurs déclarations
    declaration1 = SicknessDeclaration(
        user_id=user.id,
        start_date=date(2024, 1, 15),
        end_date=date(2024, 1, 17),
        description="Grippe"
    )
    
    declaration2 = SicknessDeclaration(
        user_id=user.id,
        start_date=date(2024, 2, 10),
        end_date=date(2024, 2, 12),
        description="Angine"
    )
    
    db.add_all([declaration1, declaration2])
    db.commit()
    
    # Récupérer toutes les déclarations
    declarations = get_sickness_declarations(db, user_id=user.id)
    
    assert len(declarations) == 2
    assert declarations[0].description == "Angine"  # Plus récente en premier
    assert declarations[1].description == "Grippe"

def test_update_sickness_declaration_file(db: Session):
    """Test de mise à jour des informations de fichier"""
    # Créer un utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer une déclaration
    declaration = SicknessDeclaration(
        user_id=user.id,
        start_date=date(2024, 1, 15),
        end_date=date(2024, 1, 17),
        description="Grippe"
    )
    db.add(declaration)
    db.commit()
    db.refresh(declaration)
    
    # Mettre à jour les informations de fichier
    updated = update_sickness_declaration_file(
        db, 
        declaration.id, 
        "certificat.pdf", 
        "/uploads/sickness_declarations/certificat.pdf"
    )
    
    assert updated.pdf_filename == "certificat.pdf"
    assert updated.pdf_path == "/uploads/sickness_declarations/certificat.pdf"

def test_mark_sickness_declaration_email_sent(db: Session):
    """Test de marquage d'une déclaration comme envoyée par email"""
    # Créer un utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer une déclaration
    declaration = SicknessDeclaration(
        user_id=user.id,
        start_date=date(2024, 1, 15),
        end_date=date(2024, 1, 17),
        description="Grippe"
    )
    db.add(declaration)
    db.commit()
    db.refresh(declaration)
    
    # Marquer comme envoyée
    updated = mark_sickness_declaration_email_sent(db, declaration.id)
    
    assert updated.email_sent == True

def test_mark_sickness_declaration_viewed(db: Session):
    """Test de marquage d'une déclaration comme vue par l'admin"""
    # Créer un utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer une déclaration
    declaration = SicknessDeclaration(
        user_id=user.id,
        start_date=date(2024, 1, 15),
        end_date=date(2024, 1, 17),
        description="Grippe"
    )
    db.add(declaration)
    db.commit()
    db.refresh(declaration)
    
    # Marquer comme vue
    updated = mark_sickness_declaration_viewed(db, declaration.id)
    
    assert updated.viewed_by_admin == True

def test_get_sickness_declaration_not_found(db: Session):
    """Test de récupération d'une déclaration inexistante"""
    declaration = get_sickness_declaration(db, 999)
    assert declaration is None

def test_update_sickness_declaration_file_not_found(db: Session):
    """Test de mise à jour d'une déclaration inexistante"""
    updated = update_sickness_declaration_file(db, 999, "test.pdf", "/test.pdf")
    assert updated is None 