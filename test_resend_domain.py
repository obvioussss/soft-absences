#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration Resend avec domaine
"""

import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import User, UserRole
from app.email_service import email_service

load_dotenv()

def check_resend_configuration():
    """Vérifier la configuration Resend actuelle"""
    
    print("=== Vérification Configuration Resend ===")
    
    resend_api_key = os.getenv('RESEND_API_KEY')
    resend_from_email = os.getenv('RESEND_FROM_EMAIL')
    
    print(f"RESEND_API_KEY: {'✅ Configuré' if resend_api_key else '❌ Non configuré'}")
    print(f"RESEND_FROM_EMAIL: {resend_from_email or '❌ Non configuré'}")
    
    if resend_from_email:
        if resend_from_email == "onboarding@resend.dev":
            print("⚠️  Mode test détecté - limitation à hello.obvious@gmail.com")
            print("   Solution : Vérifier un domaine sur Resend")
        elif "resend.dev" in resend_from_email:
            print("⚠️  Domaine Resend de test détecté")
            print("   Solution : Utiliser votre propre domaine vérifié")
        else:
            print("✅ Domaine personnalisé détecté")
            print("   Votre domaine devrait être vérifié sur Resend")
    
    print()

def test_email_to_pierre():
    """Test spécifique pour Pierre"""
    
    print("=== Test d'envoi à Pierre ===")
    
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
            print(f"✅ Email envoyé avec succès à Pierre ({pierre.email})")
            print("Pierre devrait recevoir une notification de confirmation")
        else:
            print(f"❌ Échec de l'envoi à Pierre ({pierre.email})")
            print("\n🔧 Solutions possibles :")
            print("1. Vérifier un domaine sur Resend (recommandé)")
            print("2. Configurer Gmail SMTP temporairement")
            print("3. Vérifier que RESEND_FROM_EMAIL utilise votre domaine vérifié")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
    finally:
        db.close()

def test_email_to_admin():
    """Test d'envoi à l'admin"""
    
    print("\n=== Test d'envoi à l'admin ===")
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    try:
        # Chercher l'admin
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if not admin:
            print("❌ Aucun admin trouvé")
            return
        
        print(f"Admin trouvé: {admin.email}")
        
        # Test notification admin
        success = email_service.send_absence_request_notification(
            admin_emails=[admin.email],
            user_name="Pierre Test",
            absence_type="vacances",
            start_date=str(date.today() + timedelta(days=1)),
            end_date=str(date.today() + timedelta(days=5)),
            reason="Test notification admin"
        )
        
        if success:
            print(f"✅ Email envoyé avec succès à l'admin ({admin.email})")
        else:
            print(f"❌ Échec de l'envoi à l'admin ({admin.email})")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
    finally:
        db.close()

def show_next_steps():
    """Afficher les prochaines étapes"""
    
    print("\n=== Prochaines étapes ===")
    
    resend_from_email = os.getenv('RESEND_FROM_EMAIL')
    
    if not resend_from_email or resend_from_email == "onboarding@resend.dev":
        print("📋 Configuration Resend avec domaine :")
        print("1. Aller sur [resend.com](https://resend.com)")
        print("2. Cliquer sur 'Domains' dans le menu")
        print("3. Cliquer sur 'Add Domain'")
        print("4. Ajouter votre domaine (ex: soft-absences.com)")
        print("5. Configurer les enregistrements DNS fournis")
        print("6. Attendre la vérification (5-10 minutes)")
        print("7. Mettre à jour RESEND_FROM_EMAIL dans .env")
        print("8. Redémarrer l'application")
        print("\n📖 Guide détaillé : RESEND_DOMAIN_SETUP.md")
    else:
        print("✅ Domaine configuré")
        print("📧 Testez maintenant avec une vraie demande d'absence")

if __name__ == "__main__":
    print("🔍 Diagnostic Configuration Resend")
    print("=" * 40)
    
    check_resend_configuration()
    test_email_to_admin()
    test_email_to_pierre()
    show_next_steps()
    
    print("\n📧 Résumé :")
    print("- Admin : Peut recevoir des emails (hello.obvious@gmail.com)")
    print("- Pierre : Ne peut pas recevoir d'emails (limitation Resend)")
    print("- Solution : Vérifier un domaine sur Resend") 