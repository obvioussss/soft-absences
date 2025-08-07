#!/usr/bin/env python3
"""
Script de test pour vérifier l'envoi d'emails avec Resend
"""

import os
from dotenv import load_dotenv
from app.email_service import EmailService

load_dotenv()

def test_email_sending():
    """Test l'envoi d'emails avec la configuration actuelle"""
    
    print("=== Test d'envoi d'emails ===")
    
    # Créer l'instance du service email
    email_service = EmailService()
    
    # Afficher la configuration
    print(f"Mode Resend activé: {email_service.use_resend}")
    if email_service.use_resend:
        print(f"Email d'expédition Resend: {email_service.resend_from_email}")
        print("✅ Configuration Resend détectée")
    else:
        print(f"Serveur SMTP: {email_service.smtp_server}")
        print(f"Port SMTP: {email_service.smtp_port}")
        print("⚠️  Utilisation du mode SMTP (Gmail)")
    
    # Test d'envoi simple - utiliser l'email autorisé par Resend
    test_email = "hello.obvious@gmail.com"  # Email autorisé par Resend en mode test
    subject = "Test du préfixe dans l'objet"
    body = """
Bonjour,

Ceci est un email de test pour vérifier que le préfixe "Gestion des absences - " est bien ajouté automatiquement dans l'objet.

Si vous recevez cet email avec le préfixe dans l'objet, la fonctionnalité fonctionne correctement !

Cordialement,
Système de gestion des absences
    """
    
    html_body = """
<html>
<body>
    <h2>Test du préfixe dans l'objet</h2>
    <p>Bonjour,</p>
    <p>Ceci est un email de test pour vérifier que le préfixe "Gestion des absences - " est bien ajouté automatiquement dans l'objet.</p>
    <p><strong>Si vous recevez cet email avec le préfixe dans l'objet, la fonctionnalité fonctionne correctement !</strong></p>
    <p>Cordialement,<br>Système de gestion des absences</p>
</body>
</html>
    """
    
    print(f"\nEnvoi d'un email de test à: {test_email}")
    print(f"Sujet original: {subject}")
    print(f"Sujet formaté: {email_service._format_subject(subject)}")
    
    # Envoyer l'email
    success = email_service.send_email(
        to_emails=[test_email],
        subject=subject,
        body=body,
        html_body=html_body
    )
    
    if success:
        print("✅ Email envoyé avec succès!")
        print("Vérifiez votre boîte de réception (et les spams)")
    else:
        print("❌ Échec de l'envoi de l'email")
        print("Vérifiez votre configuration dans le fichier .env")

def test_attachment_email():
    """Test l'envoi d'email avec pièce jointe"""
    
    print("\n=== Test d'envoi d'email avec pièce jointe ===")
    
    email_service = EmailService()
    
    # Créer un fichier de test
    test_file_path = "test_attachment.txt"
    with open(test_file_path, "w") as f:
        f.write("Ceci est un fichier de test pour vérifier l'envoi de pièces jointes avec le préfixe dans l'objet.")
    
    test_email = "hello.obvious@gmail.com"  # Email autorisé par Resend en mode test
    subject = "Test pièce jointe avec préfixe"
    body = """
Bonjour,

Ceci est un test d'envoi d'email avec pièce jointe et vérification du préfixe dans l'objet.

Vous devriez trouver un fichier texte en pièce jointe.

Cordialement,
Système de gestion des absences
    """
    
    print(f"Envoi d'un email avec pièce jointe à: {test_email}")
    print(f"Sujet original: {subject}")
    print(f"Sujet formaté: {email_service._format_subject(subject)}")
    
    # Envoyer l'email avec pièce jointe
    success = email_service.send_email_with_attachment(
        to_emails=[test_email],
        subject=subject,
        body=body,
        attachment_path=test_file_path
    )
    
    # Nettoyer le fichier de test
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    
    if success:
        print("✅ Email avec pièce jointe envoyé avec succès!")
    else:
        print("❌ Échec de l'envoi de l'email avec pièce jointe")

if __name__ == "__main__":
    print("Configuration email actuelle:")
    print(f"RESEND_API_KEY: {'Configuré' if os.getenv('RESEND_API_KEY') else 'Non configuré'}")
    print(f"SMTP_USERNAME: {'Configuré' if os.getenv('SMTP_USERNAME') else 'Non configuré'}")
    print()
    
    print("⚠️  Note: En mode test, Resend n'autorise l'envoi qu'à hello.obvious@gmail.com")
    print("   Pour envoyer à d'autres emails, vous devrez vérifier un domaine sur resend.com")
    print()
    
    test_email_sending()
    test_attachment_email()
    
    print("\n=== Test terminé ===")
    print("Si les tests ont réussi, votre configuration email fonctionne correctement!")
    print("\n📧 Prochaines étapes:")
    print("1. Vérifiez votre boîte de réception hello.obvious@gmail.com")
    print("2. Vérifiez que les sujets commencent par 'Gestion des absences - '")
    print("3. Pour envoyer à d'autres emails, vérifiez un domaine sur resend.com/domains")
    print("4. Mettez à jour RESEND_FROM_EMAIL avec votre domaine vérifié") 