#!/usr/bin/env python3
"""
Script de test pour vérifier l'envoi d'emails à tous les utilisateurs
"""

import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import User, UserRole, AbsenceType, AbsenceStatus
from app.email_service import email_service

load_dotenv()

def test_email_to_all_users():
    """Test l'envoi d'emails à tous les utilisateurs"""
    
    print("=== Test d'envoi d'emails à tous les utilisateurs ===")
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    try:
        # Récupérer tous les utilisateurs
        all_users = db.query(User).all()
        
        print(f"Utilisateurs trouvés: {len(all_users)}")
        
        for user in all_users:
            print(f"  - {user.email} ({user.role.value})")
        
        if not all_users:
            print("❌ Aucun utilisateur trouvé dans la base de données")
            return
        
        # Tester l'envoi à chaque utilisateur
        for user in all_users:
            print(f"\n--- Test pour {user.email} ---")
            
            user_name = f"{user.first_name} {user.last_name}"
            
            if user.role == UserRole.ADMIN:
                # Test notification admin
                print("Envoi notification admin...")
                success = email_service.send_absence_request_notification(
                    admin_emails=[user.email],
                    user_name="Pierre Test",
                    absence_type="vacances",
                    start_date=str(date.today() + timedelta(days=1)),
                    end_date=str(date.today() + timedelta(days=5)),
                    reason="Test notification admin"
                )
            else:
                # Test notification utilisateur
                print("Envoi notification utilisateur...")
                success = email_service.send_absence_status_notification(
                    user_email=user.email,
                    user_name=user_name,
                    absence_type="vacances",
                    status="approuve",
                    admin_comment="Test notification utilisateur"
                )
            
            if success:
                print(f"✅ Email envoyé avec succès à {user.email}")
            else:
                print(f"❌ Échec de l'envoi à {user.email}")
                
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
    finally:
        db.close()

def test_specific_user():
    """Test spécifique pour Pierre"""
    
    print("\n=== Test spécifique pour Pierre ===")
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    try:
        # Chercher Pierre
        pierre = db.query(User).filter(User.email == "fautrel.pierre@gmail.com").first()
        
        if not pierre:
            print("❌ Pierre (fautrel.pierre@gmail.com) non trouvé")
            return
        
        print(f"Pierre trouvé: {pierre.first_name} {pierre.last_name}")
        
        # Test notification de statut
        user_name = f"{pierre.first_name} {pierre.last_name}"
        
        print("Envoi notification de confirmation d'approbation...")
        success = email_service.send_absence_status_notification(
            user_email=pierre.email,
            user_name=user_name,
            absence_type="vacances",
            status="approuve",
            admin_comment="Votre demande de vacances a été approuvée !"
        )
        
        if success:
            print(f"✅ Email de confirmation envoyé à Pierre ({pierre.email})")
            print("Pierre devrait recevoir une notification de confirmation")
        else:
            print(f"❌ Échec de l'envoi à Pierre ({pierre.email})")
            print("Vérifiez la configuration email (Gmail SMTP recommandé)")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Configuration email actuelle:")
    print(f"RESEND_API_KEY: {'Configuré' if os.getenv('RESEND_API_KEY') else 'Non configuré'}")
    print(f"SMTP_USERNAME: {'Configuré' if os.getenv('SMTP_USERNAME') else 'Non configuré'}")
    print()
    
    if os.getenv('SMTP_USERNAME'):
        print("✅ Configuration Gmail SMTP détectée")
        print("   Tous les utilisateurs peuvent recevoir des emails")
    elif os.getenv('RESEND_API_KEY'):
        print("⚠️  Configuration Resend détectée")
        print("   Seul hello.obvious@gmail.com peut recevoir des emails")
        print("   Consultez GMAIL_SMTP_SETUP.md pour la configuration Gmail")
    else:
        print("❌ Aucune configuration email détectée")
        print("   Consultez GMAIL_SMTP_SETUP.md pour la configuration")
    
    print()
    
    test_specific_user()
    test_email_to_all_users()
    
    print("\n=== Test terminé ===")
    print("\n📧 Prochaines étapes:")
    print("1. Si vous utilisez Resend, configurez Gmail SMTP temporairement")
    print("2. Vérifiez les boîtes de réception des utilisateurs")
    print("3. Testez une vraie demande d'absence dans l'application") 