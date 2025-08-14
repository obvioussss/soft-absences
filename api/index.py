"""
Point d'entrée Vercel pour l'application FastAPI
"""
import os
import sys

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer l'application FastAPI principale
from app.main import app

# Vercel utilise cette variable pour servir l'application
handler = app
