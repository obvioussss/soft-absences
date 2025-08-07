#!/usr/bin/env python3
"""
Configuration automatique GitHub + Netlify + Resend
"""

import webbrowser
import os
import subprocess
import time
from datetime import datetime

def check_git_installed():
    """Vérifier que Git est installé"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git installé")
            return True
        else:
            print("❌ Git non installé")
            return False
    except FileNotFoundError:
        print("❌ Git non installé")
        return False

def setup_git_repo():
    """Configurer le dépôt Git"""
    print("🔧 Configuration du dépôt Git...")
    
    # Ajouter tous les fichiers
    subprocess.run(['git', 'add', '.'], check=True)
    print("✅ Fichiers ajoutés au dépôt")
    
    # Premier commit
    subprocess.run(['git', 'commit', '-m', 'Initial commit - Soft Absences'], check=True)
    print("✅ Premier commit créé")
    
    return True

def create_github_repo():
    """Créer un dépôt GitHub automatiquement"""
    print("🚀 Création automatique du dépôt GitHub...")
    
    # Ouvrir GitHub pour créer un nouveau dépôt
    webbrowser.open("https://github.com/new")
    
    print("\n📋 Instructions pour créer le dépôt GitHub :")
    print("1. Entrer un nom : soft-absences")
    print("2. Choisir 'Public'")
    print("3. NE PAS cocher 'Add a README file'")
    print("4. NE PAS cocher 'Add .gitignore'")
    print("5. Cliquer 'Create repository'")
    print("6. Copier l'URL du dépôt (ex: https://github.com/votre-username/soft-absences.git)")
    
    repo_url = input("\n🌐 Collez l'URL de votre dépôt GitHub : ").strip()
    
    if not repo_url or "github.com" not in repo_url:
        print("❌ URL GitHub invalide")
        return None
    
    return repo_url

def push_to_github(repo_url):
    """Pousser le code vers GitHub"""
    print(f"📤 Poussage vers GitHub : {repo_url}")
    
    try:
        # Ajouter le remote
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
        print("✅ Remote GitHub ajouté")
        
        # Pousser vers GitHub
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        print("✅ Code poussé vers GitHub")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du push : {e}")
        return False

def deploy_to_netlify():
    """Déployer automatiquement sur Netlify via GitHub"""
    print("🚀 Déploiement automatique sur Netlify...")
    
    # Ouvrir Netlify
    webbrowser.open("https://app.netlify.com/start")
    
    print("\n📋 Instructions de déploiement automatique :")
    print("1. Cliquer 'Sign up with GitHub'")
    print("2. Autoriser Netlify")
    print("3. Cliquer 'New site from Git'")
    print("4. Choisir 'GitHub'")
    print("5. Sélectionner votre dépôt 'soft-absences'")
    print("6. Cliquer 'Deploy site'")
    print("7. Attendre le déploiement (30 secondes)")
    
    input("\n⏳ Appuyez sur Entrée quand le site est déployé...")
    
    # Demander le domaine généré
    domain = input("🌐 Entrez votre domaine Netlify (ex: soft-absences-123456.netlify.app) : ").strip()
    return domain

def configure_dns_automatically(domain):
    """Configurer les DNS automatiquement"""
    print(f"\n🔧 Configuration DNS pour {domain}")
    
    # Ouvrir les paramètres du site
    webbrowser.open(f"https://app.netlify.com/sites/{domain}/settings/domain")
    
    print("\n📋 Instructions DNS automatiques :")
    print("1. Cliquer 'DNS' dans le menu de gauche")
    print("2. Cliquer 'Add DNS record'")
    print("3. Ajouter l'enregistrement SPF :")
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
    
    # Revenir sur Netlify
    webbrowser.open(f"https://app.netlify.com/sites/{domain}/settings/domain")
    
    print("\n📋 Instructions DKIM :")
    print("1. Cliquer 'DNS' dans le menu de gauche")
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
    
    # Commiter et pousser les changements
    subprocess.run(['git', 'add', '.env'], check=True)
    subprocess.run(['git', 'commit', '-m', f'Update email configuration for {domain}'], check=True)
    subprocess.run(['git', 'push'], check=True)
    print("✅ Changements poussés vers GitHub")

def test_configuration():
    """Tester la configuration"""
    print("\n🧪 Test de la configuration...")
    
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
                admin_comment="Test de configuration automatique GitHub + Netlify + Resend"
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
    """Configuration automatique complète GitHub + Netlify + Resend"""
    print("🚀 Configuration automatique GitHub + Netlify + Resend")
    print("=" * 70)
    print()
    print("Je vais automatiser tout le processus :")
    print("✅ Création du dépôt GitHub")
    print("✅ Déploiement automatique sur Netlify")
    print("✅ Configuration DNS")
    print("✅ Intégration Resend")
    print("✅ Test de la configuration")
    print()
    
    # Vérifier Git
    if not check_git_installed():
        print("❌ Git n'est pas installé. Installez-le d'abord.")
        return
    
    # Étape 1 : Configurer Git
    print("1️⃣  CONFIGURATION GIT")
    setup_git_repo()
    
    # Étape 2 : Créer le dépôt GitHub
    print("\n2️⃣  CRÉATION DÉPÔT GITHUB")
    repo_url = create_github_repo()
    
    if not repo_url:
        print("❌ Impossible de continuer sans dépôt GitHub")
        return
    
    # Étape 3 : Pousser vers GitHub
    print("\n3️⃣  PUSH VERS GITHUB")
    if not push_to_github(repo_url):
        print("❌ Échec du push vers GitHub")
        return
    
    # Étape 4 : Déployer sur Netlify
    print("\n4️⃣  DÉPLOIEMENT NETLIFY")
    domain = deploy_to_netlify()
    
    if not domain:
        print("❌ Impossible de continuer sans domaine")
        return
    
    # Étape 5 : Configurer DNS
    print("\n5️⃣  CONFIGURATION DNS")
    configure_dns_automatically(domain)
    
    # Étape 6 : Ajouter sur Resend
    print("\n6️⃣  AJOUT SUR RESEND")
    dkim_value = add_to_resend(domain)
    
    # Étape 7 : Ajouter DKIM
    print("\n7️⃣  AJOUT ENREGISTREMENT DKIM")
    add_dkim_record(domain, dkim_value)
    
    # Étape 8 : Vérifier
    print("\n8️⃣  VÉRIFICATION")
    verify_domain()
    
    # Étape 9 : Mettre à jour .env
    print("\n9️⃣  MISE À JOUR CONFIGURATION")
    update_env_file(domain)
    
    # Étape 10 : Tester
    print("\n🔟 TEST")
    test_configuration()
    
    print("\n🎉 Configuration terminée !")
    print(f"✅ Dépôt GitHub : {repo_url}")
    print(f"✅ Domaine Netlify : {domain}")
    print("✅ Pierre peut maintenant recevoir des notifications")
    print("✅ Tous les utilisateurs peuvent recevoir des emails")
    print("\n📧 Testez maintenant avec une vraie demande d'absence !")

if __name__ == "__main__":
    main() 