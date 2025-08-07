from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
import hashlib
from datetime import datetime, timedelta
import base64

# Ajouter le répertoire api au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from database import init_db, verify_password, hash_password
    from static_files import get_static_content, get_mime_type
except ImportError as e:
    print(f"Erreur import: {e}")
    # Fallback si les imports relatifs ne fonctionnent pas
    try:
        from .database import init_db, verify_password, hash_password
        from .static_files import get_static_content, get_mime_type
    except ImportError:
        print("Impossible d'importer les modules")
        # Définir des fonctions de fallback
        def init_db():
            return None
        def verify_password(password, password_hash):
            return password == "password123"
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()
        def get_static_content(file_path):
            return None
        def get_mime_type(file_path):
            return "text/plain"

# Configuration JWT simplifiée
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    """Créer un token JWT simplifié"""
    try:
        # Import JWT seulement si disponible
        import jwt
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    except ImportError:
        # Fallback si JWT n'est pas disponible
        payload = {
            "sub": data.get("sub", ""),
            "user_id": data.get("user_id", ""),
            "role": data.get("role", ""),
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        # Encoder en base64 simple
        payload_str = json.dumps(payload)
        encoded = base64.b64encode(payload_str.encode()).decode()
        return f"token_{encoded}"

def verify_token(token: str):
    """Vérifier un token JWT simplifié"""
    try:
        if token.startswith("token_"):
            # Token simplifié
            encoded = token[6:]  # Enlever "token_"
            payload_str = base64.b64decode(encoded).decode()
            payload = json.loads(payload_str)
            
            # Vérifier l'expiration
            exp = datetime.fromisoformat(payload["exp"].replace("Z", "+00:00"))
            if exp < datetime.utcnow():
                return None
            return payload
        else:
            # Token JWT standard
            import jwt
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
    except Exception:
        return None

def serve_static_file(self, file_path):
    """Sert un fichier statique"""
    try:
        print(f"Tentative de servir le fichier: {file_path}")  # Debug
        result = handle_static_file(file_path)
        
        if not result:
            print(f"Fichier statique non trouvé: {file_path}")
            return False
            
        mime_type = result["mime_type"]
        content = result["content"]
        
        print(f"Contenu trouvé, longueur: {len(content)}")  # Debug
        
        self.send_response(200)
        self.send_header('Content-type', mime_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.end_headers()
        
        # Encoder le contenu en UTF-8
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
            
        self.wfile.write(content_bytes)
        print(f"Fichier servi avec succès: {file_path}")  # Debug
        return True
        
    except Exception as e:
        print(f"Erreur lors du service du fichier statique {file_path}: {e}")
        return False

def handle_health_check():
    """Gère la route /health"""
    return {
        "status": "OK", 
        "environment": os.getenv("ENVIRONMENT", "production"),
        "message": "API fonctionnelle",
        "database": "SQLite en mémoire",
        "version": "1.0.0"
    }

def handle_root():
    """Gère la route /"""
    return {
        "message": "Application de gestion des absences", 
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/", "/health", "/auth/login", "/users", "/absence-requests",
            "/dashboard", "/calendar", "/sickness-declarations"
        ]
    }

def handle_users():
    """Gère la route /users"""
    try:
        conn = init_db()
        if not conn:
            return {"error": "Base de données non initialisée"}
            
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, first_name, last_name, role FROM users')
        users = cursor.fetchall()
        conn.close()
        
        return {
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
    except Exception as e:
        return {
            "error": f"Erreur lors de la récupération des utilisateurs: {str(e)}"
        }

def handle_absence_requests():
    """Gère la route /absence-requests"""
    try:
        conn = init_db()
        if not conn:
            return {"error": "Base de données non initialisée"}
            
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.id, a.type, a.start_date, a.end_date, a.status, a.reason,
                   u.first_name, u.last_name, u.email
            FROM absence_requests a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
        ''')
        absences = cursor.fetchall()
        conn.close()
        
        return {
            "absence_requests": [
                {
                    "id": abs[0],
                    "type": abs[1],
                    "start_date": abs[2],
                    "end_date": abs[3],
                    "status": abs[4],
                    "reason": abs[5],
                    "user_name": f"{abs[6]} {abs[7]}",
                    "user_email": abs[8]
                } for abs in absences
            ]
        }
    except Exception as e:
        return {
            "error": f"Erreur lors de la récupération des absences: {str(e)}"
        }

def handle_dashboard():
    """Gère la route /dashboard"""
    try:
        conn = init_db()
        if not conn:
            return {"error": "Base de données non initialisée"}
            
        cursor = conn.cursor()
        
        # Statistiques des absences
        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'EN_ATTENTE' THEN 1 ELSE 0 END) as en_attente,
                   SUM(CASE WHEN status = 'APPROUVE' THEN 1 ELSE 0 END) as approuve,
                   SUM(CASE WHEN status = 'REFUSE' THEN 1 ELSE 0 END) as refuse
            FROM absence_requests
        ''')
        stats = cursor.fetchone()
        
        # Utilisateurs
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "statistics": {
                "total_absences": stats[0] or 0,
                "en_attente": stats[1] or 0,
                "approuve": stats[2] or 0,
                "refuse": stats[3] or 0,
                "total_users": user_count
            }
        }
    except Exception as e:
        return {
            "error": f"Erreur lors de la récupération des statistiques: {str(e)}"
        }

def handle_login(data):
    """Gère la route /auth/login"""
    try:
        email = data.get('email', '')
        password = data.get('password', '')
        
        if not email or not password:
            return {
                "error": "Email et mot de passe requis"
            }
        
        conn = init_db()
        if not conn:
            return {"error": "Base de données non initialisée"}
            
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, first_name, last_name, password_hash, role FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user[4]):
            # Créer un token JWT
            access_token = create_access_token(
                data={"sub": user[1], "user_id": user[0], "role": user[5]}
            )
            
            return {
                "success": True,
                "message": "Connexion réussie",
                "user": {
                    "id": user[0],
                    "email": user[1],
                    "first_name": user[2],
                    "last_name": user[3],
                    "role": user[5]
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
        else:
            return {
                "error": "Email ou mot de passe incorrect"
            }
    except Exception as e:
        return {
            "error": f"Erreur lors de la connexion: {str(e)}"
        }

def handle_static_file(file_path):
    """Gère les fichiers statiques"""
    try:
        content = get_static_content(file_path)
        
        if not content:
            print(f"Contenu non trouvé pour: {file_path}")
            return None
        
        return {
            "content": content,
            "mime_type": get_mime_type(file_path)
        }
    except Exception as e:
        print(f"Erreur lors de la récupération du fichier statique {file_path}: {e}")
        return None

def handle_route_not_found(path):
    """Gère les routes non trouvées"""
    return {
        "error": "Route non trouvée",
        "path": path,
        "available_routes": [
            "/", "/health", "/auth/login", "/users", "/absence-requests",
            "/dashboard", "/calendar", "/sickness-declarations"
        ]
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parser l'URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            print(f"Requête reçue: {path}")  # Debug
            
            # Gérer les fichiers statiques CSS
            if path.endswith('.css'):
                file_path = path
                if serve_static_file(self, file_path):
                    return
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"error": "Fichier CSS non trouvé", "path": path}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
            
            # Gérer les routes API
            if path in ['/health', '/users', '/absence-requests', '/api/dashboard']:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                
                if path == '/health':
                    response = handle_health_check()
                elif path == '/users':
                    response = handle_users()
                elif path == '/absence-requests':
                    response = handle_absence_requests()
                elif path == '/api/dashboard':
                    response = handle_dashboard()
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # Gérer les routes HTML et fichiers statiques
            file_path = None
            if path == '/':
                file_path = '/static/index.html'
            elif path == '/dashboard':
                file_path = '/static/dashboard.html'
            elif path.startswith('/static/'):
                file_path = path
            else:
                # Route non trouvée
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = handle_route_not_found(path)
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # Servir le fichier HTML/statique
            print(f"Tentative de servir: {file_path}")  # Debug
            if serve_static_file(self, file_path):
                print(f"Fichier servi avec succès: {file_path}")  # Debug
                return
            else:
                print(f"Échec du service du fichier: {file_path}")  # Debug
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"error": "Fichier non trouvé", "path": path, "mapped_path": file_path}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
                
        except Exception as e:
            print(f"Erreur dans do_GET: {e}")  # Debug
            response = {
                "error": "Erreur serveur",
                "message": str(e),
                "path": self.path
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
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
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
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
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return 