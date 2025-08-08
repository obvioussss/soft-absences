import sqlite3
import hashlib
import os
from datetime import datetime

_pg_conn = None

def _init_db_postgres(db_url: str):
    """Initialise (si besoin) la base Postgres (Neon) et renvoie une connexion réutilisable."""
    global _pg_conn
    if _pg_conn is not None:
        return _pg_conn
    try:
        import psycopg
        _pg_conn = psycopg.connect(db_url, autocommit=True)
        cur = _pg_conn.cursor()
        # Création des tables si absentes (syntaxe Postgres)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'USER',
                is_active BOOLEAN DEFAULT TRUE,
                annual_leave_days INTEGER DEFAULT 25,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS absence_requests (
                id BIGSERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'EN_ATTENTE',
                approved_by_id INTEGER,
                admin_comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sickness_declarations (
                id BIGSERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                description TEXT,
                pdf_filename TEXT,
                pdf_path TEXT,
                pdf_data BYTEA,
                email_sent BOOLEAN DEFAULT FALSE,
                viewed_by_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Assurer la présence de la colonne pdf_data
        try:
            cur.execute("SELECT 1 FROM information_schema.columns WHERE table_name='sickness_declarations' AND column_name='pdf_data'")
            if cur.fetchone() is None:
                cur.execute("ALTER TABLE sickness_declarations ADD COLUMN pdf_data BYTEA")
        except Exception:
            pass
        # Admin par défaut si absent
        admin_local_password = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute(
            """
            INSERT INTO users (email, first_name, last_name, password_hash, role)
            SELECT %s, %s, %s, %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = %s)
            """,
            (
                'hello.obvious@gmail.com', 'Admin', 'System', admin_local_password, 'ADMIN',
                'hello.obvious@gmail.com'
            )
        )
        cur.close()
        return _pg_conn
    except Exception:
        # Si psycopg indisponible ou erreur, on ne casse pas le runtime
        _pg_conn = None
        return None


def init_db():
    """Initialise la base de données persistante (fichier) pour l'environnement serverless.

    Note: Sur Vercel, le système de fichiers est en lecture seule sauf le répertoire /tmp.
    Nous utilisons donc un fichier SQLite dans /tmp afin que les écritures persistent
    au moins pendant toute la durée de vie de l'instance (bien plus fiable que :memory:).
    """
    db_url = os.getenv('DATABASE_URL', '').strip()
    if db_url.startswith('postgres://') or db_url.startswith('postgresql://'):
        pg = _init_db_postgres(db_url)
        if pg is not None:
            return pg

    # Fallback SQLite fichier (persistance locale de l'instance)
    db_file = os.getenv('DB_FILE', '/tmp/soft_absences.db')
    # Assurer l'existence du dossier cible
    os.makedirs(os.path.dirname(db_file), exist_ok=True)

    conn = sqlite3.connect(db_file, check_same_thread=False)
    cursor = conn.cursor()
    
    # Créer les tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sickness_declarations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            description TEXT,
            pdf_filename TEXT,
            pdf_path TEXT,
            pdf_data BLOB,
            email_sent BOOLEAN DEFAULT 0,
            viewed_by_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    # Assurer la présence de la colonne pdf_data si table déjà existante
    try:
        cursor.execute("PRAGMA table_info(sickness_declarations)")
        cols = [r[1] for r in cursor.fetchall()]
        if 'pdf_data' not in cols:
            cursor.execute('ALTER TABLE sickness_declarations ADD COLUMN pdf_data BLOB')
    except Exception:
        pass
    
    # Créer uniquement l'admin par défaut si absent
    admin_local_password = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, first_name, last_name, password_hash, role) 
        VALUES ('hello.obvious@gmail.com', 'Admin', 'System', ?, 'ADMIN')
    ''', (admin_local_password,))
    
    conn.commit()
    return conn

def hash_password(password):
    """Hash un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Vérifie un mot de passe"""
    return hash_password(password) == password_hash 