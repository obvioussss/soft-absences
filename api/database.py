import sqlite3
import hashlib
from datetime import datetime

def init_db():
    """Initialise la base de données en mémoire pour Vercel"""
    conn = sqlite3.connect(':memory:')
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
    
    # Insérer des données de test avec mot de passe hashé
    test_password = hashlib.sha256("password123".encode()).hexdigest()
    
    # Admin
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, first_name, last_name, password_hash, role) 
        VALUES ('admin@example.com', 'Admin', 'User', ?, 'ADMIN')
    ''', (test_password,))

    # Admin local (pour correspondre à l'interface locale)
    admin_local_password = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, first_name, last_name, password_hash, role) 
        VALUES ('hello.obvious@gmail.com', 'Admin', 'System', ?, 'ADMIN')
    ''', (admin_local_password,))
    
    # Utilisateur test
    user_password = hashlib.sha256("password123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, first_name, last_name, password_hash, role) 
        VALUES ('fautrel.pierre@gmail.com', 'Pierre', 'Fautrel', ?, 'USER')
    ''', (user_password,))
    
    # Ajouter quelques absences de test
    cursor.execute('''
        INSERT OR IGNORE INTO absence_requests 
        (user_id, type, start_date, end_date, reason, status) 
        VALUES 
        (2, 'VACANCES', '2024-01-15', '2024-01-19', 'Vacances d''hiver', 'APPROUVE'),
        (2, 'MALADIE', '2024-02-01', '2024-02-03', 'Grippe', 'EN_ATTENTE'),
        (2, 'VACANCES', '2024-03-20', '2024-03-25', 'Vacances de printemps', 'REFUSE')
    ''')
    
    # Ajouter quelques déclarations de maladie de test
    cursor.execute('''
        INSERT OR IGNORE INTO sickness_declarations 
        (user_id, start_date, end_date, description) 
        VALUES 
        (2, '2024-02-01', '2024-02-03', 'Grippe avec certificat médical'),
        (2, '2024-04-10', '2024-04-12', 'Angine')
    ''')
    
    conn.commit()
    return conn

def hash_password(password):
    """Hash un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Vérifie un mot de passe"""
    return hash_password(password) == password_hash 