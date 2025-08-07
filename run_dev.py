#!/usr/bin/env python3
"""
Script pour lancer le serveur de développement
"""
import os
import subprocess
import sys

def main():
    # Définir l'environnement de développement
    os.environ["ENVIRONMENT"] = "development"
    
    # Vérifier si le fichier .env existe
    if not os.path.exists(".env"):
        print("⚠️  Fichier .env non trouvé !")
        print("📝 Veuillez créer un fichier .env avec la configuration suivante :")
        print("""
# Base de données
DATABASE_URL=sqlite:///./absences.db
DATABASE_URL_TEST=sqlite:///./test_absences.db

# Sécurité
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration Email (optionnel pour le développement)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=

# Environnement
ENVIRONMENT=development
        """)
        print("❌ Arrêt du serveur. Créez le fichier .env et relancez.")
        sys.exit(1)
    else:
        print("✅ Fichier .env trouvé")
    
    # Créer un admin par défaut
    print("Vérification/création de l'administrateur...")
    subprocess.run([sys.executable, "create_admin.py"])
    
    # Lancer le serveur
    print("Démarrage du serveur de développement...")
    print("🚀 Serveur disponible sur http://localhost:8000")
    print("📖 Documentation API : http://localhost:8000/docs")
    print("🔍 Monitoring : http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Serveur arrêté")

if __name__ == "__main__":
    main()