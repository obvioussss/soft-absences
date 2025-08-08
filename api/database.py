import sqlite3
import hashlib
import os
from datetime import datetime

def init_db():
    """Initialise la base de données persistante (fichier) pour l'environnement serverless.

    Note: Sur Vercel, le système de fichiers est en lecture seule sauf le répertoire /tmp.
    Nous utilisons donc un fichier SQLite dans /tmp afin que les écritures persistent
    au moins pendant toute la durée de vie de l'instance (bien plus fiable que :memory:).
    """
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
            google_calendar_event_id TEXT,
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
            email_sent BOOLEAN DEFAULT 0,
            viewed_by_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
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