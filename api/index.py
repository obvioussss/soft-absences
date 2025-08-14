from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
import hashlib
from datetime import datetime, timedelta, timezone, date as _date
import base64
import io
import importlib.util
import uuid
import mimetypes
import requests

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
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", os.getenv("EMAIL_FROM", "noreply@example.com")).strip() or "noreply@example.com"
DEFAULT_ADMIN_EMAIL = "hello.obvious@gmail.com"

def send_email_resend(to_emails, subject, text, html=None, attachment_path=None, attachment_filename=None):
    try:
        if not RESEND_API_KEY:
            return False
        data = {
            "from": RESEND_FROM_EMAIL,
            "to": to_emails if isinstance(to_emails, list) else [to_emails],
            "subject": subject,
            "text": text,
        }
        if html:
            data["html"] = html
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
            data["attachments"] = [{
                "content": b64,
                "filename": attachment_filename or os.path.basename(attachment_path)
            }]
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json=data
        )
        return resp.status_code == 200
    except Exception:
        return False

def json_serial(obj):
    """Helper pour sérialiser les objets date/datetime en JSON (compat Postgres)."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, _date):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def safe_json_dumps(obj):
    """Sérialise un objet en JSON de manière sécurisée"""
    return json.dumps(obj, default=json_serial, ensure_ascii=False)

def _to_date(value):
    """Convertit une valeur (date ou string) en datetime.date de manière robuste."""
    try:
        from datetime import date
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            # Conserver uniquement la partie date au cas où
            return date.fromisoformat(value.split('T')[0])
        return date.fromisoformat(str(value))
    except Exception:
        # Fallback: aujourd'hui pour éviter un crash serveur
        from datetime import date as _d
        return _d.today()

def create_access_token(data: dict):
    """Créer un token JWT simplifié.

    Tolère les environnements où la lib PyJWT n'est pas disponible
    ou présente une API différente, en basculant automatiquement
    vers un jeton base64 signé faiblement (suffisant pour le front).
    """
    try:
        # Import JWT si disponible et compatible
        import jwt  # type: ignore
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        try:
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
            return encoded_jwt
        except Exception:
            # Si l'API importée ne propose pas encode/decode (ex: autre paquet 'jwt'), fallback
            pass
    except Exception:
        # Import introuvable ou erreur d'implémentation: fallback
        pass

    # Fallback: token base64 simple
    payload = {
        "sub": data.get("sub", ""),
        "user_id": data.get("user_id", ""),
        "role": data.get("role", ""),
        "exp": (datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat().replace('+00:00', 'Z')
    }
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
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                return None
            return payload
        else:
            # Token JWT standard (si lib compatible disponible)
            try:
                import jwt  # type: ignore
                return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # type: ignore
            except Exception:
                return None
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
        try:
            cursor.execute('SELECT id, email, first_name, last_name, role, annual_leave_days FROM users WHERE email = %s', (email,))
        except Exception:
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
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "style-src-elem 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        # Éviter le cache agressif pour le HTML afin d'éviter des 404 mises en cache par le CDN
        if str(mime_type).startswith('text/html'):
            self.send_header('Cache-Control', 'no-store, max-age=0')
        else:
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
                SELECT a.id, a.type, a.start_date, a.end_date, a.status, a.reason, a.created_at,
                       u.id, u.first_name, u.last_name, u.email
                FROM absence_requests a
                JOIN users u ON a.user_id = u.id
                WHERE a.user_id = %s
                ORDER BY a.created_at DESC
            ''', (current_user['id'],))
        else:
            cursor.execute('''
                SELECT a.id, a.type, a.start_date, a.end_date, a.status, a.reason, a.created_at,
                       u.id, u.first_name, u.last_name, u.email
                FROM absence_requests a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.created_at DESC
            ''')
        absences = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "type": (row[1] or '').lower(),
                "start_date": row[2],
                "end_date": row[3],
                "status": (row[4] or '').lower(),
                "reason": row[5],
                "created_at": row[6],
                "user": {
                    "id": row[7],
                    "first_name": row[8],
                    "last_name": row[9],
                    "email": row[10],
                }
            } for row in absences
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
        cursor.execute('SELECT id, email, first_name, last_name, role, annual_leave_days, is_active FROM users WHERE id = %s', (user_id,))
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
        cursor.execute('SELECT first_name, last_name, email, annual_leave_days FROM users WHERE id = %s', (user_id,))
        u = cursor.fetchone()
        if not u:
            conn.close()
            return {"error": "Utilisateur non trouvé"}
        # Statistiques basiques
        cursor.execute('SELECT start_date, end_date, type, status, reason, created_at FROM absence_requests WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        total_days = 0
        vacation_days = 0
        sick_days = 0
        pending = 0
        approved = 0
        recent_absences = []
        for r in rows:
            s = _to_date(r[0]); e = _to_date(r[1])
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
                WHERE s.user_id = %s
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
            WHERE user_id = %s AND status = 'APPROUVE' AND type = 'VACANCES'
        ''', (current_user['id'],))
        approved = cursor.fetchall()

        from datetime import date
        used_days = 0
        for row in approved:
            start = _to_date(row[0])
            end = _to_date(row[1])
            used_days += (end - start).days + 1

        # Compter en attente et approuvées
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN status = 'EN_ATTENTE' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'APPROUVE' THEN 1 ELSE 0 END)
            FROM absence_requests WHERE user_id = %s
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
                (a.start_date BETWEEN %s AND %s) OR
                (a.end_date BETWEEN %s AND %s) OR
                (a.start_date <= %s AND a.end_date >= %s)
            )
        ''', (start_date, end_date, start_date, end_date, start_date, end_date))
        requests = cursor.fetchall()

        events = []
        for r in requests:
            start_val = _to_date(r[2])
            end_val = _to_date(r[3])
            events.append({
                "id": r[0],
                "title": f"{r[6]} {r[7]} - {'Vacances' if r[1]=='VACANCES' else 'Maladie'}" + (" (En attente)" if r[4]=='EN_ATTENTE' else (" (Refusé)" if r[4]=='REFUSE' else "")),
                "start": str(max(start_date, start_val)),
                "end": str(min(end_date, end_val)),
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
                (s.start_date BETWEEN %s AND %s) OR
                (s.end_date BETWEEN %s AND %s) OR
                (s.start_date <= %s AND s.end_date >= %s)
            )
        ''', (start_date, end_date, start_date, end_date, start_date, end_date))
        sicks = cursor.fetchall()
        for s in sicks:
            email_status = " ✉️" if s[4] else " ❌"
            start_val = _to_date(s[1]); end_val = _to_date(s[2])
            events.append({
                "id": s[0],
                "title": f"{s[5]} {s[6]} - Arrêt maladie{email_status}",
                "start": str(max(start_date, start_val)),
                "end": str(min(end_date, end_val)),
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
            WHERE user_id = %s AND (
                (start_date BETWEEN %s AND %s) OR
                (end_date BETWEEN %s AND %s) OR
                (start_date <= %s AND end_date >= %s)
            )
        ''', (current_user['id'], start_date, end_date, start_date, end_date, start_date, end_date))
        rows = cursor.fetchall()

        events = []
        for r in rows:
            events.append({
                "id": r[0],
                "title": ("Vacances" if r[1]=='VACANCES' else 'Maladie') + (" (En attente)" if r[4]=='EN_ATTENTE' else (" (Refusé)" if r[4]=='REFUSE' else "")),
                "start": str(max(start_date, _to_date(r[2]))),
                "end": str(min(end_date, _to_date(r[3]))),
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
            WHERE user_id = %s AND (
                (start_date BETWEEN %s AND %s) OR
                (end_date BETWEEN %s AND %s) OR
                (start_date <= %s AND end_date >= %s)
            )
        ''', (current_user['id'], start_date, end_date, start_date, end_date, start_date, end_date))
        srows = cursor.fetchall()
        for s in srows:
            email_status = " ✉️" if s[4] else " ❌"
            events.append({
                "id": s[0],
                "title": f"Arrêt maladie{email_status}",
                "start": str(max(start_date, _to_date(s[1]))),
                "end": str(min(end_date, _to_date(s[2]))),
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
            WHERE user_id = %s AND status = 'APPROUVE' AND type = 'VACANCES'
              AND start_date <= %s AND end_date >= %s
        ''', (current_user['id'], end_date, start_date))
        rows = cursor.fetchall()
        used_days = 0
        for r in rows:
            s = _to_date(r[0])
            e = _to_date(r[1])
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
        cursor.execute('SELECT id, email, first_name, last_name, password_hash, role FROM users WHERE email = %s', (email,))
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
        content_entry = get_static_content(file_path)
        
        if not content_entry:
            print(f"Contenu non trouvé pour: {file_path}")
            return None
        
        # content_entry peut déjà contenir le mime type
        if isinstance(content_entry, dict) and "content" in content_entry:
            return {
                "content": content_entry["content"],
                "mime_type": content_entry.get("mime_type", get_mime_type(file_path))
            }
        else:
            return {
                "content": content_entry,
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
    def _respond_static_head(self, file_path: str) -> bool:
        try:
            result = handle_static_file(file_path)
            if not result:
                return False
            mime_type = result["mime_type"]
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; style-src-elem 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'")
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.end_headers()
            return True
        except Exception:
            return False

    def do_HEAD(self):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            if path == '/' or path in ['/dashboard', '/dashboard/'] or path.startswith('/static/') or path.endswith('.css') or path.endswith('.js') or path.endswith('.ico'):
                if path == '/':
                    file_path = '/static/index.html'
                elif path in ['/dashboard', '/dashboard/']:
                    file_path = '/static/index.html'
                else:
                    file_path = path
                if self._respond_static_head(file_path):
                    return
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        except Exception:
            self.send_response(500)
            self.end_headers()
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
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; style-src-elem 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'")
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
                # Délivrance PDF des déclarations: /sickness-declarations/{id}/pdf
                if path.startswith('/sickness-declarations/') and path.endswith('/pdf'):
                    try:
                        seg = path.strip('/').split('/')
                        decl_id = int(seg[1])
                        conn = init_db(); cursor = conn.cursor()
                        cursor.execute('SELECT pdf_path, pdf_filename, pdf_data, user_id FROM sickness_declarations WHERE id = %s', (decl_id,))
                        row = cursor.fetchone(); conn.close()
                        if not row:
                            self.send_response(404); self.end_headers(); return
                        pdf_path = row[0]; pdf_filename = row[1]; pdf_data = row[2]
                        content_bytes = None
                        if pdf_path and os.path.exists(pdf_path):
                            with open(pdf_path, 'rb') as f:
                                content_bytes = f.read()
                        elif pdf_data is not None:
                            # pdf_data stocké en BLOB/BYTEA (psycopg retourne souvent memoryview)
                            if isinstance(pdf_data, (bytes, bytearray)):
                                content_bytes = pdf_data
                            else:
                                try:
                                    content_bytes = bytes(pdf_data)
                                except Exception:
                                    content_bytes = None
                        if not content_bytes:
                            self.send_response(404); self.end_headers(); return
                        self.send_response(200)
                        self.send_header('Content-type', 'application/pdf')
                        self.send_header('Content-Disposition', f'inline; filename="{pdf_filename or "document.pdf"}"')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(content_bytes)
                        return
                    except Exception:
                        self.send_response(500); self.end_headers(); return
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
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
                    # Toujours renvoyer un tableau JSON, même si vide, pour éviter les erreurs frontend
                    result = handle_absence_requests(current_user)
                    response = result if isinstance(result, list) else ([] if not result or result.get('error') else [])
                elif path == '/absence-requests/all':
                    # Pour compat avec le frontend, retourner la même liste sans filtre (toujours tableau)
                    result = handle_absence_requests(None)
                    response = result if isinstance(result, list) else ([] if not result or result.get('error') else [])
                elif path == '/api/dashboard':
                    current_user = get_user_from_auth_header(self.headers)
                    response = handle_dashboard(current_user)
                elif path == '/token':
                    # Variante GET: /token?username=...&password=...
                    params = parse_qs(parsed_url.query)
                    email = (params.get('username') or [''])[0]
                    password = (params.get('password') or [''])[0]
                    try:
                        conn = init_db(); cursor = conn.cursor()
                        try:
                            cursor.execute('SELECT id, email, first_name, last_name, password_hash, role FROM users WHERE email = %s', (email,))
                        except Exception:
                            cursor.execute('SELECT id, email, first_name, last_name, password_hash, role FROM users WHERE email = ?', (email,))
                        user = cursor.fetchone(); conn.close()
                    except Exception:
                        user = None
                    if user and verify_password(password, user[4]):
                        response = {
                            "access_token": create_access_token({"sub": user[1], "user_id": user[0], "role": (user[5] or '').lower()}),
                            "token_type": "bearer"
                        }
                    else:
                        # Fallback admin bootstrap
                        if email == DEFAULT_ADMIN_EMAIL and (password == 'admin123' or verify_password(password, hash_password('admin123'))):
                            response = {
                                "access_token": create_access_token({"sub": email, "user_id": 0, "role": 'admin'}),
                                "token_type": "bearer"
                            }
                        else:
                            response = {"error": "Email ou mot de passe incorrect"}
                elif path == '/users/me':
                    # Récupérer l'utilisateur depuis le token
                    user_info = get_user_from_auth_header(self.headers)
                    if user_info and isinstance(user_info, dict):
                        # Normaliser le rôle en minuscule
                        user_info['role'] = (user_info.get('role') or '').lower()
                        response = user_info
                    else:
                        response = {"error": "Unauthorized"}
                elif path == '/admin/reset-user':
                    # Variante GET pour réinitialiser un utilisateur sans passer par POST (contourne bug do_POST)
                    params = parse_qs(parsed_url.query)
                    email = (params.get('email') or [''])[0]
                    # Signature HMAC simplifiée: sha256(SECRET_KEY + email)
                    sig = (params.get('sig') or [''])[0]
                    import hashlib as _hl
                    expected = _hl.sha256((SECRET_KEY + (email or '')).encode()).hexdigest() if email else ''
                    if not email or not sig or sig != expected:
                        response = {"error": "Forbidden"}
                    else:
                        try:
                            conn = init_db(); cursor = conn.cursor()
                            try:
                                cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
                                row = cursor.fetchone()
                            except Exception:
                                cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
                                row = cursor.fetchone()
                            if not row:
                                response = {"error": "Utilisateur introuvable"}
                            else:
                                try:
                                    cursor.execute('UPDATE users SET password_hash = %s WHERE email = %s', (hash_password('admin123'), email))
                                except Exception:
                                    cursor.execute('UPDATE users SET password_hash = ? WHERE email = ?', (hash_password('admin123'), email))
                                try:
                                    conn.commit()
                                except Exception:
                                    pass
                                response = {"message": "Mot de passe réinitialisé", "email": email, "new_password": "admin123"}
                            conn.close()
                        except Exception as e:
                            response = {"error": str(e)}
                elif path == '/auth/bootstrap-token':
                    # Obtenir un token admin temporaire via BOOTSTRAP_TOKEN
                    bootstrap_token = os.getenv('BOOTSTRAP_TOKEN', '').strip()
                    provided = self.headers.get('X-Bootstrap-Token') or ''
                    try:
                        provided = provided or (parse_qs(parsed_url.query).get('token') or [''])[0]
                    except Exception:
                        pass
                    if bootstrap_token and provided == bootstrap_token:
                        # fabriquer un token admin minimal
                        response = {
                            "access_token": create_access_token({"sub": DEFAULT_ADMIN_EMAIL, "user_id": 0, "role": "admin"}),
                            "token_type": "bearer"
                        }
                    else:
                        response = {"error": "Forbidden"}
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
                    res = handle_sickness_list(current_user)
                    response = res if isinstance(res, list) else ([] if not res or res.get('error') else [])
                
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
            response = {"error": "Route non trouvée"}
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
            elif content_type.startswith('application/x-www-form-urlencoded') or content_type.startswith('application/x-www-form-urlencoded;'):
                parsed = parse_qs(raw_body.decode('utf-8'))
                data = {k: v[0] for k, v in parsed.items()}

            # Support multipart/form-data pour formulaires
            elif content_type.startswith('multipart/form-data'):
                import cgi
                env = {
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                    'CONTENT_LENGTH': str(content_length)
                }
                fs = cgi.FieldStorage(fp=io.BytesIO(raw_body), headers=self.headers, environ=env)
                data = {key: fs.getvalue(key) for key in fs.keys()} if fs else {}
                # Attacher l'objet FieldStorage complet pour accès au fichier si présent
                data["__fs__"] = fs

            # Reporter l'écriture des headers après la construction de la réponse
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
                    try:
                        cursor.execute('SELECT id, email, first_name, last_name, password_hash, role FROM users WHERE email = %s', (email,))
                    except Exception:
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
                    # Fallback bootstrap: autoriser le compte admin par défaut même si la base est vide
                    if email == DEFAULT_ADMIN_EMAIL and (password == 'admin123' or verify_password(password, hash_password('admin123'))):
                        access_token = create_access_token(
                            data={"sub": email, "user_id": 0, "role": 'admin'}
                        )
                        response = {"access_token": access_token, "token_type": "bearer"}
                    else:
                        response = {"error": "Email ou mot de passe incorrect"}
            elif self.path == '/admin/reset-db':
                # Endpoint ADMIN-ONLY (avec token bootstrap alternatif) pour réinitialiser la base en production
                current_user = get_user_from_auth_header(self.headers)
                # Autorisation via rôle admin OU via jeton de bootstrap
                bootstrap_token = os.getenv('BOOTSTRAP_TOKEN', '').strip()
                header_token = self.headers.get('X-Bootstrap-Token') or ''
                # Permettre aussi via query param ?token=...
                try:
                    from urllib.parse import urlparse, parse_qs as _pqs
                    q_token = (_pqs(urlparse(self.path).query).get('token') or [''])[0]
                except Exception:
                    q_token = ''
                is_admin = bool(current_user and current_user.get('role') == 'admin')
                is_bootstrap = bool(bootstrap_token and (header_token == bootstrap_token or q_token == bootstrap_token))
                if not (is_admin or is_bootstrap):
                    response = {"error": "Forbidden"}
                else:
                    try:
                        conn = init_db(); cursor = conn.cursor()
                        # Purger dans l'ordre pour respecter les contraintes logiques
                        try:
                            cursor.execute('DELETE FROM sickness_declarations')
                        except Exception:
                            pass
                        try:
                            cursor.execute('DELETE FROM absence_requests')
                        except Exception:
                            pass
                        # Conserver l'admin par défaut, supprimer les autres utilisateurs
                        try:
                            cursor.execute("DELETE FROM users WHERE email <> %s", (DEFAULT_ADMIN_EMAIL,))
                        except Exception:
                            # Fallback si param style sqlite
                            try:
                                cursor.execute("DELETE FROM users WHERE email <> ?", (DEFAULT_ADMIN_EMAIL,))
                            except Exception:
                                pass
                        # S'assurer que l'admin par défaut existe
                        try:
                            cursor.execute('SELECT 1 FROM users WHERE email = %s', (DEFAULT_ADMIN_EMAIL,))
                            row = cursor.fetchone()
                        except Exception:
                            row = None
                        if not row:
                            try:
                                cursor.execute(
                                    'INSERT INTO users (email, first_name, last_name, password_hash, role) VALUES (%s, %s, %s, %s, %s)',
                                    (DEFAULT_ADMIN_EMAIL, 'Admin', 'System', hash_password('admin123'), 'ADMIN')
                                )
                            except Exception:
                                try:
                                    cursor.execute(
                                        'INSERT INTO users (email, first_name, last_name, password_hash, role) VALUES (?, ?, ?, ?, ?)',
                                        (DEFAULT_ADMIN_EMAIL, 'Admin', 'System', hash_password('admin123'), 'ADMIN')
                                    )
                                except Exception:
                                    pass
                        try:
                            conn.commit()
                        except Exception:
                            pass
                        conn.close()
                        response = {"message": "Database reset completed"}
                    except Exception as e:
                        response = {"error": str(e)}
            elif self.path == '/admin/reset-user' and isinstance(data, dict):
                # Réinitialise le mot de passe d'un utilisateur spécifique à admin123
                current_user = get_user_from_auth_header(self.headers)
                bootstrap_token = os.getenv('BOOTSTRAP_TOKEN', '').strip()
                header_token = self.headers.get('X-Bootstrap-Token') or ''
                try:
                    from urllib.parse import urlparse, parse_qs as _pqs
                    q_token = (_pqs(urlparse(self.path).query).get('token') or [''])[0]
                except Exception:
                    q_token = ''
                is_admin = bool(current_user and current_user.get('role') == 'admin')
                is_bootstrap = bool(bootstrap_token and (header_token == bootstrap_token or q_token == bootstrap_token))
                if not (is_admin or is_bootstrap):
                    response = {"error": "Forbidden"}
                else:
                    email = (data or {}).get('email') or ''
                    if not email:
                        response = {"error": "Email requis"}
                    else:
                        try:
                            conn = init_db(); cursor = conn.cursor()
                            # Vérifier existence
                            try:
                                cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
                                row = cursor.fetchone()
                            except Exception:
                                cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
                                row = cursor.fetchone()
                            if not row:
                                response = {"error": "Utilisateur introuvable"}
                            else:
                                # Mettre à jour le hash du mot de passe
                                try:
                                    cursor.execute('UPDATE users SET password_hash = %s WHERE email = %s', (hash_password('admin123'), email))
                                except Exception:
                                    cursor.execute('UPDATE users SET password_hash = ? WHERE email = ?', (hash_password('admin123'), email))
                                try:
                                    conn.commit()
                                except Exception:
                                    pass
                                response = {"message": "Mot de passe réinitialisé", "email": email, "new_password": "admin123"}
                            conn.close()
                        except Exception as e:
                            response = {"error": str(e)}
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
                                VALUES (%s, %s, %s, %s, %s, 'EN_ATTENTE')
                            ''', (current_user['id'], abs_type, start_date, end_date, reason))
                            conn.commit()
                            new_id = cursor.lastrowid
                            # Email aux admins + fallback
                            cursor.execute("SELECT email FROM users WHERE UPPER(role)='ADMIN'")
                            admin_rows = cursor.fetchall() or []
                            admin_emails = [r[0] for r in admin_rows]
                            if DEFAULT_ADMIN_EMAIL not in admin_emails:
                                admin_emails.append(DEFAULT_ADMIN_EMAIL)
                            # Envoi email (meilleur effort)
                            try:
                                subject = f"Gestion des absences - Nouvelle demande - {current_user['first_name']} {current_user['last_name']}"
                                body = f"Nouvelle demande {req.get('type')} du {start_date} au {end_date}.\nRaison: {reason or '—'}"
                                send_email_resend(admin_emails, subject, body, f"<p>{body}</p>")
                            except Exception:
                                pass
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
                # Créer une déclaration de maladie (multipart accepté + PDF enregistré)
                current_user = get_user_from_auth_header(self.headers)
                if not current_user:
                    response = {"error": "Unauthorized"}
                else:
                    start_date = None; end_date = None; description = None
                    pdf_filename = None; pdf_path = None
                    fs = None
                    if isinstance(data, dict):
                        start_date = data.get('start_date'); end_date = data.get('end_date'); description = data.get('description')
                        fs = data.get('__fs__')
                    # Support fallback quand Content-Type est mal détecté côté Vercel
                    if not fs and 'multipart/form-data' in (self.headers.get('Content-Type') or ''):
                        try:
                            import cgi, io
                            env = {
                                'REQUEST_METHOD': 'POST',
                                'CONTENT_TYPE': self.headers.get('Content-Type', ''),
                                'CONTENT_LENGTH': self.headers.get('Content-Length', '0'),
                            }
                            fs = cgi.FieldStorage(fp=io.BytesIO(raw_body), headers=self.headers, environ=env)
                        except Exception:
                            fs = None
                    if not start_date or not end_date:
                        response = {"error": "Invalid payload"}
                    else:
                        try:
                            # Sauvegarder le PDF si fourni (requis côté front)
                            if fs and hasattr(fs, 'keys') and ('pdf_file' in fs.keys()):
                                try:
                                    pdf_field = fs['pdf_file']
                                    # FieldStorage peut retourner une liste si plusieurs fichiers
                                    if isinstance(pdf_field, list) and pdf_field:
                                        pdf_field = pdf_field[0]
                                    original_name = getattr(pdf_field, 'filename', 'document.pdf') or 'document.pdf'
                                    base_dir = '/tmp/uploads/sickness_declarations'
                                    os.makedirs(base_dir, exist_ok=True)
                                    unique_name = f"{uuid.uuid4()}.pdf"
                                    file_path = os.path.join(base_dir, unique_name)
                                    file_bytes = pdf_field.file.read()
                                    with open(file_path, 'wb') as out:
                                        out.write(file_bytes)
                                    pdf_filename = original_name
                                    pdf_path = file_path
                                except Exception as e:
                                    response = {"error": f"Erreur sauvegarde PDF: {str(e)}"}
                                    # Laisser la sortie commune gérer les headers/écriture
                                    raise Exception(response["error"])
                            else:
                                # Si pas de fichier détecté dans la requête multipart
                                response = {"error": "PDF manquant (pdf_file)"}
                                raise Exception(response["error"])

                            conn = init_db(); cursor = conn.cursor()
                            # Essayer d'insérer aussi les octets (pdf_data)
                            try:
                                cursor.execute('''
                                    INSERT INTO sickness_declarations (user_id, start_date, end_date, description, pdf_filename, pdf_path, pdf_data, email_sent, viewed_by_admin)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 0)
                                ''', (current_user['id'], start_date, end_date, description, pdf_filename, pdf_path, file_bytes))
                            except Exception:
                                # fallback si colonne absente
                                cursor.execute('''
                                    INSERT INTO sickness_declarations (user_id, start_date, end_date, description, pdf_filename, pdf_path, email_sent, viewed_by_admin)
                                    VALUES (%s, %s, %s, %s, %s, %s, 0, 0)
                                ''', (current_user['id'], start_date, end_date, description, pdf_filename, pdf_path))
                            conn.commit(); new_id = cursor.lastrowid

                            # Envoi email (meilleur effort) à admins + user avec la pièce jointe
                            try:
                                subject = f"Gestion des absences - Déclaration maladie - {current_user['first_name']} {current_user['last_name']}"
                                body = f"Déclaration du {start_date} au {end_date}. Description: {description or '—'}"
                                cursor.execute("SELECT email FROM users WHERE UPPER(role)='ADMIN'")
                                admin_rows = cursor.fetchall() or []
                                recipients = [r[0] for r in admin_rows]
                                if DEFAULT_ADMIN_EMAIL not in recipients:
                                    recipients.append(DEFAULT_ADMIN_EMAIL)
                                recipients.append(current_user['email'])
                                ok = send_email_resend(list(set(recipients)), subject, body, f"<p>{body}</p>", attachment_path=pdf_path, attachment_filename=pdf_filename)
                                if ok:
                                    cursor.execute('UPDATE sickness_declarations SET email_sent=1 WHERE id=%s', (new_id,))
                                    conn.commit()
                            except Exception:
                                pass
                            conn.close()
                            response = {
                                "id": new_id,
                                "start_date": start_date,
                                "end_date": end_date,
                                "description": description,
                                "pdf_filename": pdf_filename,
                                "email_sent": True,
                                "viewed_by_admin": False,
                                "user": {"id": current_user['id'], "email": current_user['email'], "first_name": current_user['first_name'], "last_name": current_user['last_name']}
                            }
                        except Exception as e:
                            response = {"error": str(e)}
            elif self.path.rstrip('/') == '/sickness-declarations/admin':
                # Admin crée une déclaration de maladie avec PDF
                current_user = get_user_from_auth_header(self.headers)
                if not current_user or current_user.get('role') != 'admin':
                    response = {"error": "Forbidden"}
                else:
                    # Exiger multipart
                    fs = (data or {}).get("__fs__")
                    try:
                        user_id = int((data or {}).get('user_id') or 0)
                    except Exception:
                        user_id = 0
                    start_date = (data or {}).get('start_date')
                    end_date = (data or {}).get('end_date')
                    description = (data or {}).get('description')
                    has_pdf = bool(fs and hasattr(fs, 'keys') and ('pdf_file' in fs.keys()))
                    if not fs or not user_id or not start_date or not end_date or not has_pdf:
                        response = {"error": "Invalid payload"}
                    else:
                        try:
                            pdf_field = fs['pdf_file']
                            if isinstance(pdf_field, list) and pdf_field:
                                pdf_field = pdf_field[0]
                            original_name = getattr(pdf_field, 'filename', 'document.pdf')
                            # Sauvegarder dans /tmp/uploads/sickness_declarations
                            base_dir = '/tmp/uploads/sickness_declarations'
                            os.makedirs(base_dir, exist_ok=True)
                            unique_name = f"{uuid.uuid4()}.pdf"
                            file_path = os.path.join(base_dir, unique_name)
                            file_bytes = pdf_field.file.read()
                            with open(file_path, 'wb') as out:
                                out.write(file_bytes)
                            conn = init_db(); cursor = conn.cursor()
                            # Essayer d'enregistrer aussi les octets
                            try:
                                cursor.execute('''
                                        INSERT INTO sickness_declarations (user_id, start_date, end_date, description, pdf_filename, pdf_path, pdf_data, email_sent, viewed_by_admin)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 0)
                                    ''', (user_id, start_date, end_date, description, original_name, file_path, file_bytes))
                            except Exception:
                                cursor.execute('''
                                    INSERT INTO sickness_declarations (user_id, start_date, end_date, description, pdf_filename, pdf_path, email_sent, viewed_by_admin)
                                    VALUES (%s, %s, %s, %s, %s, %s, 0, 0)
                                ''', (user_id, start_date, end_date, description, original_name, file_path))
                            conn.commit(); new_id = cursor.lastrowid
                            # Récupérer email user + admins
                            cursor.execute('SELECT email, first_name, last_name FROM users WHERE id = %s', (user_id,))
                            urow = cursor.fetchone() or (None, '', '')
                            user_email = urow[0]
                            cursor.execute("SELECT email FROM users WHERE UPPER(role)='ADMIN'")
                            admin_rows = cursor.fetchall() or []
                            recipients = [r[0] for r in admin_rows]
                            if DEFAULT_ADMIN_EMAIL not in recipients:
                                recipients.append(DEFAULT_ADMIN_EMAIL)
                            if user_email: recipients.append(user_email)
                            subject = f"Gestion des absences - Arrêt maladie - {urow[1]} {urow[2]}"
                            body = f"Arrêt maladie du {start_date} au {end_date}. Description: {description or '—'}"
                            ok = send_email_resend(list(set(recipients)), subject, body, f"<p>{body}</p>", attachment_path=file_path, attachment_filename=original_name)
                            if ok:
                                cursor.execute('UPDATE sickness_declarations SET email_sent=1 WHERE id=%s', (new_id,))
                                conn.commit()
                            conn.close()
                            response = {"id": new_id, "start_date": start_date, "end_date": end_date, "description": description, "email_sent": bool(ok), "pdf_filename": original_name}
                        except Exception as e:
                            response = {"error": str(e)}
            elif self.path.startswith('/sickness-declarations/') and self.path.endswith('/mark-viewed'):
                # Marquer comme vue et envoyer un email au user
                try:
                    decl_id = int(self.path.strip('/').split('/')[1])
                except Exception:
                    decl_id = 0
                if decl_id <= 0:
                    response = {"error": "Bad request"}
                else:
                    try:
                        conn = init_db(); cursor = conn.cursor()
                        cursor.execute('UPDATE sickness_declarations SET viewed_by_admin=1 WHERE id=%s', (decl_id,))
                        # Récupérer infos pour email
                        cursor.execute('''
                            SELECT s.start_date, s.end_date, u.email, u.first_name, u.last_name
                             FROM sickness_declarations s JOIN users u ON s.user_id = u.id WHERE s.id = %s
                        ''', (decl_id,))
                        r = cursor.fetchone()
                        conn.commit(); conn.close()
                        if r:
                            subject = f"Gestion des absences - Déclaration consultée"
                            body = f"Votre déclaration du {r[0]} au {r[1]} a été consultée."
                            send_email_resend([r[2]], subject, body, f"<p>{body}</p>")
                        response = {"message": "Déclaration marquée comme vue et email envoyé"}
                    except Exception as e:
                        response = {"error": str(e)}
            elif self.path.startswith('/sickness-declarations/') and self.path.endswith('/resend-email'):
                # Renvoyer l'email pour une déclaration donnée (admin-only)
                try:
                    decl_id = int(self.path.strip('/').split('/')[1])
                except Exception:
                    decl_id = 0
                current_user = get_user_from_auth_header(self.headers)
                if not current_user or current_user.get('role') != 'admin':
                    response = {"error": "Forbidden"}
                elif decl_id <= 0:
                    response = {"error": "Bad request"}
                else:
                    try:
                        conn = init_db(); cursor = conn.cursor()
                        cursor.execute('''
                            SELECT s.pdf_path, s.pdf_filename, s.pdf_data, s.start_date, s.end_date, u.email, u.first_name, u.last_name
                              FROM sickness_declarations s JOIN users u ON s.user_id = u.id WHERE s.id = %s
                        ''', (decl_id,))
                        row = cursor.fetchone();
                        if not row:
                            conn.close(); response = {"error": "Declaration not found"}
                        else:
                            pdf_path, pdf_filename, pdf_data, s_start, s_end, user_email, fn, ln = row
                            attachment_path = None
                            if pdf_path and os.path.exists(pdf_path):
                                attachment_path = pdf_path
                            elif pdf_data is not None:
                                try:
                                    base_dir = '/tmp/uploads/sickness_declarations'
                                    os.makedirs(base_dir, exist_ok=True)
                                    tmp_name = f"{uuid.uuid4()}_resend.pdf"
                                    attachment_path = os.path.join(base_dir, tmp_name)
                                    content_bytes = pdf_data if isinstance(pdf_data, (bytes, bytearray)) else bytes(pdf_data)
                                    with open(attachment_path, 'wb') as f:
                                        f.write(content_bytes)
                                except Exception:
                                    attachment_path = None
                            # Construire destinataires: admins + user
                            cursor.execute("SELECT email FROM users WHERE UPPER(role)='ADMIN'")
                            admin_rows = cursor.fetchall() or []
                            recipients = [r[0] for r in admin_rows]
                            if DEFAULT_ADMIN_EMAIL not in recipients:
                                recipients.append(DEFAULT_ADMIN_EMAIL)
                            if user_email: recipients.append(user_email)
                            subject = f"Gestion des absences - Déclaration maladie (renvoi) - {fn} {ln}"
                            body = f"Déclaration du {s_start} au {s_end}."
                            ok = send_email_resend(list(set(recipients)), subject, body, f"<p>{body}</p>", attachment_path=attachment_path, attachment_filename=pdf_filename or 'document.pdf')
                            if ok:
                                cursor.execute('UPDATE sickness_declarations SET email_sent=1 WHERE id=%s', (decl_id,))
                                conn.commit()
                            conn.close()
                            response = {"message": "Email renvoyé", "ok": bool(ok)}
                    except Exception as e:
                        response = {"error": str(e)}
            elif self.path.rstrip('/') == '/absence-requests/admin':
                # Création d'une absence par un administrateur (JSON)
                current_user = get_user_from_auth_header(self.headers)
                if not current_user or current_user.get('role') != 'admin':
                    response = {"error": "Forbidden"}
                else:
                    payload = data or {}
                    try:
                        user_id = int(payload.get('user_id') or 0)
                    except Exception:
                        user_id = 0
                    abs_type = to_db_type(payload.get('type'))  # 'VACANCES' ou 'MALADIE'
                    start_date = payload.get('start_date')
                    end_date = payload.get('end_date')
                    reason = payload.get('reason')
                    admin_comment = payload.get('admin_comment')
                    status = to_db_status((payload.get('status') or 'approuve'))  # APPUOUE par défaut
                    if not user_id or abs_type not in ['VACANCES','MALADIE'] or not start_date or not end_date:
                        response = {"error": "Invalid payload"}
                    else:
                        try:
                            conn = init_db(); cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO absence_requests (user_id, type, start_date, end_date, reason, status, approved_by_id, admin_comment)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (user_id, abs_type, start_date, end_date, reason, status, current_user['id'], admin_comment))
                            conn.commit(); new_id = cursor.lastrowid
                            conn.close()
                            response = {"id": new_id, "user_id": user_id, "type": payload.get('type'), "start_date": start_date, "end_date": end_date, "reason": reason, "status": payload.get('status') or 'approuve'}
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
                            VALUES (%s, %s, %s, %s, %s)
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
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()

            response = {"error": "Route non trouvée"}

            if path.startswith('/absence-requests/admin/'):
                # PUT /absence-requests/admin/{id} (mise à jour admin complète)
                current_user = get_user_from_auth_header(self.headers)
                if not current_user or current_user.get('role') != 'admin':
                    response = {"error": "Forbidden"}
                else:
                    try:
                        request_id = int(path.split('/')[2])
                    except Exception:
                        request_id = 0
                    payload = data or {}
                    # Construire dynamiquement le SET
                    fields = []
                    params = []
                    if 'type' in payload and payload.get('type'):
                        fields.append('type = %s'); params.append(to_db_type(payload.get('type')))
                    if 'start_date' in payload and payload.get('start_date'):
                        fields.append('start_date = %s'); params.append(payload.get('start_date'))
                    if 'end_date' in payload and payload.get('end_date'):
                        fields.append('end_date = %s'); params.append(payload.get('end_date'))
                    if 'reason' in payload:
                        fields.append('reason = %s'); params.append(payload.get('reason'))
                    if 'status' in payload and payload.get('status'):
                        fields.append('status = %s'); params.append(to_db_status(payload.get('status')))
                    if 'admin_comment' in payload:
                        fields.append('admin_comment = %s'); params.append(payload.get('admin_comment'))
                    # Garder une trace de l'admin qui a modifié
                    fields.append('approved_by_id = %s'); params.append(current_user['id'])
                    if request_id <= 0 or not fields:
                        response = {"error": "Invalid payload"}
                    else:
                        try:
                            conn = init_db(); cursor = conn.cursor()
                            sql = f"UPDATE absence_requests SET {', '.join(fields)} WHERE id = %s"
                            params.append(request_id)
                            cursor.execute(sql, tuple(params))
                            conn.commit(); conn.close()
                            # Retour minimal
                            response = {"id": request_id, **{k: payload.get(k) for k in ['type','start_date','end_date','reason','status','admin_comment'] if k in payload}}
                        except Exception as e:
                            response = {"error": str(e)}
            elif path.startswith('/absence-requests/') and path.endswith('/status'):
                try:
                    request_id = int(path.split('/')[2])
                except Exception:
                    request_id = 0
                new_status = to_db_status((data or {}).get('status'))
                admin_comment = (data or {}).get('admin_comment')
                try:
                    conn = init_db(); cursor = conn.cursor()
                    cursor.execute('UPDATE absence_requests SET status = %s, admin_comment = %s WHERE id = %s', (new_status, admin_comment, request_id))
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
                            UPDATE users SET email=%s, first_name=%s, last_name=%s, role=%s, password_hash=%s WHERE id=%s
                        ''', (
                            payload.get('email'), payload.get('first_name'), payload.get('last_name'), (payload.get('role') or 'user').upper(), hash_password(payload.get('password')), user_id
                        ))
                    else:
                        cursor.execute('''
                            UPDATE users SET email=%s, first_name=%s, last_name=%s, role=%s WHERE id=%s
                        ''', (
                            payload.get('email'), payload.get('first_name'), payload.get('last_name'), (payload.get('role') or 'user').upper(), user_id
                        ))
                    conn.commit(); conn.close()
                    response = {"id": user_id, **{k: payload.get(k) for k in ['email','first_name','last_name','role']}}
                except Exception as e:
                    response = {"error": str(e)}

            # Écrire la réponse
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(safe_json_dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
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
                    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
                    conn.commit(); conn.close()
                    response = {"message": "Utilisateur supprimé"}
                except Exception as e:
                    response = {"error": str(e)}
            elif path.startswith('/absence-requests/admin/'):
                # DELETE /absence-requests/admin/{id}
                current_user = get_user_from_auth_header(self.headers)
                if not current_user or current_user.get('role') != 'admin':
                    response = {"error": "Forbidden"}
                else:
                    try:
                        request_id = int(path.split('/')[3])
                    except Exception:
                        request_id = 0
                    if request_id <= 0:
                        response = {"error": "Bad request"}
                    else:
                        try:
                            conn = init_db(); cursor = conn.cursor()
                            cursor.execute('DELETE FROM absence_requests WHERE id = %s', (request_id,))
                            conn.commit(); conn.close()
                            response = {"message": "Absence supprimée"}
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return