#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur par défaut
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import Base, User, UserRole
from app.auth import get_password_hash

def create_admin_user():
    """Créer un utilisateur administrateur par défaut"""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    try:
        # Vérifier si un admin existe déjà
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if admin_exists:
            print("✅ Un administrateur existe déjà")
            # Mettre à jour l'email de l'admin existant si nécessaire
            if admin_exists.email != "hello.obvious@gmail.com":
                admin_exists.email = "hello.obvious@gmail.com"
                db.commit()
                print("✅ Email de l'administrateur mis à jour vers hello.obvious@gmail.com")
            return
        
        # Créer l'administrateur par défaut
        admin_user = User(
            email="hello.obvious@gmail.com",
            hashed_password=get_password_hash("admin123"),
            first_name="Admin",
            last_name="System",
            role=UserRole.ADMIN,
            is_active=True,
            annual_leave_days=25
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Administrateur créé avec succès")
        print("   Email: hello.obvious@gmail.com")
        print("   Mot de passe: admin123")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'administrateur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()