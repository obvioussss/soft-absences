#!/usr/bin/env python3
"""
API ultra-simplifiée pour l'authentification - évite tous les problèmes d'import
"""
from http.server import BaseHTTPRequestHandler
import json
import hashlib
from datetime import datetime, timedelta
import base64

# Configuration
ADMIN_EMAIL = "hello.obvious@gmail.com"
ADMIN_PASSWORD = "admin123"

def simple_hash(password: str) -> str:
    """Hash simple avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_simple_token(email: str, user_id: int, role: str) -> str:
    """Créer un token simple (pas JWT mais fonctionnel)"""
    data = {
        "sub": email,
        "user_id": user_id,
        "role": role,
        "exp": (datetime.now() + timedelta(hours=24)).isoformat()
    }
    token_data = json.dumps(data)
    token_encoded = base64.b64encode(token_data.encode()).decode()
    return f"token_{token_encoded}"

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        """Gérer uniquement l'authentification"""
        try:
            # Lire le contenu de la requête
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length)
            
            # Parser JSON
            try:
                data = json.loads(raw_body.decode('utf-8'))
            except:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "JSON invalide"}).encode())
                return

            email = data.get('email', '')
            password = data.get('password', '')
            
            # Vérification simple de l'admin
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                token = create_simple_token(email, 1, "ADMIN")
                
                response = {
                    "success": True,
                    "message": "Connexion réussie",
                    "user": {
                        "id": 1,
                        "email": email,
                        "first_name": "Admin",
                        "last_name": "System",
                        "role": "ADMIN"
                    },
                    "access_token": token,
                    "token_type": "bearer"
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                response = {"error": "Email ou mot de passe incorrect"}
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Erreur serveur: {str(e)}"}).encode())

    def do_GET(self):
        """Health check simple"""
        response = {
            "status": "OK",
            "message": "API d'authentification simplifiée",
            "endpoint": "/auth/login"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())