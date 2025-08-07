#!/usr/bin/env python3
"""
Script pour guider la configuration InfinityFree + Resend
"""

import os
import webbrowser
from datetime import datetime

def show_infinityfree_guide():
    """Afficher le guide InfinityFree"""
    
    print("🚀 Configuration InfinityFree + Resend")
    print("=" * 40)
    
    print("\n📋 Étapes à suivre :")
    print()
    
    print("1️⃣  CRÉER UN COMPTE INFINITYFREE")
    print("   - Aller sur : https://infinityfree.net")
    print("   - Cliquer sur 'Sign Up'")
    print("   - Remplir le formulaire")
    print("   - Confirmer l'email")
    print()
    
    print("2️⃣  CRÉER UN DOMAINE")
    print("   - Se connecter au panneau de contrôle")
    print("   - Aller dans 'Domains' > 'Add Domain'")
    print("   - Choisir un nom (ex: soft-absences)")
    print("   - Sélectionner .epizy.com")
    print("   - Créer le domaine")
    print()
    
    print("3️⃣  CONFIGURER LES DNS")
    print("   - Aller dans 'DNS Manager'")
    print("   - Ajouter les enregistrements suivants :")
    print()
    print("   Enregistrement SPF :")
    print("   - Type: TXT")
    print("   - Name: @")
    print("   - Value: v=spf1 include:_spf.resend.com ~all")
    print()
    print("   Enregistrement DKIM (à ajouter après étape 4) :")
    print("   - Type: TXT")
    print("   - Name: resend._domainkey")
    print("   - Value: [valeur fournie par Resend]")
    print()
    
    print("4️⃣  AJOUTER LE DOMAINE SUR RESEND")
    print("   - Aller sur : https://resend.com/domains")
    print("   - Cliquer 'Add Domain'")
    print("   - Entrer votre domaine (ex: soft-absences.epizy.com)")
    print("   - Suivre les instructions de vérification")
    print()
    
    print("5️⃣  CONFIGURER L'APPLICATION")
    print("   - Mettre à jour le fichier .env :")
    print("   - RESEND_FROM_EMAIL=noreply@votre-domaine.epizy.com")
    print()
    
    print("6️⃣  TESTER")
    print("   - python3 test_resend_domain.py")
    print()

def open_infinityfree():
    """Ouvrir InfinityFree dans le navigateur"""
    print("🌐 Ouverture d'InfinityFree...")
    webbrowser.open("https://infinityfree.net")

def open_resend_domains():
    """Ouvrir Resend Domains dans le navigateur"""
    print("🌐 Ouverture de Resend Domains...")
    webbrowser.open("https://resend.com/domains")

def check_current_config():
    """Vérifier la configuration actuelle"""
    print("\n🔍 Configuration actuelle :")
    
    resend_from_email = os.getenv('RESEND_FROM_EMAIL', 'Non configuré')
    print(f"RESEND_FROM_EMAIL: {resend_from_email}")
    
    if resend_from_email == "onboarding@resend.dev":
        print("⚠️  Mode test - besoin d'un domaine vérifié")
    elif "epizy.com" in resend_from_email:
        print("✅ Domaine InfinityFree configuré")
    elif resend_from_email != "Non configuré":
        print("✅ Domaine personnalisé configuré")
    else:
        print("❌ Aucun domaine configuré")

def main():
    """Fonction principale"""
    
    print("🎯 Assistant Configuration InfinityFree + Resend")
    print("=" * 50)
    
    check_current_config()
    
    print("\n" + "=" * 50)
    show_infinityfree_guide()
    
    print("🔗 Liens utiles :")
    print("   - InfinityFree : https://infinityfree.net")
    print("   - Resend Domains : https://resend.com/domains")
    print("   - Guide complet : RESEND_DOMAIN_ALTERNATIVES.md")
    
    print("\n❓ Questions ?")
    print("   - Vérifiez le guide RESEND_DOMAIN_ALTERNATIVES.md")
    print("   - Testez avec python3 test_resend_domain.py")
    print("   - Contactez-moi si vous avez des difficultés")

if __name__ == "__main__":
    main() 