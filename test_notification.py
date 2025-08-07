#!/usr/bin/env python3
"""
Script de test pour vérifier les notifications email
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

def test_admin_notification():
    """Test l'envoi de notification aux admins"""
    
    print("=== Test de notification admin ===")
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    try:
        # Récupérer tous les admins
        admin_users = db.query(User).filter(User.role == UserRole.ADMIN).all()
        admin_emails = [admin.email for admin in admin_users]
        
        print(f"Admins trouvés: {admin_emails}")
        
        if not admin_emails:
            print("❌ Aucun admin trouvé dans la base de données")
            return
        
        # Simuler une notification de demande d'absence
        user_name = "Pierre Test"
        absence_type = "vacances"
        start_date = str(date.today() + timedelta(days=1))
        end_date = str(date.today() + timedelta(days=5))
        reason = "Test de notification"
        
        print(f"Envoi de notification à: {admin_emails}")
        print(f"Utilisateur: {user_name}")
        print(f"Type: {absence_type}")
        print(f"Dates: {start_date} - {end_date}")
        
        # Envoyer la notification
        success = email_service.send_absence_request_notification(
            admin_emails=admin_emails,
            user_name=user_name,
            absence_type=absence_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        
        if success:
            print("✅ Notification admin envoyée avec succès!")
            print("Vérifiez votre boîte de réception hello.obvious@gmail.com")
        else:
            print("❌ Échec de l'envoi de la notification admin")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
    finally:
        db.close()

def test_user_notification():
    """Test l'envoi de notification aux utilisateurs"""
    
    print("\n=== Test de notification utilisateur ===")
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    try:
        # Récupérer un utilisateur non-admin
        user = db.query(User).filter(User.role != UserRole.ADMIN).first()
        
        if not user:
            print("❌ Aucun utilisateur non-admin trouvé dans la base de données")
            return
        
        print(f"Utilisateur trouvé: {user.email}")
        
        # Simuler une notification de statut
        user_name = f"{user.first_name} {user.last_name}"
        absence_type = "vacances"
        status = "approuve"
        admin_comment = "Test de notification utilisateur"
        
        print(f"Envoi de notification à: {user.email}")
        print(f"Statut: {status}")
        print(f"Commentaire: {admin_comment}")
        
        # Envoyer la notification
        success = email_service.send_absence_status_notification(
            user_email=user.email,
            user_name=user_name,
            absence_type=absence_type,
            status=status,
            admin_comment=admin_comment
        )
        
        if success:
            print("✅ Notification utilisateur envoyée avec succès!")
            print(f"Vérifiez la boîte de réception {user.email}")
        else:
            print("❌ Échec de l'envoi de la notification utilisateur")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Configuration email actuelle:")
    print(f"RESEND_API_KEY: {'Configuré' if os.getenv('RESEND_API_KEY') else 'Non configuré'}")
    print(f"SMTP_USERNAME: {'Configuré' if os.getenv('SMTP_USERNAME') else 'Non configuré'}")
    print()
    
    test_admin_notification()
    test_user_notification()
    
    print("\n=== Test terminé ===") 