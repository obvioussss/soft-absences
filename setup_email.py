#!/usr/bin/env python3
"""
Configuration automatique Email - Choix de solution
"""

import os
import sys

def show_menu():
    """Afficher le menu principal"""
    print("🚀 Configuration automatique Email")
    print("=" * 50)
    print()
    print("Choisissez votre solution pour envoyer des emails à tous les utilisateurs :")
    print()
    print("1️⃣  GITHUB + NETLIFY + RESEND (Recommandé)")
    print("   ✅ Déploiement automatique")
    print("   ✅ Configuration complète")
    print("   ✅ Domaine professionnel")
    print("   ⏱️  Temps : 10-15 minutes")
    print()
    print("2️⃣  GMAIL SMTP (Solution de secours)")
    print("   ✅ Configuration immédiate")
    print("   ✅ Pas besoin de domaine")
    print("   ⚠️  Nécessite validation 2 étapes")
    print("   ⏱️  Temps : 5 minutes")
    print()
    print("3️⃣  TESTER LA CONFIGURATION ACTUELLE")
    print("   🔍 Vérifier l'état actuel")
    print("   🧪 Tester l'envoi d'emails")
    print()
    print("0️⃣  QUITTER")
    print()

def run_github_netlify_setup():
    """Lancer la configuration GitHub + Netlify"""
    print("🚀 Lancement de la configuration GitHub + Netlify + Resend...")
    print()
    
    # Importer et exécuter le script GitHub + Netlify
    try:
        from auto_github_netlify import main as github_netlify_main
        github_netlify_main()
    except ImportError:
        print("❌ Erreur : Script GitHub + Netlify non trouvé")
        print("💡 Assurez-vous que auto_github_netlify.py existe")

def run_gmail_setup():
    """Lancer la configuration Gmail"""
    print("🚀 Lancement de la configuration Gmail SMTP...")
    print()
    
    # Importer et exécuter le script Gmail
    try:
        from auto_gmail_setup import main as gmail_main
        gmail_main()
    except ImportError:
        print("❌ Erreur : Script Gmail non trouvé")
        print("💡 Assurez-vous que auto_gmail_setup.py existe")

def test_current_config():
    """Tester la configuration actuelle"""
    print("🔍 Test de la configuration actuelle...")
    print()
    
    try:
        from test_resend_domain import main as test_main
        test_main()
    except ImportError:
        print("❌ Erreur : Script de test non trouvé")
        print("💡 Assurez-vous que test_resend_domain.py existe")

def main():
    """Menu principal"""
    while True:
        show_menu()
        
        choice = input("Choisissez une option (1-3, 0 pour quitter) : ").strip()
        
        if choice == "1":
            print("\n" + "="*50)
            print("🎯 GITHUB + NETLIFY + RESEND")
            print("="*50)
            print()
            print("Cette solution vous donnera :")
            print("✅ Un dépôt GitHub pour votre code")
            print("✅ Déploiement automatique sur Netlify")
            print("✅ Un domaine professionnel (.netlify.app)")
            print("✅ Configuration DNS automatique")
            print("✅ Envoi à tous les utilisateurs")
            print("✅ Pas de limitations")
            print()
            confirm = input("Voulez-vous continuer avec GitHub + Netlify ? (o/n) : ").strip().lower()
            if confirm in ['o', 'oui', 'y', 'yes']:
                run_github_netlify_setup()
            else:
                print("❌ Configuration GitHub + Netlify annulée")
        
        elif choice == "2":
            print("\n" + "="*50)
            print("🎯 GMAIL SMTP")
            print("="*50)
            print()
            print("Cette solution vous donnera :")
            print("✅ Configuration immédiate")
            print("✅ Envoi à tous les utilisateurs")
            print("✅ Pas besoin de domaine")
            print("⚠️  Nécessite validation 2 étapes Gmail")
            print()
            confirm = input("Voulez-vous continuer avec Gmail SMTP ? (o/n) : ").strip().lower()
            if confirm in ['o', 'oui', 'y', 'yes']:
                run_gmail_setup()
            else:
                print("❌ Configuration Gmail annulée")
        
        elif choice == "3":
            print("\n" + "="*50)
            print("🔍 TEST DE LA CONFIGURATION ACTUELLE")
            print("="*50)
            test_current_config()
        
        elif choice == "0":
            print("\n👋 Au revoir !")
            print("💡 Vous pouvez relancer ce script à tout moment")
            break
        
        else:
            print("❌ Choix invalide. Veuillez choisir 1-3 ou 0.")
        
        print("\n" + "="*50)
        input("Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main() 