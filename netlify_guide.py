#!/usr/bin/env python3
"""
Assistant Configuration Netlify + Resend
"""

import webbrowser
import os

def open_netlify():
    """Ouvrir Netlify"""
    print("🌐 Ouverture de Netlify...")
    webbrowser.open("https://netlify.com")

def open_resend_domains():
    """Ouvrir Resend Domains"""
    print("🌐 Ouverture de Resend Domains...")
    webbrowser.open("https://resend.com/domains")

def show_step_1():
    """Étape 1 : Créer un compte Netlify"""
    print("\n" + "="*50)
    print("1️⃣  CRÉER UN COMPTE NETLIFY")
    print("="*50)
    print()
    print("📋 Étapes :")
    print("1. Aller sur https://netlify.com")
    print("2. Cliquer 'Sign up' (avec GitHub, Google, ou email)")
    print("3. Créer un compte gratuit")
    print("4. Confirmer l'email si nécessaire")
    print()
    print("✅ Une fois connecté, dites-moi et je vous guide pour l'étape 2")

def show_step_2():
    """Étape 2 : Créer un site"""
    print("\n" + "="*50)
    print("2️⃣  CRÉER UN SITE (PEUT ÊTRE VIDE)")
    print("="*50)
    print()
    print("📋 Étapes :")
    print("1. Sur le dashboard Netlify, cliquer 'New site from Git'")
    print("2. Choisir 'Deploy manually'")
    print("3. Créer un fichier index.html vide :")
    print("   <html><body><h1>Hello</h1></body></html>")
    print("4. Glisser-déposer ce fichier dans la zone de déploiement")
    print("5. Attendre le déploiement (30 secondes)")
    print()
    print("✅ Une fois le site déployé, dites-moi et je vous guide pour l'étape 3")

def show_step_3():
    """Étape 3 : Obtenir le domaine"""
    print("\n" + "="*50)
    print("3️⃣  OBTENIR VOTRE DOMAINE")
    print("="*50)
    print()
    print("📋 Étapes :")
    print("1. Aller dans 'Site settings' (icône engrenage)")
    print("2. Cliquer 'Domain management'")
    print("3. Votre domaine sera : votre-site-123456.netlify.app")
    print("4. Copier ce domaine")
    print()
    print("✅ Une fois que vous avez votre domaine, dites-moi et je vous guide pour l'étape 4")

def show_step_4():
    """Étape 4 : Configurer DNS"""
    print("\n" + "="*50)
    print("4️⃣  CONFIGURER LES DNS")
    print("="*50)
    print()
    print("📋 Étapes :")
    print("1. Dans 'Site settings' > 'Domain management' > 'DNS'")
    print("2. Cliquer 'Add DNS record'")
    print("3. Ajouter l'enregistrement SPF :")
    print("   - Type : TXT")
    print("   - Name : @ (ou laissez vide)")
    print("   - Value : v=spf1 include:_spf.resend.com ~all")
    print("4. Cliquer 'Save'")
    print()
    print("✅ Une fois l'enregistrement SPF ajouté, dites-moi et je vous guide pour l'étape 5")

def show_step_5():
    """Étape 5 : Ajouter sur Resend"""
    print("\n" + "="*50)
    print("5️⃣  AJOUTER LE DOMAINE SUR RESEND")
    print("="*50)
    print()
    print("📋 Étapes :")
    print("1. Aller sur https://resend.com/domains")
    print("2. Cliquer 'Add Domain'")
    print("3. Entrer votre domaine Netlify (ex: votre-site-123456.netlify.app)")
    print("4. Cliquer 'Add Domain'")
    print("5. Suivre les instructions de vérification")
    print("6. Copier la valeur DKIM fournie par Resend")
    print()
    print("✅ Une fois que vous avez la valeur DKIM, dites-moi et je vous guide pour l'étape 6")

def show_step_6():
    """Étape 6 : Ajouter DKIM"""
    print("\n" + "="*50)
    print("6️⃣  AJOUTER L'ENREGISTREMENT DKIM")
    print("="*50)
    print()
    print("📋 Étapes :")
    print("1. Revenir sur Netlify > 'Site settings' > 'Domain management' > 'DNS'")
    print("2. Cliquer 'Add DNS record'")
    print("3. Ajouter l'enregistrement DKIM :")
    print("   - Type : TXT")
    print("   - Name : resend._domainkey")
    print("   - Value : [coller la valeur DKIM de Resend]")
    print("4. Cliquer 'Save'")
    print()
    print("✅ Une fois l'enregistrement DKIM ajouté, dites-moi et je vous guide pour l'étape 7")

def show_step_7():
    """Étape 7 : Vérifier et configurer"""
    print("\n" + "="*50)
    print("7️⃣  VÉRIFIER ET CONFIGURER")
    print("="*50)
    print()
    print("📋 Étapes :")
    print("1. Revenir sur Resend")
    print("2. Cliquer 'Verify' à côté de votre domaine")
    print("3. Attendre la vérification (5-10 minutes)")
    print("4. Le statut doit passer de 'Pending' à 'Verified'")
    print()
    print("5. Mettre à jour votre fichier .env :")
    print("   RESEND_FROM_EMAIL=noreply@votre-domaine.netlify.app")
    print()
    print("6. Tester la configuration :")
    print("   python3 test_resend_domain.py")
    print()
    print("🎉 Félicitations ! Votre configuration est terminée !")

def main():
    """Fonction principale"""
    print("🚀 Assistant Configuration Netlify + Resend")
    print("="*60)
    print()
    print("Je vais vous guider étape par étape pour configurer Netlify")
    print("avec Resend et pouvoir envoyer des emails à tous vos utilisateurs.")
    print()
    
    while True:
        print("\n📋 Menu :")
        print("1. Étape 1 : Créer un compte Netlify")
        print("2. Étape 2 : Créer un site")
        print("3. Étape 3 : Obtenir le domaine")
        print("4. Étape 4 : Configurer DNS")
        print("5. Étape 5 : Ajouter sur Resend")
        print("6. Étape 6 : Ajouter DKIM")
        print("7. Étape 7 : Vérifier et configurer")
        print("8. Ouvrir Netlify")
        print("9. Ouvrir Resend Domains")
        print("0. Quitter")
        
        choice = input("\nChoisissez une étape (1-9, 0 pour quitter) : ").strip()
        
        if choice == "1":
            show_step_1()
        elif choice == "2":
            show_step_2()
        elif choice == "3":
            show_step_3()
        elif choice == "4":
            show_step_4()
        elif choice == "5":
            show_step_5()
        elif choice == "6":
            show_step_6()
        elif choice == "7":
            show_step_7()
        elif choice == "8":
            open_netlify()
        elif choice == "9":
            open_resend_domains()
        elif choice == "0":
            print("\n👋 Bonne chance avec votre configuration !")
            break
        else:
            print("❌ Choix invalide. Veuillez choisir 1-9 ou 0.")

if __name__ == "__main__":
    main() 