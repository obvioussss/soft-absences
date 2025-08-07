from http.server import BaseHTTPRequestHandler
import json
import os
import sqlite3
from datetime import datetime
import mimetypes
import hashlib

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

def get_mime_type(file_path):
    """Détermine le type MIME d'un fichier"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def get_static_content(file_path):
    """Retourne le contenu des fichiers statiques embarqués"""
    static_files = {
        '/static/index.html': '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soft Absences - Gestion des Absences</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 500px;
            width: 90%;
            text-align: center;
        }

        .logo {
            font-size: 2.5rem;
            margin-bottom: 20px;
            color: #667eea;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2rem;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1rem;
        }

        .status-card {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        }

        .api-info {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }

        .api-info h3 {
            color: #495057;
            margin-bottom: 15px;
        }

        .endpoints {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }

        .endpoint {
            background: #667eea;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-size: 0.9rem;
            text-decoration: none;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .endpoint:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .features {
            margin-top: 30px;
            text-align: left;
        }

        .features h3 {
            color: #333;
            margin-bottom: 15px;
            text-align: center;
        }

        .feature-list {
            list-style: none;
        }

        .feature-list li {
            padding: 8px 0;
            color: #555;
            position: relative;
            padding-left: 25px;
        }

        .feature-list li:before {
            content: "✅";
            position: absolute;
            left: 0;
            color: #4CAF50;
        }

        .login-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
        }

        .login-section h3 {
            color: #333;
            margin-bottom: 15px;
        }

        .login-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .form-group {
            text-align: left;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }

        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }

        .login-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .error-message {
            color: #dc3545;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            display: none;
        }

        @media (max-width: 600px) {
            .container {
                padding: 20px;
                margin: 20px;
            }
            
            .logo {
                font-size: 2rem;
            }
            
            h1 {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏢</div>
        <h1>Soft Absences</h1>
        <p class="subtitle">Gestion des absences et congés</p>
        
        <div class="status-card">
            <h3>✅ Application Opérationnelle</h3>
            <p>L'application est prête à être utilisée</p>
        </div>

        <div class="api-info">
            <h3>🔗 API Endpoints</h3>
            <div class="endpoints">
                <a href="/health" class="endpoint">Health Check</a>
                <a href="/users" class="endpoint">Utilisateurs</a>
                <a href="/absences" class="endpoint">Absences</a>
                <a href="/docs" class="endpoint">Documentation</a>
            </div>
        </div>

        <div class="features">
            <h3>✨ Fonctionnalités</h3>
            <ul class="feature-list">
                <li>Gestion des demandes d'absence</li>
                <li>Validation par les administrateurs</li>
                <li>Calendrier des absences</li>
                <li>Notifications par email</li>
                <li>Déclarations de maladie</li>
                <li>Intégration Google Calendar</li>
            </ul>
        </div>

        <div class="login-section">
            <h3>🔐 Connexion</h3>
            <form class="login-form" id="loginForm">
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required placeholder="admin@example.com">
                </div>
                <div class="form-group">
                    <label for="password">Mot de passe</label>
                    <input type="password" id="password" name="password" required placeholder="admin123">
                </div>
                <button type="submit" class="login-btn">Se connecter</button>
            </form>
            <div class="error-message" id="errorMessage"></div>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('errorMessage');
            
            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    
                    // Rediriger vers le dashboard
                    window.location.href = '/dashboard';
                } else {
                    const errorData = await response.json();
                    errorMessage.textContent = errorData.error || 'Erreur de connexion';
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                errorMessage.textContent = 'Erreur de connexion au serveur';
                errorMessage.style.display = 'block';
            }
        });

        // Vérifier si l'utilisateur est déjà connecté
        const token = localStorage.getItem('token');
        if (token) {
            // Rediriger vers le dashboard si déjà connecté
            window.location.href = '/dashboard';
        }
    </script>
</body>
</html>''',
        '/static/dashboard.html': '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Soft Absences</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: bold;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logout-btn {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }

        .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }

        .main-content {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }

        .card h3 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }

        .card-content {
            color: #666;
            line-height: 1.6;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .stat-item {
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            color: #666;
            font-size: 0.9rem;
        }

        .action-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }

        .btn {
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
            font-weight: 500;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }

        .btn-secondary {
            background: #6c757d;
            color: white;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .recent-absences {
            margin-top: 2rem;
        }

        .absence-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid #e9ecef;
        }

        .absence-item:last-child {
            border-bottom: none;
        }

        .absence-info h4 {
            color: #333;
            margin-bottom: 0.5rem;
        }

        .absence-info p {
            color: #666;
            font-size: 0.9rem;
        }

        .status-badge {
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .status-pending {
            background: #fff3cd;
            color: #856404;
        }

        .status-approved {
            background: #d4edda;
            color: #155724;
        }

        .status-rejected {
            background: #f8d7da;
            color: #721c24;
        }

        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 1rem;
            }

            .main-content {
                padding: 0 1rem;
            }

            .dashboard-grid {
                grid-template-columns: 1fr;
            }

            .action-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">🏢 Soft Absences</div>
            <div class="user-info">
                <span id="userName">Chargement...</span>
                <button class="logout-btn" onclick="logout()">Déconnexion</button>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="dashboard-grid">
            <div class="card">
                <h3>📊 Statistiques</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number" id="totalAbsences">-</div>
                        <div class="stat-label">Total Absences</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="pendingAbsences">-</div>
                        <div class="stat-label">En Attente</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="approvedAbsences">-</div>
                        <div class="stat-label">Approuvées</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>🚀 Actions Rapides</h3>
                <div class="card-content">
                    <p>Gérez vos absences et demandes rapidement</p>
                    <div class="action-buttons">
                        <a href="#" class="btn btn-primary" onclick="showNewAbsenceForm()">Nouvelle Demande</a>
                        <a href="#" class="btn btn-secondary" onclick="showCalendar()">Voir Calendrier</a>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>📅 Prochaines Absences</h3>
                <div class="card-content">
                    <div id="upcomingAbsences">
                        <p>Chargement des absences...</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="card recent-absences">
            <h3>📋 Absences Récentes</h3>
            <div id="recentAbsencesList">
                <p>Chargement...</p>
            </div>
        </div>
    </main>

    <script>
        // Vérifier l'authentification
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/';
        }

        // Charger les informations utilisateur
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        document.getElementById('userName').textContent = user.first_name ? `${user.first_name} ${user.last_name}` : 'Utilisateur';

        // Charger les données du dashboard
        async function loadDashboardData() {
            try {
                const [absencesResponse, usersResponse] = await Promise.all([
                    fetch('/absences', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    }),
                    fetch('/users', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    })
                ]);

                if (absencesResponse.ok) {
                    const absencesData = await absencesResponse.json();
                    updateAbsencesStats(absencesData.absences || []);
                    updateRecentAbsences(absencesData.absences || []);
                }

                if (usersResponse.ok) {
                    const usersData = await usersResponse.json();
                    // Mettre à jour les statistiques utilisateurs si nécessaire
                }
            } catch (error) {
                console.error('Erreur lors du chargement des données:', error);
            }
        }

        function updateAbsencesStats(absences) {
            const total = absences.length;
            const pending = absences.filter(a => a.status === 'EN_ATTENTE').length;
            const approved = absences.filter(a => a.status === 'APPROUVEE').length;

            document.getElementById('totalAbsences').textContent = total;
            document.getElementById('pendingAbsences').textContent = pending;
            document.getElementById('approvedAbsences').textContent = approved;
        }

        function updateRecentAbsences(absences) {
            const recentList = document.getElementById('recentAbsencesList');
            const upcomingList = document.getElementById('upcomingAbsences');

            if (absences.length === 0) {
                recentList.innerHTML = '<p>Aucune absence récente</p>';
                upcomingList.innerHTML = '<p>Aucune absence à venir</p>';
                return;
            }

            // Trier par date de création (plus récentes en premier)
            const sortedAbsences = absences.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            const recentAbsences = sortedAbsences.slice(0, 5);

            // Filtrer les absences à venir (dates futures)
            const upcomingAbsences = absences.filter(a => new Date(a.start_date) > new Date()).slice(0, 3);

            // Afficher les absences récentes
            recentList.innerHTML = recentAbsences.map(absence => `
                <div class="absence-item">
                    <div class="absence-info">
                        <h4>${absence.type}</h4>
                        <p>${absence.user_name} - ${new Date(absence.start_date).toLocaleDateString()} au ${new Date(absence.end_date).toLocaleDateString()}</p>
                    </div>
                    <span class="status-badge status-${absence.status.toLowerCase()}">${absence.status}</span>
                </div>
            `).join('');

            // Afficher les absences à venir
            upcomingList.innerHTML = upcomingAbsences.map(absence => `
                <div class="absence-item">
                    <div class="absence-info">
                        <h4>${absence.type}</h4>
                        <p>${absence.user_name} - ${new Date(absence.start_date).toLocaleDateString()} au ${new Date(absence.end_date).toLocaleDateString()}</p>
                    </div>
                    <span class="status-badge status-${absence.status.toLowerCase()}">${absence.status}</span>
                </div>
            `).join('');
        }

        function showNewAbsenceForm() {
            alert('Fonctionnalité à implémenter : Formulaire de nouvelle demande d\'absence');
        }

        function showCalendar() {
            alert('Fonctionnalité à implémenter : Vue calendrier');
        }

        function logout() {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/';
        }

        // Charger les données au chargement de la page
        loadDashboardData();
    </script>
</body>
</html>''',
        '/static/style.css': '''/* Variables CSS */
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --success-color: #4CAF50;
    --warning-color: #ff9800;
    --danger-color: #f44336;
    --light-gray: #f5f7fa;
    --dark-gray: #333;
    --border-radius: 15px;
    --box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    --transition: all 0.3s ease;
}

/* Reset et base */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    min-height: 100vh;
    line-height: 1.6;
}

/* Conteneurs */
.container {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: 2rem;
    max-width: 500px;
    width: 90%;
    margin: 2rem auto;
    text-align: center;
}

/* En-têtes */
.header {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    color: white;
    padding: 1rem 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
}

/* Cartes */
.card {
    background: white;
    border-radius: var(--border-radius);
    padding: 2rem;
    box-shadow: var(--box-shadow);
    transition: var(--transition);
    margin-bottom: 1rem;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.card h3 {
    color: var(--dark-gray);
    margin-bottom: 1rem;
    font-size: 1.3rem;
}

/* Boutons */
.btn {
    padding: 0.8rem 1.5rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    text-align: center;
    transition: var(--transition);
    font-weight: 500;
    font-size: 1rem;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

/* Formulaires */
.form-group {
    text-align: left;
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--dark-gray);
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 12px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s;
}

.form-group input:focus {
    outline: none;
    border-color: var(--primary-color);
}

/* Messages */
.error-message {
    color: var(--danger-color);
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    padding: 10px;
    border-radius: 8px;
    margin-top: 10px;
    display: none;
}

.success-message {
    color: var(--success-color);
    background: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 10px;
    border-radius: 8px;
    margin-top: 10px;
}

/* Statuts */
.status-badge {
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
}

.status-pending {
    background: #fff3cd;
    color: #856404;
}

.status-approved {
    background: #d4edda;
    color: #155724;
}

.status-rejected {
    background: #f8d7da;
    color: #721c24;
}

/* Grilles */
.grid {
    display: grid;
    gap: 1rem;
}

.grid-2 {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.grid-3 {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

/* Responsive */
@media (max-width: 768px) {
    .container {
        padding: 1rem;
        margin: 1rem;
    }
    
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
    
    .grid-2,
    .grid-3 {
        grid-template-columns: 1fr;
    }
}'''
    }
    
    return static_files.get(file_path)

def serve_static_file(self, file_path):
    """Sert un fichier statique"""
    try:
        content = get_static_content(file_path)
        
        if not content:
            return False
            
        # Déterminer le type MIME
        mime_type = get_mime_type(file_path)
        
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
                # Authentification
                email = data.get('email', '')
                password = data.get('password', '')
                
                if not email or not password:
                    response = {
                        "error": "Email et mot de passe requis"
                    }
                else:
                    conn = init_db()
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, email, first_name, last_name, password_hash, role FROM users WHERE email = ?', (email,))
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user and verify_password(password, user[4]):
                        response = {
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
                        response = {
                            "error": "Email ou mot de passe incorrect"
                        }
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