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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insérer des données de test avec mot de passe hashé
    test_password = hashlib.sha256("password123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, first_name, last_name, password_hash, role) 
        VALUES ('admin@example.com', 'Admin', 'User', ?, 'ADMIN')
    ''', (test_password,))
    
    # Ajouter un utilisateur de test
    user_password = hashlib.sha256("password123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, first_name, last_name, password_hash, role) 
        VALUES ('fautrel.pierre@gmail.com', 'Pierre', 'Fautrel', ?, 'USER')
    ''', (user_password,))
    
    conn.commit()
    return conn

def hash_password(password):
    """Hash un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Vérifie un mot de passe"""
    return hash_password(password) == password_hash 