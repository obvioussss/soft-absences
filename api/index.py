from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
import hashlib
from datetime import datetime, timedelta
import base64
import io
import importlib.util

# Ajouter le répertoire api au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def _import_by_path(module_name: str, filename: str):
    try:
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(current_dir, filename))
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        return mod
    except Exception as e:
        print(f"Import dynamique échoué pour {filename}: {e}")
        return None

# Import robustes des dépendances locales
init_db = None
verify_password = None
hash_password = None
get_static_content = None
get_mime_type = None

try:
    from database import init_db as _idb, verify_password as _vp, hash_password as _hp
    from static_files import get_static_content as _gsc, get_mime_type as _gmt
    init_db, verify_password, hash_password = _idb, _vp, _hp
    get_static_content, get_mime_type = _gsc, _gmt
except Exception as e:
    print(f"Erreur import direct: {e}, tentative import dynamique…")
    db_mod = _import_by_path("database", "database.py")
    sf_mod = _import_by_path("static_files", "static_files.py")
    if db_mod is not None:
        init_db = getattr(db_mod, 'init_db', None)
        verify_password = getattr(db_mod, 'verify_password', None)
        hash_password = getattr(db_mod, 'hash_password', None)
    if sf_mod is not None:
        get_static_content = getattr(sf_mod, 'get_static_content', None)
        get_mime_type = getattr(sf_mod, 'get_mime_type', None)

if init_db is None:
    def init_db():
        return None
if verify_password is None:
    def verify_password(password, password_hash):
        return password == "password123"
if hash_password is None:
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
if get_static_content is None:
    def get_static_content(file_path):
        return None
if get_mime_type is None:
    def get_mime_type(file_path):
        return "text/plain"

# Configuration JWT simplifiée
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def json_serial(obj):
    """Helper pour sérialiser les objets datetime en JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def safe_json_dumps(obj):
    """Sérialise un objet en JSON de manière sécurisée"""
    return json.dumps(obj, default=json_serial, ensure_ascii=False)

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
            "exp": (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()
        }
        # Encoder en base64 simple
        payload_str = safe_json_dumps(payload)
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

def get_user_from_auth_header(headers):
    """Extrait l'utilisateur courant depuis l'en-tête Authorization (Bearer)"""
    try:
        auth_header = headers.get('Authorization') if hasattr(headers, 'get') else None
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ', 1)[1]
        payload = verify_token(token)
        if not payload or not payload.get('sub'):
            return None
        email = payload['sub']
        conn = init_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, first_name, last_name, role, annual_leave_days FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "email": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "role": (row[4] or '').lower(),
            "annual_leave_days": row[5] or 25
        }
    except Exception:
        return None

def serve_static_file(self, file_path):
    """Sert un fichier statique en s'appuyant sur api/static_files.py pour refléter exactement le dossier static/ local"""
    try:
        print(f"Tentative de servir le fichier: {file_path}")  # Debug

        # Récupérer via get_static_content généré depuis static/
        result = handle_static_file(file_path)
        if not result:
            print(f"Fichier statique non trouvé via api/static_files.py: {file_path}, tentative de lecture disque...")
            # Fallback: lecture directe depuis le répertoire static/ si présent dans le bundle
            try:
                rel_path = file_path.lstrip('/')
                # Sécurité basique: forcer dans sous-dossier static
                if not rel_path.startswith('static') and file_path != '/favicon.ico':
                    return False
                local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rel_path) if rel_path.startswith('static') else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'favicon.ico')
                with open(local_path, 'rb') as f:
                    content = f.read()
                mime_type = get_mime_type(file_path)
                result = {"content": content, "mime_type": mime_type}
            except Exception as e:
                print(f"Lecture disque échouée pour {file_path}: {e}")
                return False
        content = result["content"]
        mime_type = result["mime_type"]

        print(f"Contenu trouvé, longueur: {len(content)}")  # Debug

        self.send_response(200)
        self.send_header('Content-type', mime_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        # CSP plus permissive pour éviter l'avertissement DevTools tout en restant raisonnable
        self.send_header(
            'Content-Security-Policy',
            "default-src 'self'; "
            "script-src 'self' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "style-src-elem 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
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
    """Liste des utilisateurs (tableau)"""
    try:
        conn = init_db()
        if not conn:
            return {"error": "Base de données non initialisée"}
            
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, first_name, last_name, role FROM users')
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": user[0],
                "email": user[1],
                "first_name": user[2],
                "last_name": user[3],
                "role": (user[4] or '').lower(),
                "is_active": True
            } for user in users
        ]
    except Exception as e:
        return {
            "error": f"Erreur lors de la récupération des utilisateurs: {str(e)}"
        }

def handle_absence_requests(current_user=None):
    """Liste des demandes d'absence (tableau). Si current_user non-admin, filtrer par user_id"""
    try:
        conn = init_db()
        if not conn:
            return {"error": "Base de données non initialisée"}
            
        cursor = conn.cursor()
        if current_user and current_user.get('role') != 'admin':
            cursor.execute('''
                SELECT a.id, a.type, a.start_date, a.end_date, a.status, a.reason,
                       u.first_name, u.last_name, u.email
                FROM absence_requests a
                JOIN users u ON a.user_id = u.id
                WHERE a.user_id = ?
                ORDER BY a.created_at DESC
            ''', (current_user['id'],))
        else:
            cursor.execute('''
                SELECT a.id, a.type, a.start_date, a.end_date, a.status, a.reason,
                       u.first_name, u.last_name, u.email
                FROM absence_requests a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.created_at DESC
            ''')
        absences = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": abs[0],
                "type": (abs[1] or '').lower(),
                "start_date": abs[2],
                "end_date": abs[3],
                "status": (abs[4] or '').lower(),
                "reason": abs[5],
                "user_name": f"{abs[6]} {abs[7]}",
                "user_email": abs[8]
            } for abs in absences
        ]
    except Exception as e:
        return {
            "error": f"Erreur lors de la récupération des absences: {str(e)}"
        }

def to_db_type(front_value: str) -> str:
    return (front_value or '').strip().upper()

def to_db_status(front_value: str) -> str:
    mapping = {
        'en_attente': 'EN_ATTENTE',
        'approuve': 'APPROUVE',
        'refuse': 'REFUSE'
    }
    return mapping.get((front_value or '').lower(), (front_value or '').upper())

def from_db_role(db_value: str) -> str:
    return (db_value or '').lower()

def handle_get_user(user_id: int):
    try:
        conn = init_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, first_name, last_name, role, annual_leave_days, is_active FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {"error": "Utilisateur non trouvé"}
        return {
            "id": row[0],
            "email": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "role": from_db_role(row[4]),
            "annual_leave_days": row[5] or 25,
            "is_active": bool(row[6]) if row[6] is not None else True
        }
    except Exception as e:
        return {"error": str(e)}

def handle_user_absence_summary(user_id: int):
    try:
        from datetime import date
        conn = init_db()
        cursor = conn.cursor()
        cursor.execute('SELECT first_name, last_name, email, annual_leave_days FROM users WHERE id = ?', (user_id,))
        u = cursor.fetchone()
        if not u:
            conn.close()
            return {"error": "Utilisateur non trouvé"}
        # Statistiques basiques
        cursor.execute('SELECT start_date, end_date, type, status, reason, created_at FROM absence_requests WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        total_days = 0
        vacation_days = 0
        sick_days = 0
        pending = 0
        approved = 0
        recent_absences = []
        for r in rows:
            s = date.fromisoformat(r[0]); e = date.fromisoformat(r[1])
            days = (e - s).days + 1
            total_days += days
            if r[2] == 'VACANCES':
                vacation_days += days
            else:
                sick_days += days
            if r[3] == 'EN_ATTENTE':
                pending += 1
            if r[3] == 'APPROUVE':
                approved += 1
            recent_absences.append({
                "type": 'vacances' if r[2]=='VACANCES' else 'maladie',
                "start_date": r[0],
                "end_date": r[1],
                "status": (r[3] or '').lower(),
                "reason": r[4],
                "created_at": r[5]
            })
        summary = {
            "user": {"first_name": u[0], "last_name": u[1], "email": u[2]},
            "total_absence_days": total_days,
            "vacation_days": vacation_days,
            "sick_days": sick_days,
            "pending_requests": pending,
            "approved_requests": approved,
            "recent_absences": recent_absences[:5]
        }
        conn.close()
        return summary
    except Exception as e:
        return {"error": str(e)}

def handle_sickness_list(current_user):
    try:
        conn = init_db()
        cursor = conn.cursor()
        if current_user and current_user.get('role') == 'admin':
            cursor.execute('''
                SELECT s.id, s.start_date, s.end_date, s.description, s.pdf_filename, s.email_sent, s.viewed_by_admin, s.created_at,
                       u.id, u.email, u.first_name, u.last_name
                FROM sickness_declarations s JOIN users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
            ''')
        else:
            cursor.execute('''
                SELECT s.id, s.start_date, s.end_date, s.description, s.pdf_filename, s.email_sent, s.viewed_by_admin, s.created_at,
                       u.id, u.email, u.first_name, u.last_name
                FROM sickness_declarations s JOIN users u ON s.user_id = u.id
                WHERE s.user_id = ?
                ORDER BY s.created_at DESC
            ''', (current_user['id'] if current_user else -1,))
        rows = cursor.fetchall()
        conn.close()
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "start_date": r[1],
                "end_date": r[2],
                "description": r[3],
                "pdf_filename": r[4],
                "email_sent": bool(r[5]),
                "viewed_by_admin": bool(r[6]),
                "created_at": r[7],
                "user": {"id": r[8], "email": r[9], "first_name": r[10], "last_name": r[11]}
            })
        return result
    except Exception as e:
        return {"error": str(e)}

def handle_dashboard(current_user):
    """Gère la route /dashboard pour l'utilisateur courant (format attendu par le frontend)"""
    try:
        if not current_user:
            return {
                "remaining_leave_days": 0,
                "used_leave_days": 0,
                "total_leave_days": 0,
                "pending_requests": 0,
                "approved_requests": 0
            }

        conn = init_db()
        if not conn:
            return {"error": "Base de données non initialisée"}

        cursor = conn.cursor()

        # Requêtes approuvées de type VACANCES pour calculer les jours utilisés
        cursor.execute('''
            SELECT start_date, end_date FROM absence_requests
            WHERE user_id = ? AND status = 'APPROUVE' AND type = 'VACANCES'
        ''', (current_user['id'],))
        approved = cursor.fetchall()

        from datetime import date
        used_days = 0
        for row in approved:
            start = date.fromisoformat(row[0])
            end = date.fromisoformat(row[1])
            used_days += (end - start).days + 1

        # Compter en attente et approuvées
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN status = 'EN_ATTENTE' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'APPROUVE' THEN 1 ELSE 0 END)
            FROM absence_requests WHERE user_id = ?
        ''', (current_user['id'],))
        counts = cursor.fetchone() or (0, 0)

        conn.close()

        total_leave_days = current_user.get('annual_leave_days', 25)
        remaining = max(0, total_leave_days - used_days)

        return {
            "remaining_leave_days": remaining,
            "used_leave_days": used_days,
            "total_leave_days": total_leave_days,
            "pending_requests": counts[0] or 0,
            "approved_requests": counts[1] or 0
        }
    except Exception as e:
        return {"error": f"Erreur lors de la récupération du dashboard: {str(e)}"}

def handle_calendar_admin(year: int, month: int):
    """Retourne les événements du mois pour l'admin"""
    try:
        from datetime import date
        conn = init_db()
        cursor = conn.cursor()

        start_date = date(year, month, 1)
        # dernier jour du mois
        if month == 12:
            from datetime import timedelta
            end_date = date(year, 12, 31)
        else:
            from calendar import monthrange
            end_date = date(year, month, monthrange(year, month)[1])

        # Absences avec jointure utilisateur
        cursor.execute('''
            SELECT a.id, a.type, a.start_date, a.end_date, a.status, a.reason,
                   u.first_name, u.last_name
            FROM absence_requests a
            JOIN users u ON a.user_id = u.id
            WHERE (
                (a.start_date BETWEEN ? AND ?) OR
                (a.end_date BETWEEN ? AND ?) OR
                (a.start_date <= ? AND a.end_date >= ?)
            )
        ''', (start_date, end_date, start_date, end_date, start_date, end_date))
        requests = cursor.fetchall()

        events = []
        for r in requests:
            events.append({
                "id": r[0],
                "title": f"{r[6]} {r[7]} - {'Vacances' if r[1]=='VACANCES' else 'Maladie'}" + (" (En attente)" if r[4]=='EN_ATTENTE' else (" (Refusé)" if r[4]=='REFUSE' else "")),
                "start": str(max(start_date, __import__('datetime').date.fromisoformat(r[2]))),
                "end": str(min(end_date, __import__('datetime').date.fromisoformat(r[3]))),
                "type": (r[1] or '').lower(),
                "status": (r[4] or '').lower(),
                "user_name": f"{r[6]} {r[7]}",
                "reason": r[5],
                "event_source": "absence_request"
            })

        # Déclarations de maladie
        cursor.execute('''
            SELECT s.id, s.start_date, s.end_date, s.description, s.email_sent,
                   u.first_name, u.last_name
            FROM sickness_declarations s
            JOIN users u ON s.user_id = u.id
            WHERE (
                (s.start_date BETWEEN ? AND ?) OR
                (s.end_date BETWEEN ? AND ?) OR
                (s.start_date <= ? AND s.end_date >= ?)
            )
        ''', (start_date, end_date, start_date, end_date, start_date, end_date))
        sicks = cursor.fetchall()
        for s in sicks:
            email_status = " ✉️" if s[4] else " ❌"
            events.append({
                "id": s[0],
                "title": f"{s[5]} {s[6]} - Arrêt maladie{email_status}",
                "start": str(max(start_date, __import__('datetime').date.fromisoformat(s[1]))),
                "end": str(min(end_date, __import__('datetime').date.fromisoformat(s[2]))),
                "type": "maladie",
                "status": "approuve",
                "user_name": f"{s[5]} {s[6]}",
                "reason": s[3],
                "event_source": "sickness_declaration"
            })

        conn.close()
        return events
    except Exception as e:
        return {"error": str(e)}

def handle_calendar_user(year: int, current_user):
    try:
        from datetime import date
        if not current_user:
            return []
        conn = init_db()
        cursor = conn.cursor()
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        cursor.execute('''
            SELECT id, type, start_date, end_date, status, reason
            FROM absence_requests
            WHERE user_id = ? AND (
                (start_date BETWEEN ? AND ?) OR
                (end_date BETWEEN ? AND ?) OR
                (start_date <= ? AND end_date >= ?)
            )
        ''', (current_user['id'], start_date, end_date, start_date, end_date, start_date, end_date))
        rows = cursor.fetchall()

        events = []
        for r in rows:
            events.append({
                "id": r[0],
                "title": ("Vacances" if r[1]=='VACANCES' else 'Maladie') + (" (En attente)" if r[4]=='EN_ATTENTE' else (" (Refusé)" if r[4]=='REFUSE' else "")),
                "start": str(max(start_date, __import__('datetime').date.fromisoformat(r[2]))),
                "end": str(min(end_date, __import__('datetime').date.fromisoformat(r[3]))),
                "type": (r[1] or '').lower(),
                "status": (r[4] or '').lower(),
                "user_name": f"{current_user['first_name']} {current_user['last_name']}",
                "reason": r[5],
                "event_source": "absence_request"
            })

        # Sickness declarations of the user
        cursor.execute('''
            SELECT id, start_date, end_date, description, email_sent
            FROM sickness_declarations
            WHERE user_id = ? AND (
                (start_date BETWEEN ? AND ?) OR
                (end_date BETWEEN ? AND ?) OR
                (start_date <= ? AND end_date >= ?)
            )
        ''', (current_user['id'], start_date, end_date, start_date, end_date, start_date, end_date))
        srows = cursor.fetchall()
        for s in srows:
            email_status = " ✉️" if s[4] else " ❌"
            events.append({
                "id": s[0],
                "title": f"Arrêt maladie{email_status}",
                "start": str(max(start_date, __import__('datetime').date.fromisoformat(s[1]))),
                "end": str(min(end_date, __import__('datetime').date.fromisoformat(s[2]))),
                "type": "maladie",
                "status": "approuve",
                "user_name": f"{current_user['first_name']} {current_user['last_name']}",
                "reason": s[3],
                "event_source": "sickness_declaration"
            })

        conn.close()
        return events
    except Exception as e:
        return {"error": str(e)}

def handle_calendar_summary(year: int, current_user):
    try:
        from datetime import date
        if not current_user:
            return {"year": year, "total_leave_days": 0, "used_leave_days": 0, "remaining_leave_days": 0}
        conn = init_db()
        cursor = conn.cursor()
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        cursor.execute('''
            SELECT start_date, end_date FROM absence_requests
            WHERE user_id = ? AND status = 'APPROUVE' AND type = 'VACANCES'
              AND start_date <= ? AND end_date >= ?
        ''', (current_user['id'], end_date, start_date))
        rows = cursor.fetchall()
        used_days = 0
        for r in rows:
            s = __import__('datetime').date.fromisoformat(r[0])
            e = __import__('datetime').date.fromisoformat(r[1])
            s = max(s, start_date)
            e = min(e, end_date)
            used_days += (e - s).days + 1
        total_leave_days = current_user.get('annual_leave_days', 25)
        remaining = max(0, total_leave_days - used_days)
        conn.close()
        return {
            "year": year,
            "total_leave_days": total_leave_days,
            "used_leave_days": used_days,
            "remaining_leave_days": remaining
        }
    except Exception as e:
        return {"error": str(e)}

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

            # Récupérer le chemin original réécrit par Vercel (si présent)
            original_candidates = [
                self.headers.get('x-vercel-original-path'),
                self.headers.get('x-original-uri'),
                self.headers.get('x-forwarded-uri'),
            ]
            for cand in original_candidates:
                if cand:
                    try:
                        path = urlparse(cand).path or path
                        break
                    except Exception:
                        pass

            # Support de x-now-route-matches (Vercel) pour extraire les groupes capturés
            if path in ['/api/index.py', '/api/index']:
                try:
                    route_matches = self.headers.get('x-now-route-matches') or ''
                    # Format typique: "1=static%2Findex.html&2=..."
                    if route_matches:
                        rm = {k: v[0] for k, v in parse_qs(route_matches).items()}
                        if '1' in rm and rm['1']:
                            # Si la route est /static/(.*) => reconstruire le chemin
                            candidate = '/' + rm['1']
                            candidate = candidate.replace('%2F', '/').replace('%2f', '/')
                            if candidate.startswith('/'):
                                path = candidate
                except Exception:
                    pass

            # Normaliser les trailing slashes ("/users/" -> "/users")
            if path != '/' and path.endswith('/'):
                path = path[:-1]
            
            print(f"Requête reçue: {path}")  # Debug
            
            # Priorité: routes statiques (/, /dashboard, /static/*, assets)
            if path == '/' or path in ['/dashboard', '/dashboard/'] or path.startswith('/static/') or path.endswith('.css') or path.endswith('.js') or path.endswith('.ico'):
                file_path = None
                if path == '/':
                    file_path = '/static/index.html'
                elif path in ['/dashboard', '/dashboard/']:
                    # Servez la SPA principale pour /dashboard aussi
                    file_path = '/static/index.html'
                else:
                    # assets
                    file_path = path
                if serve_static_file(self, file_path):
                    return
                else:
                    # Fallback: si dashboard indisponible, servir l'index
                    if file_path == '/static/dashboard.html':
                        if serve_static_file(self, '/static/index.html'):
                            return
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; style-src-elem 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'")
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"error": "Fichier non trouvé", "path": path, "mapped_path": file_path}
                    self.wfile.write(safe_json_dumps(response).encode('utf-8'))
                    return
            
            # Gérer les routes API principales + motifs dynamiques
            if (
                path in ['/health', '/users', '/absence-requests', '/api/dashboard', '/users/me', '/absence-requests/all', '/calendar/admin', '/calendar/user', '/calendar/summary', '/sickness-declarations']
                or path.startswith('/users/')
                or path.startswith('/sickness-declarations/')
                or path.startswith('/absence-requests/')
            ):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
                
                if path == '/health':
                    response = handle_health_check()
                elif path == '/users':
                    response = handle_users()
                elif path == '/absence-requests':
                    current_user = get_user_from_auth_header(self.headers)
                    response = handle_absence_requests(current_user)
                elif path == '/absence-requests/all':
                    # Pour compat avec le frontend, retourner la même liste
                    response = handle_absence_requests(None)
                elif path == '/api/dashboard':
                    current_user = get_user_from_auth_header(self.headers)
                    response = handle_dashboard(current_user)
                elif path == '/users/me':
                    # Récupérer l'utilisateur depuis le token
                    user_info = get_user_from_auth_header(self.headers)
                    response = user_info or {"error": "Unauthorized"}
                elif path.startswith('/users/'):
                    # /users/{id} or /users/{id}/absence-summary
                    segments = path.strip('/').split('/')
                    response = {"error": "Bad request"}
                    if len(segments) >= 2 and segments[0] == 'users':
                        try:
                            user_id = int(segments[1])
                        except Exception:
                            user_id = 0
                        if user_id > 0 and len(segments) == 3 and segments[2] == 'absence-summary':
                            response = handle_user_absence_summary(user_id)
                        elif user_id > 0 and len(segments) == 2:
                            response = handle_get_user(user_id)
                elif path == '/calendar/admin':
                    # require admin
                    current_user = get_user_from_auth_header(self.headers)
                    if not current_user or current_user.get('role') != 'admin':
                        response = {"error": "Forbidden"}
                    else:
                        params = parse_qs(parsed_url.query)
                        year = int(params.get('year', ['0'])[0])
                        month = int(params.get('month', ['0'])[0])
                        response = handle_calendar_admin(year, month)
                elif path == '/calendar/user':
                    current_user = get_user_from_auth_header(self.headers)
                    params = parse_qs(parsed_url.query)
                    year = int(params.get('year', ['0'])[0])
                    response = handle_calendar_user(year, current_user)
                elif path == '/calendar/summary':
                    current_user = get_user_from_auth_header(self.headers)
                    params = parse_qs(parsed_url.query)
                    year = int(params.get('year', ['0'])[0])
                    response = handle_calendar_summary(year, current_user)
                elif path == '/sickness-declarations':
                    current_user = get_user_from_auth_header(self.headers)
                    response = handle_sickness_list(current_user)
                
                self.wfile.write(safe_json_dumps(response).encode('utf-8'))
                return
            
            # Si non statique: suite du traitement API
                
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
            self.wfile.write(safe_json_dumps(response).encode('utf-8'))
            return

    def do_POST(self):
        """Gérer les requêtes POST (auth, token, etc.)"""
        try:
            # Lire le contenu de la requête
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length)

            content_type = self.headers.get('Content-Type', '')
            data = None

            # Support JSON
            if content_type.startswith('application/json'):
                try:
                    data = json.loads(raw_body.decode('utf-8'))
                except Exception:
                    data = None

            # Support x-www-form-urlencoded
            elif content_type.startswith('application/x-www-form-urlencoded'):
                parsed = parse_qs(raw_body.decode('utf-8'))
                data = {k: v[0] for k, v in parsed.items()}

            # Support multipart/form-data pour OAuth2 FormData
            elif content_type.startswith('multipart/form-data'):
                import cgi
                env = {
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                    'CONTENT_LENGTH': str(content_length)
                }
                fs = cgi.FieldStorage(fp=io.BytesIO(raw_body), headers=self.headers, environ=env)
                data = {key: fs.getvalue(key) for key in fs.keys()} if fs else {}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()

            if self.path == '/auth/login' and isinstance(data, dict):
                response = handle_login(data)
            elif self.path == '/token' and isinstance(data, dict):
                # OAuth2PasswordRequestForm: username, password
                email = data.get('username', '')
                password = data.get('password', '')

                # Vérifier l'utilisateur
                try:
                    conn = init_db()
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, email, first_name, last_name, password_hash, role FROM users WHERE email = ?', (email,))
                    user = cursor.fetchone()
                    conn.close()
                except Exception:
                    user = None

                if user and verify_password(password, user[4]):
                    access_token = create_access_token(
                        data={"sub": user[1], "user_id": user[0], "role": (user[5] or '').lower()}
                    )
                    response = {
                        "access_token": access_token,
                        "token_type": "bearer"
                    }
                else:
                    response = {"error": "Email ou mot de passe incorrect"}
            elif self.path.rstrip('/') == '/absence-requests':
                # Créer une demande d'absence
                current_user = get_user_from_auth_header(self.headers)
                if not current_user:
                    response = {"error": "Unauthorized"}
                else:
                    req = data or {}
                    abs_type = to_db_type(req.get('type'))
                    start_date = req.get('start_date')
                    end_date = req.get('end_date')
                    reason = req.get('reason')
                    if abs_type not in ['VACANCES', 'MALADIE'] or not start_date or not end_date:
                        response = {"error": "Invalid payload"}
                    else:
                        try:
                            conn = init_db()
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO absence_requests (user_id, type, start_date, end_date, reason, status)
                                VALUES (?, ?, ?, ?, ?, 'EN_ATTENTE')
                            ''', (current_user['id'], abs_type, start_date, end_date, reason))
                            conn.commit()
                            new_id = cursor.lastrowid
                            conn.close()
                            response = {
                                "id": new_id,
                                "type": req.get('type'),
                                "start_date": start_date,
                                "end_date": end_date,
                                "reason": reason,
                                "status": "en_attente"
                            }
                        except Exception as e:
                            response = {"error": str(e)}
            elif self.path.rstrip('/') == '/sickness-declarations':
                # Créer une déclaration de maladie (multipart accepté)
                current_user = get_user_from_auth_header(self.headers)
                if not current_user:
                    response = {"error": "Unauthorized"}
                else:
                    start_date = None; end_date = None; description = None
                    if isinstance(data, dict):
                        start_date = data.get('start_date'); end_date = data.get('end_date'); description = data.get('description')
                    if not start_date or not end_date:
                        response = {"error": "Invalid payload"}
                    else:
                        try:
                            conn = init_db()
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO sickness_declarations (user_id, start_date, end_date, description, email_sent, viewed_by_admin)
                                VALUES (?, ?, ?, ?, 1, 0)
                            ''', (current_user['id'], start_date, end_date, description))
                            conn.commit()
                            new_id = cursor.lastrowid
                            conn.close()
                            response = {
                                "id": new_id,
                                "start_date": start_date,
                                "end_date": end_date,
                                "description": description,
                                "email_sent": True,
                                "viewed_by_admin": False,
                                "user": {"id": current_user['id'], "email": current_user['email'], "first_name": current_user['first_name'], "last_name": current_user['last_name']}
                            }
                        except Exception as e:
                            response = {"error": str(e)}
            elif self.path.startswith('/users'):
                # Création utilisateur POST /users
                if self.path.rstrip('/') == '/users':
                    payload = data or {}
                    try:
                        conn = init_db(); cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO users (email, first_name, last_name, password_hash, role)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            payload.get('email'),
                            payload.get('first_name'),
                            payload.get('last_name'),
                            hash_password(payload.get('password') or ''),
                            (payload.get('role') or 'user').upper()
                        ))
                        conn.commit(); new_id = cursor.lastrowid; conn.close()
                        response = {"id": new_id, **{k: payload.get(k) for k in ['email','first_name','last_name','role']}}
                    except Exception as e:
                        response = {"error": str(e)}
            else:
                response = {
                    "error": "Route non trouvée",
                    "path": self.path
                }

        except Exception as e:
            response = {
                "error": "Erreur serveur",
                "message": str(e)
            }

        self.wfile.write(safe_json_dumps(response).encode('utf-8'))
        return

    def do_PUT(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length)
            try:
                data = json.loads(raw_body.decode('utf-8'))
            except Exception:
                data = {}

            path = urlparse(self.path).path
            # Normaliser
            if path != '/' and path.endswith('/'):
                path = path[:-1]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()

            response = {"error": "Route non trouvée"}

            if path.startswith('/absence-requests/') and path.endswith('/status'):
                try:
                    request_id = int(path.split('/')[2])
                except Exception:
                    request_id = 0
                new_status = to_db_status((data or {}).get('status'))
                admin_comment = (data or {}).get('admin_comment')
                try:
                    conn = init_db(); cursor = conn.cursor()
                    cursor.execute('UPDATE absence_requests SET status = ?, admin_comment = ? WHERE id = ?', (new_status, admin_comment, request_id))
                    conn.commit(); conn.close()
                    response = {"id": request_id, "status": (data or {}).get('status'), "admin_comment": admin_comment}
                except Exception as e:
                    response = {"error": str(e)}
            elif path.startswith('/users/'):
                # PUT /users/{id}
                try:
                    user_id = int(path.split('/')[2])
                except Exception:
                    user_id = 0
                payload = data or {}
                try:
                    conn = init_db(); cursor = conn.cursor()
                    if payload.get('password'):
                        cursor.execute('''
                            UPDATE users SET email=?, first_name=?, last_name=?, role=?, password_hash=? WHERE id=?
                        ''', (
                            payload.get('email'), payload.get('first_name'), payload.get('last_name'), (payload.get('role') or 'user').upper(), hash_password(payload.get('password')), user_id
                        ))
                    else:
                        cursor.execute('''
                            UPDATE users SET email=?, first_name=?, last_name=?, role=? WHERE id=?
                        ''', (
                            payload.get('email'), payload.get('first_name'), payload.get('last_name'), (payload.get('role') or 'user').upper(), user_id
                        ))
                    conn.commit(); conn.close()
                    response = {"id": user_id, **{k: payload.get(k) for k in ['email','first_name','last_name','role']}}
                except Exception as e:
                    response = {"error": str(e)}

            self.wfile.write(safe_json_dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(safe_json_dumps({"error": str(e)}).encode('utf-8'))

    def do_DELETE(self):
        try:
            path = urlparse(self.path).path
            if path != '/' and path.endswith('/'):
                path = path[:-1]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()

            response = {"error": "Route non trouvée"}
            if path.startswith('/users/'):
                try:
                    user_id = int(path.split('/')[2])
                except Exception:
                    user_id = 0
                try:
                    conn = init_db(); cursor = conn.cursor()
                    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                    conn.commit(); conn.close()
                    response = {"message": "Utilisateur supprimé"}
                except Exception as e:
                    response = {"error": str(e)}
            self.wfile.write(safe_json_dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(safe_json_dumps({"error": str(e)}).encode('utf-8'))

    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return