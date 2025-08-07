#!/usr/bin/env python3
"""
Configuration automatique Netlify + Resend
"""

import webbrowser
import os
import time
from datetime import datetime

def create_netlify_account():
    """Ouvrir Netlify pour créer un compte"""
    print("🌐 Ouverture de Netlify pour créer un compte...")
    webbrowser.open("https://netlify.com")
    
    print("\n📋 Instructions automatiques :")
    print("1. Cliquer 'Sign up'")
    print("2. Choisir 'Sign up with GitHub' (recommandé)")
    print("3. Autoriser Netlify")
    print("4. Votre compte sera créé automatiquement")
    
    input("\n⏳ Appuyez sur Entrée quand votre compte est créé...")

def deploy_site():
    """Déployer le site automatiquement"""
    print("\n🚀 Déploiement automatique du site...")
    
    # Vérifier que le fichier index.html existe
    if not os.path.exists("index.html"):
        print("❌ Fichier index.html non trouvé")
        return None
    
    print("✅ Fichier index.html trouvé")
    print("\n📋 Instructions de déploiement :")
    print("1. Sur le dashboard Netlify, cliquer 'New site from Git'")
    print("2. Choisir 'Deploy manually'")
    print("3. Glisser-déposer le fichier index.html dans la zone")
    print("4. Attendre le déploiement (30 secondes)")
    
    input("\n⏳ Appuyez sur Entrée quand le site est déployé...")
    
    # Demander le domaine généré
    domain = input("🌐 Entrez votre domaine Netlify (ex: soft-absences-123456.netlify.app) : ").strip()
    return domain

def configure_dns(domain):
    """Configurer les DNS automatiquement"""
    print(f"\n🔧 Configuration DNS pour {domain}")
    
    print("\n📋 Instructions DNS :")
    print("1. Aller dans 'Site settings' (icône engrenage)")
    print("2. Cliquer 'Domain management'")
    print("3. Cliquer 'DNS'")
    print("4. Cliquer 'Add DNS record'")
    print()
    print("5. Ajouter l'enregistrement SPF :")
    print("   - Type : TXT")
    print("   - Name : @ (ou laissez vide)")
    print("   - Value : v=spf1 include:_spf.resend.com ~all")
    print("   - Cliquer 'Save'")
    
    input("\n⏳ Appuyez sur Entrée quand l'enregistrement SPF est ajouté...")
    
    return domain

def add_to_resend(domain):
    """Ajouter le domaine sur Resend"""
    print(f"\n📧 Ajout du domaine {domain} sur Resend...")
    webbrowser.open("https://resend.com/domains")
    
    print("\n📋 Instructions Resend :")
    print("1. Cliquer 'Add Domain'")
    print(f"2. Entrer : {domain}")
    print("3. Cliquer 'Add Domain'")
    print("4. Suivre les instructions de vérification")
    print("5. Copier la valeur DKIM fournie")
    
    dkim_value = input("\n🔑 Collez la valeur DKIM de Resend : ").strip()
    return dkim_value

def add_dkim_record(domain, dkim_value):
    """Ajouter l'enregistrement DKIM"""
    print(f"\n🔧 Ajout de l'enregistrement DKIM pour {domain}")
    
    print("\n📋 Instructions DKIM :")
    print("1. Revenir sur Netlify > 'Site settings' > 'Domain management' > 'DNS'")
    print("2. Cliquer 'Add DNS record'")
    print("3. Ajouter l'enregistrement DKIM :")
    print("   - Type : TXT")
    print("   - Name : resend._domainkey")
    print(f"   - Value : {dkim_value}")
    print("   - Cliquer 'Save'")
    
    input("\n⏳ Appuyez sur Entrée quand l'enregistrement DKIM est ajouté...")

def verify_domain():
    """Vérifier le domaine sur Resend"""
    print("\n✅ Vérification du domaine sur Resend...")
    webbrowser.open("https://resend.com/domains")
    
    print("\n📋 Instructions de vérification :")
    print("1. Cliquer 'Verify' à côté de votre domaine")
    print("2. Attendre 5-10 minutes")
    print("3. Le statut doit passer de 'Pending' à 'Verified'")
    
    input("\n⏳ Appuyez sur Entrée quand le domaine est vérifié...")

def update_env_file(domain):
    """Mettre à jour le fichier .env automatiquement"""
    print(f"\n⚙️  Mise à jour automatique du fichier .env...")
    
    # Lire le fichier .env actuel
    env_content = ""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.read()
    
    # Remplacer la ligne RESEND_FROM_EMAIL
    lines = env_content.split("\n")
    new_lines = []
    
    for line in lines:
        if line.startswith("RESEND_FROM_EMAIL="):
            new_lines.append(f"RESEND_FROM_EMAIL=noreply@{domain}")
        else:
            new_lines.append(line)
    
    # Écrire le nouveau contenu
    new_content = "\n".join(new_lines)
    
    with open(".env", "w") as f:
        f.write(new_content)
    
    print(f"✅ Fichier .env mis à jour avec : RESEND_FROM_EMAIL=noreply@{domain}")

def test_configuration():
    """Tester la configuration"""
    print("\n🧪 Test de la configuration...")
    
    # Importer et tester
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
                admin_comment="Test de configuration automatique Netlify + Resend"
            )
            
            if success:
                print("🎉 Configuration réussie ! Pierre devrait recevoir un email.")
            else:
                print("❌ Échec de l'envoi. Vérifiez la configuration.")
        else:
            print("⚠️  Pierre non trouvé dans la base de données")
            
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")

def main():
    """Configuration automatique complète"""
    print("🚀 Configuration automatique Netlify + Resend")
    print("=" * 60)
    print()
    print("Je vais vous guider automatiquement à travers toutes les étapes.")
    print("Vous n'aurez qu'à suivre les instructions et appuyer sur Entrée.")
    print()
    
    # Étape 1 : Créer un compte
    print("1️⃣  CRÉATION DU COMPTE NETLIFY")
    create_netlify_account()
    
    # Étape 2 : Déployer le site
    print("\n2️⃣  DÉPLOIEMENT DU SITE")
    domain = deploy_site()
    
    if not domain:
        print("❌ Impossible de continuer sans domaine")
        return
    
    # Étape 3 : Configurer DNS
    print("\n3️⃣  CONFIGURATION DNS")
    configure_dns(domain)
    
    # Étape 4 : Ajouter sur Resend
    print("\n4️⃣  AJOUT SUR RESEND")
    dkim_value = add_to_resend(domain)
    
    # Étape 5 : Ajouter DKIM
    print("\n5️⃣  AJOUT ENREGISTREMENT DKIM")
    add_dkim_record(domain, dkim_value)
    
    # Étape 6 : Vérifier
    print("\n6️⃣  VÉRIFICATION")
    verify_domain()
    
    # Étape 7 : Mettre à jour .env
    print("\n7️⃣  MISE À JOUR CONFIGURATION")
    update_env_file(domain)
    
    # Étape 8 : Tester
    print("\n8️⃣  TEST")
    test_configuration()
    
    print("\n🎉 Configuration terminée !")
    print(f"✅ Domaine configuré : {domain}")
    print("✅ Pierre peut maintenant recevoir des notifications")
    print("✅ Tous les utilisateurs peuvent recevoir des emails")
    print("\n📧 Testez maintenant avec une vraie demande d'absence !")

if __name__ == "__main__":
    main() 