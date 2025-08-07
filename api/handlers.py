import json
import os
from datetime import datetime
from .database import init_db, verify_password
from .static_files import get_static_content, get_mime_type

def handle_health_check():
    """Gère la route /health"""
    return {
        "status": "OK", 
        "environment": os.getenv("ENVIRONMENT", "production"),
        "message": "API fonctionnelle",
        "database": "SQLite en mémoire"
    }

def handle_root():
    """Gère la route /"""
    return {
        "message": "Application de gestion des absences", 
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/users", "/absences", "/static/index.html"]
    }

def handle_users():
    """Gère la route /users"""
    conn = init_db()
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

def handle_absences():
    """Gère la route /absences"""
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
    
    return {
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

def handle_login(data):
    """Gère la route /auth/login"""
    email = data.get('email', '')
    password = data.get('password', '')
    
    if not email or not password:
        return {
            "error": "Email et mot de passe requis"
        }
    
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, first_name, last_name, password_hash, role FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[4]):
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
            "token": f"token_{user[0]}_{datetime.now().timestamp()}"
        }
    else:
        return {
            "error": "Email ou mot de passe incorrect"
        }

def handle_static_file(file_path):
    """Gère les fichiers statiques"""
    content = get_static_content(file_path)
    
    if not content:
        return None
    
    return {
        "content": content,
        "mime_type": get_mime_type(file_path)
    }

def handle_route_not_found(path):
    """Gère les routes non trouvées"""
    return {
        "error": "Route non trouvée",
        "path": path,
        "available_routes": ["/", "/health", "/users", "/absences", "/static/index.html"]
    } 