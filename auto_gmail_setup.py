#!/usr/bin/env python3
"""
Configuration automatique Gmail SMTP (Solution de secours)
"""

import webbrowser
import os

def setup_gmail_smtp():
    """Configurer Gmail SMTP automatiquement"""
    print("🚀 Configuration automatique Gmail SMTP")
    print("=" * 50)
    print()
    print("Cette solution vous permettra d'envoyer des emails à tous les utilisateurs")
    print("sans avoir besoin de configurer un domaine.")
    print()
    
    # Étape 1 : Activer la validation en 2 étapes
    print("1️⃣  ACTIVER LA VALIDATION EN 2 ÉTAPES")
    webbrowser.open("https://myaccount.google.com/security")
    
    print("\n📋 Instructions :")
    print("1. Aller dans 'Validation en 2 étapes'")
    print("2. Cliquer 'Commencer'")
    print("3. Suivre les étapes pour activer")
    print("4. Confirmer avec votre mot de passe")
    
    input("\n⏳ Appuyez sur Entrée quand la validation en 2 étapes est activée...")
    
    # Étape 2 : Générer un mot de passe d'application
    print("\n2️⃣  GÉNÉRER UN MOT DE PASSE D'APPLICATION")
    webbrowser.open("https://myaccount.google.com/apppasswords")
    
    print("\n📋 Instructions :")
    print("1. Sélectionner 'Mail' dans le menu déroulant")
    print("2. Cliquer 'Générer'")
    print("3. Copier le mot de passe de 16 caractères")
    print("4. Le mot de passe commence par 'xxxx'")
    
    app_password = input("\n🔑 Collez le mot de passe d'application : ").strip()
    
    if not app_password or len(app_password) != 16:
        print("❌ Mot de passe invalide. Il doit faire 16 caractères.")
        return
    
    # Étape 3 : Mettre à jour le fichier .env
    print("\n3️⃣  MISE À JOUR AUTOMATIQUE DU FICHIER .ENV")
    
    # Lire le fichier .env actuel
    env_content = ""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.read()
    
    # Préparer le nouveau contenu
    lines = env_content.split("\n")
    new_lines = []
    
    # Variables à configurer
    smtp_config = {
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USERNAME": "hello.obvious@gmail.com",
        "SMTP_PASSWORD": app_password,
        "EMAIL_FROM": "hello.obvious@gmail.com"
    }
    
    # Remplacer ou ajouter les variables SMTP
    smtp_vars_found = set()
    
    for line in lines:
        if line.startswith("SMTP_SERVER="):
            new_lines.append(f"SMTP_SERVER={smtp_config['SMTP_SERVER']}")
            smtp_vars_found.add("SMTP_SERVER")
        elif line.startswith("SMTP_PORT="):
            new_lines.append(f"SMTP_PORT={smtp_config['SMTP_PORT']}")
            smtp_vars_found.add("SMTP_PORT")
        elif line.startswith("SMTP_USERNAME="):
            new_lines.append(f"SMTP_USERNAME={smtp_config['SMTP_USERNAME']}")
            smtp_vars_found.add("SMTP_USERNAME")
        elif line.startswith("SMTP_PASSWORD="):
            new_lines.append(f"SMTP_PASSWORD={smtp_config['SMTP_PASSWORD']}")
            smtp_vars_found.add("SMTP_PASSWORD")
        elif line.startswith("EMAIL_FROM="):
            new_lines.append(f"EMAIL_FROM={smtp_config['EMAIL_FROM']}")
            smtp_vars_found.add("EMAIL_FROM")
        elif line.startswith("RESEND_API_KEY="):
            # Commenter Resend temporairement
            new_lines.append(f"# {line}")
        elif line.startswith("RESEND_FROM_EMAIL="):
            # Commenter Resend temporairement
            new_lines.append(f"# {line}")
        else:
            new_lines.append(line)
    
    # Ajouter les variables manquantes
    for var, value in smtp_config.items():
        if var not in smtp_vars_found:
            new_lines.append(f"{var}={value}")
    
    # Écrire le nouveau contenu
    new_content = "\n".join(new_lines)
    
    with open(".env", "w") as f:
        f.write(new_content)
    
    print("✅ Fichier .env mis à jour automatiquement")
    print("✅ Configuration Gmail SMTP activée")
    print("✅ Configuration Resend temporairement désactivée")
    
    # Étape 4 : Tester la configuration
    print("\n4️⃣  TEST DE LA CONFIGURATION")
    test_gmail_configuration()

def test_gmail_configuration():
    """Tester la configuration Gmail"""
    print("\n🧪 Test de la configuration Gmail SMTP...")
    
    try:
        from app.email_service import email_service
        from app.database import get_db
        from app.models import User
        
        db = next(get_db())
        pierre = db.query(User).filter(User.email == "fautrel.pierre@gmail.com").first()
        
        if pierre:
            print(f"✅ Test d'envoi à Pierre ({pierre.email})...")
            
            success = email_service.send_absence_status_notification(
                user_email=pierre.email,
                user_name=f"{pierre.first_name} {pierre.last_name}",
                absence_type="vacances",
                status="approuve",
                admin_comment="Test de configuration automatique Gmail SMTP"
            )
            
            if success:
                print("🎉 Configuration Gmail réussie !")
                print("✅ Pierre devrait recevoir un email de test")
                print("✅ Tous les utilisateurs peuvent maintenant recevoir des emails")
            else:
                print("❌ Échec de l'envoi. Vérifiez la configuration Gmail.")
        else:
            print("⚠️  Pierre non trouvé dans la base de données")
            
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")

def main():
    """Configuration automatique Gmail SMTP"""
    print("🚀 Configuration automatique Gmail SMTP")
    print("=" * 50)
    print()
    print("Cette solution vous permettra d'envoyer des emails à tous les utilisateurs")
    print("immédiatement, sans avoir besoin de configurer un domaine.")
    print()
    print("⚠️  Vous devrez activer la validation en 2 étapes sur votre compte Gmail")
    print("⚠️  Et générer un mot de passe d'application")
    print()
    
    choice = input("Voulez-vous continuer avec Gmail SMTP ? (o/n) : ").strip().lower()
    
    if choice in ['o', 'oui', 'y', 'yes']:
        setup_gmail_smtp()
    else:
        print("❌ Configuration annulée")
        print("💡 Vous pouvez toujours utiliser Netlify + Resend plus tard")

if __name__ == "__main__":
    main() 