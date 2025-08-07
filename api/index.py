from http.server import BaseHTTPRequestHandler
import json
import os
from .database import init_db
from .handlers import (
    handle_health_check,
    handle_root,
    handle_users,
    handle_absences,
    handle_login,
    handle_static_file,
    handle_route_not_found
)

def serve_static_file(self, file_path):
    """Sert un fichier statique"""
    try:
        result = handle_static_file(file_path)
        
        if not result:
            return False
            
        # Déterminer le type MIME
        mime_type = result["mime_type"]
        content = result["content"]
        
        self.send_response(200)
        self.send_header('Content-type', mime_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
        return True
        
    except Exception as e:
        print(f"Erreur lors du service du fichier statique {file_path}: {e}")
        return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Gérer les fichiers statiques
            if (self.path.startswith('/static/') or 
                self.path.endswith('.css') or 
                self.path.endswith('.html') or
                self.path == '/' or
                self.path == '/dashboard'):
                
                # Mapper les routes vers les fichiers statiques
                if self.path == '/':
                    file_path = '/static/index.html'
                elif self.path == '/dashboard':
                    file_path = '/static/dashboard.html'
                elif self.path == '/style.css':
                    file_path = '/static/style.css'
                else:
                    file_path = self.path
                
                if serve_static_file(self, file_path):
                    return
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        "error": "Fichier non trouvé",
                        "path": self.path,
                        "mapped_path": file_path
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
                response = handle_health_check()
            elif self.path == '/':
                response = handle_root()
            elif self.path == '/users':
                response = handle_users()
            elif self.path == '/absences':
                response = handle_absences()
            else:
                response = handle_route_not_found(self.path)
                
        except Exception as e:
            response = {
                "error": "Erreur serveur",
                "message": str(e),
                "path": self.path
            }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        return

    def do_POST(self):
        """Gérer les requêtes POST pour l'authentification"""
        try:
            # Lire le contenu de la requête
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parser le JSON
            data = json.loads(post_data.decode('utf-8'))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if self.path == '/auth/login':
                response = handle_login(data)
            else:
                response = {
                    "error": "Route non trouvée",
                    "path": self.path
                }
                
        except json.JSONDecodeError:
            response = {
                "error": "Données JSON invalides"
            }
        except Exception as e:
            response = {
                "error": "Erreur serveur",
                "message": str(e)
            }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        return

    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return 