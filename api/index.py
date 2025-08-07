from http.server import BaseHTTPRequestHandler
import json
import os
import sqlite3
from datetime import datetime
import mimetypes

# Base de données en mémoire pour Vercel
def init_db():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Créer les tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            role TEXT DEFAULT 'USER',
            is_active BOOLEAN DEFAULT 1,
            annual_leave_days INTEGER DEFAULT 25,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS absence_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'EN_ATTENTE',
            approved_by_id INTEGER,
            admin_comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insérer des données de test
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, first_name, last_name, role) 
        VALUES ('admin@example.com', 'Admin', 'User', 'ADMIN')
    ''')
    
    conn.commit()
    return conn

def get_mime_type(file_path):
    """Détermine le type MIME d'un fichier"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def serve_static_file(self, file_path):
    """Sert un fichier statique"""
    try:
        # Construire le chemin complet
        full_path = os.path.join(os.getcwd(), 'static', file_path.lstrip('/static/'))
        
        if not os.path.exists(full_path):
            return False
            
        with open(full_path, 'rb') as f:
            content = f.read()
            
        # Déterminer le type MIME
        mime_type = get_mime_type(file_path)
        
        self.send_response(200)
        self.send_header('Content-type', mime_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)
        return True
        
    except Exception as e:
        print(f"Erreur lors du service du fichier statique {file_path}: {e}")
        return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Gérer les fichiers statiques
            if self.path.startswith('/static/'):
                if serve_static_file(self, self.path):
                    return
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        "error": "Fichier non trouvé",
                        "path": self.path
                    }
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
            
            # Gérer les routes API
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if self.path == '/health':
                response = {
                    "status": "OK", 
                    "environment": os.getenv("ENVIRONMENT", "production"),
                    "message": "API fonctionnelle",
                    "database": "SQLite en mémoire"
                }
            elif self.path == '/':
                response = {
                    "message": "Application de gestion des absences", 
                    "status": "running",
                    "version": "1.0.0",
                    "endpoints": ["/", "/health", "/users", "/absences", "/static/index.html"]
                }
            elif self.path == '/users':
                conn = init_db()
                cursor = conn.cursor()
                cursor.execute('SELECT id, email, first_name, last_name, role FROM users')
                users = cursor.fetchall()
                conn.close()
                
                response = {
                    "users": [
                        {
                            "id": user[0],
                            "email": user[1],
                            "first_name": user[2],
                            "last_name": user[3],
                            "role": user[4]
                        } for user in users
                    ]
                }
            elif self.path == '/absences':
                conn = init_db()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.id, a.type, a.start_date, a.end_date, a.status, 
                           u.first_name, u.last_name
                    FROM absence_requests a
                    JOIN users u ON a.user_id = u.id
                ''')
                absences = cursor.fetchall()
                conn.close()
                
                response = {
                    "absences": [
                        {
                            "id": abs[0],
                            "type": abs[1],
                            "start_date": abs[2],
                            "end_date": abs[3],
                            "status": abs[4],
                            "user_name": f"{abs[5]} {abs[6]}"
                        } for abs in absences
                    ]
                }
            else:
                response = {
                    "error": "Route non trouvée",
                    "path": self.path,
                    "available_routes": ["/", "/health", "/users", "/absences", "/static/index.html"]
                }
                
        except Exception as e:
            response = {
                "error": "Erreur serveur",
                "message": str(e),
                "path": self.path
            }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        return 