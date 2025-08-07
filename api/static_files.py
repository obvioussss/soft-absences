import mimetypes

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

        .login-container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }

        .logo {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 1rem;
        }

        .form-group {
            margin-bottom: 1rem;
            text-align: left;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }

        input {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e1e5e9;
            border-radius: 5px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
        }

        button {
            width: 100%;
            padding: 0.75rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        button:hover {
            transform: translateY(-2px);
        }

        .error {
            color: #e74c3c;
            margin-top: 1rem;
            padding: 0.5rem;
            background: #fdf2f2;
            border-radius: 5px;
            display: none;
        }

        .success {
            color: #27ae60;
            margin-top: 1rem;
            padding: 0.5rem;
            background: #f0f9f4;
            border-radius: 5px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🏢 Soft Absences</div>
        <h2>Connexion</h2>
        <form id="loginForm">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Mot de passe</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Se connecter</button>
        </form>
        <div id="error" class="error"></div>
        <div id="success" class="success"></div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('error');
            const successDiv = document.getElementById('success');
            
            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    successDiv.textContent = 'Connexion réussie ! Redirection...';
                    successDiv.style.display = 'block';
                    errorDiv.style.display = 'none';
                    
                    // Stocker les informations utilisateur
                    localStorage.setItem('user', JSON.stringify(data.user));
                    localStorage.setItem('token', data.token);
                    
                    // Rediriger vers le dashboard
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    errorDiv.textContent = data.error || 'Erreur de connexion';
                    errorDiv.style.display = 'block';
                    successDiv.style.display = 'none';
                }
            } catch (error) {
                errorDiv.textContent = 'Erreur de connexion au serveur';
                errorDiv.style.display = 'block';
                successDiv.style.display = 'none';
            }
        });
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
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
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
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }

        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .card h3 {
            color: #333;
            margin-bottom: 1rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 0.5rem 0.5rem 0.5rem 0;
        }

        .btn:hover {
            transform: translateY(-2px);
            transition: transform 0.2s ease;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .stat-item {
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 5px;
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
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🏢 Soft Absences</div>
        <div class="user-info">
            <span id="userName">Chargement...</span>
            <a href="#" class="logout-btn" onclick="logout()">Déconnexion</a>
        </div>
    </div>

    <div class="container">
        <h1>Tableau de bord</h1>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>📊 Statistiques</h3>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number" id="totalRequests">-</div>
                        <div class="stat-label">Demandes totales</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="pendingRequests">-</div>
                        <div class="stat-label">En attente</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="approvedRequests">-</div>
                        <div class="stat-label">Approuvées</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>🚀 Actions rapides</h3>
                <a href="#" class="btn" onclick="showNewRequestForm()">➕ Nouvelle demande</a>
                <a href="#" class="btn" onclick="showCalendar()">📅 Calendrier</a>
                <a href="#" class="btn" onclick="showMyRequests()">📋 Mes demandes</a>
            </div>

            <div class="card">
                <h3>📅 Prochaines absences</h3>
                <div id="upcomingAbsences">
                    <p>Aucune absence programmée</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Vérifier l'authentification
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const token = localStorage.getItem('token');

        if (!user.id || !token) {
            window.location.href = '/';
        }

        document.getElementById('userName').textContent = `${user.first_name} ${user.last_name}`;

        // Charger les données du dashboard
        loadDashboardData();

        async function loadDashboardData() {
            try {
                // Charger les statistiques
                const statsResponse = await fetch('/dashboard/stats', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (statsResponse.ok) {
                    const stats = await statsResponse.json();
                    document.getElementById('totalRequests').textContent = stats.total || 0;
                    document.getElementById('pendingRequests').textContent = stats.pending || 0;
                    document.getElementById('approvedRequests').textContent = stats.approved || 0;
                }

                // Charger les prochaines absences
                const absencesResponse = await fetch('/calendar/upcoming', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (absencesResponse.ok) {
                    const absences = await absencesResponse.json();
                    displayUpcomingAbsences(absences);
                }
            } catch (error) {
                console.error('Erreur lors du chargement des données:', error);
            }
        }

        function displayUpcomingAbsences(absences) {
            const container = document.getElementById('upcomingAbsences');
            
            if (!absences || absences.length === 0) {
                container.innerHTML = '<p>Aucune absence programmée</p>';
                return;
            }

            const html = absences.slice(0, 5).map(absence => `
                <div style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                    <strong>${absence.type}</strong> - ${absence.start_date} à ${absence.end_date}
                    <br><small>${absence.user_name}</small>
                </div>
            `).join('');
            
            container.innerHTML = html;
        }

        function logout() {
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            window.location.href = '/';
        }

        function showNewRequestForm() {
            // Implémenter l'affichage du formulaire de nouvelle demande
            alert('Fonctionnalité à implémenter');
        }

        function showCalendar() {
            // Implémenter l'affichage du calendrier
            alert('Fonctionnalité à implémenter');
        }

        function showMyRequests() {
            // Implémenter l'affichage des demandes de l'utilisateur
            alert('Fonctionnalité à implémenter');
        }
    </script>
</body>
</html>''',
        '/static/style.css': '''/* Styles globaux */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f7fa;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Header */
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 0;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
}

/* Navigation */
.nav {
    display: flex;
    gap: 1rem;
}

.nav-link {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    transition: background-color 0.3s ease;
}

.nav-link:hover {
    background: rgba(255, 255, 255, 0.2);
}

/* Cards */
.card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
}

.card h3 {
    color: #333;
    margin-bottom: 1rem;
    border-bottom: 2px solid #667eea;
    padding-bottom: 0.5rem;
}

/* Buttons */
.btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    margin: 0.5rem 0.5rem 0.5rem 0;
    transition: transform 0.2s ease;
}

.btn:hover {
    transform: translateY(-2px);
}

.btn-secondary {
    background: #6c757d;
}

.btn-success {
    background: #28a745;
}

.btn-danger {
    background: #dc3545;
}

.btn-warning {
    background: #ffc107;
    color: #212529;
}

/* Forms */
.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #333;
    font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e1e5e9;
    border-radius: 5px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #667eea;
}

/* Tables */
.table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

.table th,
.table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
}

.table th {
    background: #f8f9fa;
    font-weight: 600;
}

.table tr:hover {
    background: #f8f9fa;
}

/* Alerts */
.alert {
    padding: 1rem;
    border-radius: 5px;
    margin-bottom: 1rem;
}

.alert-success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.alert-danger {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.alert-warning {
    background: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
}

/* Utilities */
.text-center {
    text-align: center;
}

.text-right {
    text-align: right;
}

.mt-2 {
    margin-top: 0.5rem;
}

.mt-3 {
    margin-top: 1rem;
}

.mb-2 {
    margin-bottom: 0.5rem;
}

.mb-3 {
    margin-bottom: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
    
    .nav {
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .container {
        padding: 0 0.5rem;
    }
}'''
    }
    
    return static_files.get(file_path, None) 