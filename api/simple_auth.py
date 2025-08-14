#!/usr/bin/env python3
"""
API simplifiée pour Vercel - gestion de l'authentification uniquement
"""
import json
import sqlite3
import hashlib
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEFAULT_ADMIN_EMAIL = "hello.obvious@gmail.com"
DEFAULT_ADMIN_PASSWORD = "admin123"

def hash_password(password: str) -> str:
    """Hash simple avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Vérifier un mot de passe"""
    return hash_password(password) == hashed

def init_simple_db():
    """Initialiser une base SQLite simple"""
    db_path = "/tmp/simple_auth.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Créer la table users si elle n'existe pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Créer l'admin par défaut s'il n'existe pas
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', (DEFAULT_ADMIN_EMAIL,))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (email, first_name, last_name, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (DEFAULT_ADMIN_EMAIL, "Admin", "System", hash_password(DEFAULT_ADMIN_PASSWORD), "admin"))
        conn.commit()
    
    return conn

def create_simple_token(email: str) -> str:
    """Créer un token simple (pas JWT)"""
    import base64
    import time
    payload = {
        "email": email,
        "timestamp": int(time.time())
    }
    token_data = json.dumps(payload)
    return base64.b64encode(token_data.encode()).decode()

def handle_login(data):
    """Gérer la connexion"""
    try:
        email = data.get('email', '')
        password = data.get('password', '')
        
        if not email or not password:
            return {"error": "Email et mot de passe requis"}
        
        conn = init_simple_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, first_name, last_name, password_hash, role FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user[4]):
            token = create_simple_token(user[1])
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user[0],
                    "email": user[1],
                    "first_name": user[2],
                    "last_name": user[3],
                    "role": user[5]
                }
            }
        else:
            return {"error": "Email ou mot de passe incorrect"}
            
    except Exception as e:
        return {"error": f"Erreur de connexion: {str(e)}"}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Gérer les requêtes POST"""
        try:
            # Lire le contenu
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length)
            
            # Parser JSON
            try:
                data = json.loads(raw_body.decode('utf-8'))
            except:
                data = {}
            
            # Headers CORS
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # Router simple
            path = urlparse(self.path).path
            
            if path == '/login':
                response = handle_login(data)
            else:
                response = {"error": "Route non trouvée", "path": path}
            
            # Réponse JSON
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {"error": f"Erreur serveur: {str(e)}"}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Gérer CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
    def do_GET(self):
        """Gérer les requêtes GET"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {"message": "API d'authentification simple", "status": "OK"}
        self.wfile.write(json.dumps(response).encode('utf-8'))