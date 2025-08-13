import mimetypes

def get_mime_type(file_path):
    """Détermine le type MIME d'un fichier"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def get_static_content(file_path):
    """Retourne le contenu des fichiers statiques embarqués"""
    static_files = {
        '/static/index.html': {
            'content': '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestion des Absences</title>
    <link rel="stylesheet" href="/static/css/styles.css">
    <!-- Script de configuration en premier -->
    <script src="/static/js/config.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Gestion des Absences</h1>
        </div>
        
        <!-- Section d'authentification -->
        <div id="auth-section" class="auth-section">
            <h2>Connexion</h2>
            <form id="login-form">
                <div class="form-group">
                    <label for="email">Email :</label>
                    <input type="email" id="email" value="hello.obvious@gmail.com" required autocomplete="email">
                </div>
                <div class="form-group">
                    <label for="password">Mot de passe :</label>
                    <input type="password" id="password" value="admin123" required autocomplete="current-password">
                </div>
                <button type="submit" class="btn">Se connecter</button>
            </form>
        </div>
        
        <!-- Contenu principal -->
        <div id="main-content" class="main-content">
            <div class="user-info" id="user-info">
                <!-- Info utilisateur -->
            </div>
            <div style="clear: both;"></div>
            
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('dashboard')">Tableau de bord</button>
                <button class="nav-tab" onclick="showTab('calendar')">Calendrier</button>
                <button class="nav-tab user-only" onclick="showTab('procedure')">Mes Demandes</button>
                <button class="nav-tab admin-only" onclick="showTab('admin-users')" style="display: none;">Utilisateurs</button>
                <button class="nav-tab admin-only" onclick="showTab('admin-requests')" style="display: none;">📋 Demandes</button>
                
                <button class="nav-tab" onclick="logout()">Déconnexion</button>
            </div>
            
            <!-- Tableau de bord -->
            <div id="dashboard" class="tab-content active">
                <h2>Tableau de bord</h2>
                <div id="dashboard-content" class="loading">Chargement...</div>
            </div>
            

            
            <!-- Calendrier -->
            <div id="calendar" class="tab-content">
                <!-- Calendrier pour admin (vue mensuelle) et utilisateurs (vue annuelle) -->
                <div id="calendar-section" class="calendar-container">
                    <div class="calendar-header">
                        <div class="calendar-nav">
                            <button id="prev-period" class="nav-btn">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                    <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            </button>
                            <h2 id="calendar-title">Calendrier</h2>
                            <button id="next-period" class="nav-btn">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                    <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            </button>
                        </div>
                        <div class="calendar-actions">
                            <button id="today-btn" class="btn btn-secondary">Aujourd'hui</button>
                            <button id="admin-add-absence-btn" class="btn btn-primary admin-only" onclick="showAdminAbsenceForm()" style="display: none;">➕ Ajouter absence</button>
                            <div id="calendar-summary" class="calendar-summary" style="display: none;">
                                <span id="summary-text"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Vue mensuelle pour admin -->
                    <div id="monthly-calendar" class="monthly-view" style="display: none;">
                        <div class="calendar-grid">
                            <div class="calendar-weekdays">
                                <div class="weekday">Lun</div>
                                <div class="weekday">Mar</div>
                                <div class="weekday">Mer</div>
                                <div class="weekday">Jeu</div>
                                <div class="weekday">Ven</div>
                                <div class="weekday">Sam</div>
                                <div class="weekday">Dim</div>
                            </div>
                            <div id="calendar-days" class="calendar-days">
                                <!-- Les jours seront générés par JavaScript -->
                            </div>
                        </div>
                    </div>

                    <!-- Vue annuelle pour utilisateurs -->
                    <div id="yearly-calendar" class="yearly-view" style="display: none;">
                        <div class="year-grid">
                            <!-- Les 12 mois seront générés par JavaScript -->
                        </div>
                    </div>

                    <!-- Modal pour afficher les détails d'un événement -->
                    <div id="event-modal" class="modal" style="display: none;">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h3 id="event-title">Détails de l'absence</h3>
                                <button class="modal-close" onclick="closeEventModal()">&times;</button>
                            </div>
                            <div class="modal-body">
                                <div class="event-details">
                                    <div class="detail-row">
                                        <strong>Utilisateur:</strong>
                                        <span id="event-user"></span>
                                    </div>
                                    <div class="detail-row">
                                        <strong>Type:</strong>
                                        <span id="event-type"></span>
                                    </div>
                                    <div class="detail-row">
                                        <strong>Dates:</strong>
                                        <span id="event-dates"></span>
                                    </div>
                                    <div class="detail-row">
                                        <strong>Status:</strong>
                                        <span id="event-status"></span>
                                    </div>
                                    <div class="detail-row" id="event-reason-row" style="display: none;">
                                        <strong>Raison:</strong>
                                        <span id="event-reason"></span>
                                    </div>
                                    <div class="detail-row admin-only" style="display:none; gap:8px;">
                                        <button id="event-edit-btn" class="btn btn-warning">Modifier</button>
                                        <button id="event-delete-btn" class="btn btn-danger">Supprimer</button>
                                    </div>
                                </div>

                                 <!-- Formulaire d'édition intégré -->
                                 <form id="event-edit-form" style="display:none; margin-top: 10px;">
                                     <div class="form-group">
                                         <label for="edit-start-date">Date de début :</label>
                                         <input type="date" id="edit-start-date" required />
                                     </div>
                                     <div class="form-group">
                                         <label for="edit-end-date">Date de fin :</label>
                                         <input type="date" id="edit-end-date" required />
                                     </div>
                                     <div class="form-group">
                                         <label for="edit-reason">Raison (optionnel) :</label>
                                         <textarea id="edit-reason" placeholder="Motif de la demande..."></textarea>
                                     </div>
                                     <div class="form-group">
                                         <label for="edit-status">Statut :</label>
                                         <select id="edit-status">
                                             <option value="en_attente">En attente</option>
                                             <option value="approuve">Approuvé</option>
                                             <option value="refuse">Refusé</option>
                                         </select>
                                     </div>
                                     <div style="text-align: right;">
                                         <button type="button" id="event-edit-cancel" class="btn">Annuler</button>
                                         <button type="submit" class="btn btn-success">Enregistrer</button>
                                     </div>
                                 </form>

                                 <!-- Confirmation de suppression intégrée -->
                                 <div id="event-delete-confirm" style="display:none; margin-top: 10px;">
                                     <div class="alert alert-error" style="margin-bottom: 12px;">
                                         Êtes-vous sûr de vouloir supprimer cette absence ?
                                     </div>
                                     <div style="text-align: right;">
                                         <button type="button" id="event-delete-cancel" class="btn">Annuler</button>
                                         <button type="button" id="event-delete-confirm-btn" class="btn btn-danger">Supprimer définitivement</button>
                                     </div>
                                 </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Formulaire admin pour créer une absence -->
                    <div id="admin-absence-modal" class="modal" style="display: none;">
                        <div class="modal-content" style="max-width: 600px;">
                            <div class="modal-header">
                                <h3 style="color: #e74c3c; margin: 0;">👨‍💼 Créer une absence (Admin)</h3>
                                <button class="modal-close" onclick="hideAdminAbsenceForm()">&times;</button>
                            </div>
                            <div class="modal-body">
                                <form id="admin-absence-form-element">
                                    <div class="form-group">
                                        <label for="admin-absence-user">Utilisateur :</label>
                                        <select id="admin-absence-user" required>
                                            <option value="">Sélectionner un utilisateur...</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="admin-absence-type">Type d'absence :</label>
                                        <select id="admin-absence-type" required>
                                            <option value="vacances">Vacances</option>
                                            <option value="maladie">Maladie</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="admin-start-date">Date de début :</label>
                                        <input type="date" id="admin-start-date" required>
                                    </div>
                                    <div class="form-group">
                                        <label for="admin-end-date">Date de fin :</label>
                                        <input type="date" id="admin-end-date" required>
                                    </div>
                                    <div class="form-group">
                                        <label for="admin-comment">Commentaire admin (optionnel) :</label>
                                        <textarea id="admin-comment" placeholder="Commentaire pour l'utilisateur..."></textarea>
                                    </div>
                                    <div class="form-group" id="admin-absence-pdf-group" style="display:none;">
                                        <label for="admin-absence-pdf">Certificat médical (PDF) :</label>
                                        <div id="admin-absence-dropzone" style="border: 2px dashed #ffc107; padding: 20px; border-radius: 8px; background: #fff8e1; text-align: center; cursor: pointer;">
                                            Glissez-déposez le PDF ici, ou cliquez pour sélectionner.
                                            <input type="file" id="admin-absence-pdf" accept=".pdf" style="display:none;">
                                        </div>
                                        <small id="admin-absence-pdf-name" style="display:block; color:#856404; margin-top:6px;">Aucun fichier sélectionné</small>
                                        <small style="display:block; color:#856404; margin-top:6px;">PDF uniquement, 10MB max</small>
                                    </div>
                                    <div style="text-align: right; margin-top: 20px;">
                                        <button type="button" class="btn" onclick="hideAdminAbsenceForm()">Annuler</button>
                                        <button type="submit" class="btn btn-success">Créer l'absence</button>
                                    </div>
                    
                    
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Procédure -->
            <div id="procedure" class="tab-content">
                <h2>Mes Demandes d'Absence</h2>
                
                <!-- Boutons d'action -->
                <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                    <button class="btn" onclick="showNewRequestForm()">➕ Nouvelle demande de congé</button>
                    <button class="btn btn-warning" onclick="showSicknessDeclarationForm()">🏥 Déclaration de maladie</button>
                </div>
                
                <!-- Formulaire de nouvelle demande intégré -->
                <div id="new-request-form" style="display: none; margin-bottom: 20px; background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <h3>Nouvelle demande d'absence</h3>
                    <form id="absence-form">
                        <div class="form-group">
                            <label for="absence-type">Type d'absence :</label>
                            <select id="absence-type" required>
                                <option value="vacances">Vacances</option>
                                <option value="maladie">Maladie</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="start-date">Date de début :</label>
                            <input type="date" id="start-date" required>
                        </div>
                        <div class="form-group">
                            <label for="end-date">Date de fin :</label>
                            <input type="date" id="end-date" required>
                        </div>
                        <div class="form-group">
                            <label for="reason">Raison (optionnel) :</label>
                            <textarea id="reason" placeholder="Motif de la demande..."></textarea>
                        </div>
                        <button type="submit" class="btn btn-success">Soumettre</button>
                        <button type="button" class="btn" onclick="hideNewRequestForm()">Annuler</button>
                    </form>
                </div>
                
                <!-- Formulaire de déclaration de maladie -->
                <div id="sickness-declaration-form" style="display: none; margin-bottom: 20px; background: #fff3cd; padding: 20px; border-radius: 8px; border: 2px solid #ffc107;">
                    <h3 style="color: #856404;">🏥 Déclaration de maladie avec certificat médical</h3>
                    <p style="color: #856404; margin-bottom: 15px;">
                        <strong>Note:</strong> Cette déclaration sera automatiquement envoyée avec votre certificat médical à hello.obvious@gmail.com
                    </p>
                    <form id="sickness-form" enctype="multipart/form-data">
                        <div class="form-group">
                            <label for="sickness-start-date">Date de début :</label>
                            <input type="date" id="sickness-start-date" required>
                        </div>
                        <div class="form-group">
                            <label for="sickness-end-date">Date de fin :</label>
                            <input type="date" id="sickness-end-date" required>
                        </div>
                        <div class="form-group">
                            <label for="sickness-description">Description (optionnel) :</label>
                            <textarea id="sickness-description" placeholder="Détails sur l'arrêt maladie..."></textarea>
                        </div>
                        <div class="form-group">
                            <label for="sickness-pdf">Certificat médical (PDF) :</label>
                            <input type="file" id="sickness-pdf" accept=".pdf" required>
                            <small style="color: #856404; display: block; margin-top: 5px;">Fichier PDF uniquement, maximum 10MB</small>
                        </div>
                        <button type="submit" class="btn btn-warning">📧 Envoyer la déclaration</button>
                        <button type="button" class="btn" onclick="hideSicknessDeclarationForm()">Annuler</button>
                    </form>
                </div>
                
                <!-- Sous-onglets pour les demandes utilisateur -->
                <div class="sub-tabs" style="margin-top: 10px;">
                    <button class="sub-tab active" onclick="showSubTab('user-vacation-requests')">🏖️ Demandes de Vacances</button>
                    <button class="sub-tab" onclick="showSubTab('user-sickness-declarations')">🏥 Déclarations de Maladie</button>
                </div>
                <div id="user-vacation-requests" class="sub-tab-content active">
                    <div id="user-vacation-requests-list" class="loading">Chargement...</div>
                </div>
                <div id="user-sickness-declarations" class="sub-tab-content">
                    <div id="user-sickness-declarations-list" class="loading">Chargement...</div>
                </div>
                
                <!-- Section procédure séparée -->
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff;">
                    <h3>📖 Procédure et Informations</h3>
                    <div style="max-width: 800px; line-height: 1.6;">
                        <p>Pour assurer une bonne organisation au sein de l'équipe, veuillez suivre la procédure ci-dessous pour toute demande de congés :</p>
                    
                    <ol style="margin: 20px 0; padding-left: 30px;">
                        <li><strong>Délai de demande :</strong> Formuler votre demande au moins 2 mois à l'avance (sauf urgence) par email hello.obvious@gmail.com</li>
                        <li><strong>Validation :</strong> La demande doit être approuvée par un réponse écrite via la chaine de mail.</li>
                        <li><strong>Confirmation :</strong> Une fois validée, l'absence sera notée dans le calendrier d'équipe</li>
                    </ol>
                    
                    <h3>Types d'Absences</h3>
                    
                    <div style="margin-bottom: 20px;">
                        <h4><strong>Congés Payés Annuels</strong></h4>
                        <p>Chaque salarié dispose de 25 jours ouvrés de congés payés par an (du 1er juin au 31 mai).</p>
                        <p>Le fractionnement des congés est possible sous certaines conditions.</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h4><strong>RTT (Réduction du Temps de Travail)</strong></h4>
                        <p>Nombre de jours selon votre contrat et la convention collective applicable.</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h4><strong>Congés Exceptionnels</strong></h4>
                        <ul style="margin-left: 20px;">
                            <li>Mariage/PACS : 4 jours</li>
                            <li>Naissance/Adoption : 3 jours</li>
                            <li>Décès d'un proche : 1 à 3 jours selon le lien de parenté</li>
                            <li>Déménagement : 1 jour</li>
                        </ul>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h4><strong>Arrêt Maladie</strong></h4>
                        <p>En cas de maladie, informer votre responsable dès que possible.</p>
                        <p>Envoyer votre arrêt de travail dans les 48 heures à l'employeur et à la CPAM.</p>
                        <p><strong>Nouveau:</strong> Vous pouvez maintenant utiliser le formulaire de déclaration de maladie ci-dessus pour envoyer automatiquement votre certificat médical.</p>
                    </div>
                </div>
            </div>
            </div>
            
            <!-- Admin: Gestion des utilisateurs -->
            <div id="admin-users" class="tab-content">
                <h2>Gestion des utilisateurs</h2>
                <button class="btn" onclick="showNewUserForm()">➕ Nouvel utilisateur</button>
                
                <!-- Formulaire utilisateur intégré -->
                <div id="new-user-form" style="display: none; margin-top: 20px; background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <h3>Nouvel utilisateur</h3>
                    <form id="user-form">
                        <div class="form-group">
                            <label for="user-email">Email :</label>
                            <input type="email" id="user-email" required autocomplete="email">
                        </div>
                        <div class="form-group">
                            <label for="user-first-name">Prénom :</label>
                            <input type="text" id="user-first-name" required autocomplete="given-name">
                        </div>
                        <div class="form-group">
                            <label for="user-last-name">Nom :</label>
                            <input type="text" id="user-last-name" required autocomplete="family-name">
                        </div>
                        <div class="form-group">
                            <label for="user-role">Rôle :</label>
                            <select id="user-role" required>
                                <option value="user">Utilisateur</option>
                                <option value="admin">Administrateur</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="user-password">Mot de passe :</label>
                            <input type="password" id="user-password" required autocomplete="new-password">
                        </div>
                        <button type="submit" class="btn btn-success">Créer</button>
                        <button type="button" class="btn" onclick="hideNewUserForm()">Annuler</button>
                    </form>
                </div>
                
                <div id="users-list" class="loading" style="margin-top: 20px;">Chargement...</div>
                
                <!-- Modal pour le résumé des absences d'un utilisateur -->
                <div id="user-absence-modal" class="modal" style="display: none;">
                    <div class="modal-content" style="max-width: 800px;">
                        <div class="modal-header">
                            <h3 id="user-absence-title">Résumé des absences</h3>
                            <button class="modal-close" onclick="closeUserAbsenceModal()">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div id="user-absence-summary" class="loading">Chargement...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Admin: Toutes les demandes -->
            <div id="admin-requests" class="tab-content">
                <h2>📋 Gestion des Demandes - Administrateur</h2>
                
                <!-- Sous-onglets pour les demandes -->
                <div class="sub-tabs">
                    <button class="sub-tab active" onclick="showSubTab('vacation-requests')">🏖️ Demandes de Vacances</button>
                    <button class="sub-tab" onclick="showSubTab('sickness-declarations')">🏥 Déclarations de Maladie</button>
                    <button class="sub-tab" onclick="showSubTab('admin-documents')">📄 Documents</button>
                </div>
                
                <!-- Contenu des sous-onglets -->
                <div id="vacation-requests" class="sub-tab-content active">
                    <div id="all-requests-list" class="loading">Chargement...</div>
                </div>
                
                <div id="sickness-declarations" class="sub-tab-content">
                    <div id="admin-sickness-list" class="loading">Chargement...</div>
                </div>

                <div id="admin-documents" class="sub-tab-content">
                    <div id="admin-documents-list" class="loading">Chargement...</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Scripts modulaires -->
    <script src="/static/js/utils.js"></script>
    <script src="/static/js/auth.js"></script>
    <script src="/static/js/dashboard.js"></script>
    <script src="/static/js/calendar.js"></script>
    <script src="/static/js/admin.js"></script>
    <script src="/static/js/sickness.js"></script>
    <script src="/static/js/main.js"></script>
</body>
</html>''',
            'mime_type': 'text/html'
        },
        '/static/css/styles.css': {
            'content': '''/* Reset et styles de base */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background-color: #f5f5f5;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Header */
.header {
    background-color: #2c3e50;
    color: white;
    padding: 1rem 0;
    margin-bottom: 20px;
    border-radius: 8px;
}

.header h1 {
    text-align: center;
}

/* Sections principales */
.auth-section {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.main-content {
    display: none;
}

/* Navigation par onglets */
.nav-tabs {
    display: flex;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-tab {
    flex: 1;
    padding: 15px;
    background: #ecf0f1;
    border: none;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s;
}

.nav-tab.active {
    background: #3498db;
    color: white;
}

.nav-tab:hover {
    background: #34495e;
    color: white;
}

.tab-content {
    display: none;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.tab-content.active {
    display: block;
}

/* Styles pour les sous-onglets */
.sub-tabs {
    display: flex;
    gap: 2px;
    margin-bottom: 20px;
    border-bottom: 1px solid #ddd;
}

.sub-tab {
    padding: 12px 20px;
    background: #f8f9fa;
    border: none;
    border-radius: 8px 8px 0 0;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: #666;
    transition: all 0.2s;
    border-bottom: 3px solid transparent;
}

.sub-tab:hover {
    background-color: #e9ecef;
    color: #495057;
}

.sub-tab.active {
    background-color: #fff;
    color: #1a73e8;
    border-bottom-color: #1a73e8;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sub-tab-content {
    display: none;
    padding: 20px 0;
}

.sub-tab-content.active {
    display: block;
}

/* Formulaires */
.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.form-group textarea {
    height: 100px;
    resize: vertical;
}

/* Boutons */
.btn {
    background: #3498db;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    margin-right: 10px;
}

.btn:hover {
    background: #2980b9;
}

.btn-success {
    background: #27ae60;
}

.btn-success:hover {
    background: #229954;
}

.btn-danger {
    background: #e74c3c;
}

.btn-danger:hover {
    background: #c0392b;
}

.btn-warning {
    background: #f39c12;
}

.btn-warning:hover {
    background: #d68910;
}

/* Tableaux */
.table {
    width: 100%;
    border-collapse: collapse;
}

.table th,
.table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.table th {
    background-color: #f8f9fa;
    font-weight: bold;
}

/* Badges de statut */
.status-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

.status-en_attente {
    background: #fff3cd;
    color: #856404;
}

.status-approuve {
    background: #d4edda;
    color: #155724;
}

.status-refuse {
    background: #f8d7da;
    color: #721c24;
}

/* Informations utilisateur */
.user-info {
    float: right;
    background: #34495e;
    color: white;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 20px;
}

/* Calendrier */
.calendar {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Alertes */
.alert {
    padding: 15px;
    margin-bottom: 20px;
    border: 1px solid transparent;
    border-radius: 4px;
}

.alert-success {
    color: #155724;
    background-color: #d4edda;
    border-color: #c3e6cb;
}

.alert-error {
    color: #721c24;
    background-color: #f8d7da;
    border-color: #f5c6cb;
}

/* États de chargement */
.loading {
    text-align: center;
    padding: 20px;
    color: #666;
}

/* ========== STYLES CALENDRIER ========== */

.calendar-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    overflow: hidden;
}

.calendar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid #dadce0;
    background-color: #fff;
}

.calendar-nav {
    display: flex;
    align-items: center;
    gap: 16px;
}

.nav-btn {
    background: none;
    border: none;
    padding: 8px;
    border-radius: 50%;
    cursor: pointer;
    color: #5f6368;
    transition: background-color 0.2s;
}

.nav-btn:hover {
    background-color: #f1f3f4;
}

.calendar-actions {
    display: flex;
    align-items: center;
    gap: 16px;
}

.calendar-summary {
    font-size: 14px;
    color: #5f6368;
    background: #f8f9fa;
    padding: 8px 12px;
    border-radius: 4px;
}

/* Vue mensuelle */
.monthly-view {
    padding: 16px;
}

.calendar-grid {
    border: 1px solid #dadce0;
    border-radius: 8px;
    overflow: hidden;
}

.calendar-weekdays {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    background-color: #f8f9fa;
}

.weekday {
    padding: 12px 8px;
    text-align: center;
    font-weight: 500;
    font-size: 14px;
    color: #5f6368;
    border-right: 1px solid #dadce0;
}

.weekday:last-child {
    border-right: none;
}

.calendar-days {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
}

.calendar-day {
    min-height: 120px;
    border-right: 1px solid #dadce0;
    border-bottom: 1px solid #dadce0;
    padding: 8px;
    background: white;
    position: relative;
}

.calendar-day:nth-child(7n) {
    border-right: none;
}

.calendar-day.empty {
    background-color: #f8f9fa;
}

.calendar-day.today {
    background-color: #e3f2fd;
}

.day-number {
    font-weight: 500;
    margin-bottom: 4px;
    color: #202124;
}

.calendar-day.today .day-number {
    background: #1a73e8;
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}

.day-events {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.event {
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 12px;
    cursor: pointer;
    transition: opacity 0.2s;
    border-left: 3px solid;
}

.event:hover {
    opacity: 0.8;
}

/* Couleurs selon le type d'absence */
.event-sickness-declaration {
    background-color: #ffeaa7 !important;
    border-left-color: #fdcb6e !important;
    font-weight: bold;
}

.event-sickness-declaration:hover {
    background-color: #fdcb6e !important;
}

.has-sickness-declaration {
    background-color: #ffeaa7 !important;
    font-weight: bold;
}
.event-vacances {
    background-color: #e8f0fe;
    border-left-color: #4285f4;
    color: #1967d2;
}

/* Variations de couleurs pour les vacances selon le statut */
.event-vacances.event-approuve {
    background-color: #d4edda;
    border-left-color: #28a745;
    color: #155724;
}

.event-vacances.event-en_attente {
    background-color: #fff3cd;
    border-left-color: #ffc107;
    color: #856404;
}

.event-vacances.event-refuse {
    background-color: #f8d7da;
    border-left-color: #dc3545;
    color: #721c24;
}

.event-maladie {
    background-color: #fce8e6;
    border-left-color: #ea4335;
    color: #d93025;
}

/* Variations de couleurs pour les maladies selon le statut */
.event-maladie.event-approuve {
    background-color: #ffebee;
    border-left-color: #f44336;
    color: #c62828;
}

.event-maladie.event-en_attente {
    background-color: #fff8e1;
    border-left-color: #ff9800;
    color: #e65100;
}

.event-maladie.event-refuse {
    background-color: #fafafa;
    border-left-color: #9e9e9e;
    color: #424242;
}

/* Couleurs selon le statut */
.event-en_attente {
    opacity: 0.7;
}

.event-refuse {
    background-color: #fef7e0;
    border-left-color: #f9ab00;
    color: #e37400;
    text-decoration: line-through;
}

/* Vue annuelle */
.yearly-view {
    padding: 24px;
}

.year-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
}

.mini-month {
    background: white;
    border: 1px solid #dadce0;
    border-radius: 8px;
    overflow: hidden;
}

.mini-month-header {
    background: #f8f9fa;
    padding: 12px 16px;
    font-weight: 500;
    color: #202124;
    border-bottom: 1px solid #dadce0;
}

.mini-month-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    padding: 8px;
}

.mini-weekday {
    padding: 4px;
    text-align: center;
    font-size: 12px;
    font-weight: 500;
    color: #5f6368;
}

.mini-day {
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.2s;
    position: relative;
}

.mini-day:hover {
    background-color: #f1f3f4;
}

.mini-day.empty {
    color: #dadce0;
    cursor: default;
}

.mini-day.today {
    background: #1a73e8;
    color: white;
}

.mini-day.has-events {
    font-weight: bold;
}

/* Variations de couleur de fond pour les mini calendriers */
.mini-day.event-vacances.event-approuve {
    background-color: #d4edda !important;
    color: #155724 !important;
}

.mini-day.event-vacances.event-en_attente {
    background-color: #fff3cd !important;
    color: #856404 !important;
}

.mini-day.event-vacances.event-refuse {
    background-color: #f8d7da !important;
    color: #721c24 !important;
}

.mini-day.event-maladie.event-approuve {
    background-color: #ffebee !important;
    color: #c62828 !important;
}

.mini-day.event-maladie.event-en_attente {
    background-color: #fff8e1 !important;
    color: #e65100 !important;
}

.mini-day.event-maladie.event-refuse {
    background-color: #fafafa !important;
    color: #424242 !important;
}

.mini-day.has-sickness-declaration {
    background-color: #ffeaa7 !important;
    color: #856404 !important;
    font-weight: bold;
}

.mini-day.has-events::after {
    content: '';
    position: absolute;
    bottom: 2px;
    left: 50%;
    transform: translateX(-50%);
    width: 4px;
    height: 4px;
    border-radius: 50%;
}

.mini-day.event-vacances.event-approuve::after {
    background-color: #28a745; /* Vert pour vacances approuvées */
}

.mini-day.event-vacances.event-en_attente::after {
    background-color: #ffc107; /* Jaune pour vacances en attente */
}

.mini-day.event-vacances.event-refuse::after {
    background-color: #dc3545; /* Rouge pour vacances refusées */
}

.mini-day.event-maladie.event-approuve::after {
    background-color: #f44336; /* Rouge pour maladie approuvée */
}

.mini-day.event-maladie.event-en_attente::after {
    background-color: #ff9800; /* Orange pour maladie en attente */
}

.mini-day.event-maladie.event-refuse::after {
    background-color: #9e9e9e; /* Gris pour maladie refusée */
}

/* Styles génériques (fallback) */
.mini-day.event-en_attente::after {
    background-color: #f9ab00;
}

.mini-day.event-refuse::after {
    background-color: #9aa0a6;
}

/* Modal des événements */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid #dadce0;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #5f6368;
    padding: 4px;
}

.modal-close:hover {
    background-color: #f1f3f4;
    border-radius: 50%;
}

.modal-body {
    padding: 24px;
}

.event-details {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.detail-row {
    display: flex;
    gap: 12px;
}

.detail-row strong {
    min-width: 80px;
    color: #5f6368;
}

/* Responsive design */
@media (max-width: 768px) {
    .calendar-header {
        flex-direction: column;
        gap: 16px;
        align-items: stretch;
    }
    
    .calendar-actions {
        justify-content: center;
    }
    
    .year-grid {
        grid-template-columns: 1fr;
    }
    
    .calendar-day {
        min-height: 80px;
    }
    
    .event {
        font-size: 10px;
    }
}''',
            'mime_type': 'text/css'
        },
        '/static/js/config.js': {
            'content': '''// Configuration centralisée de l'application
const CONFIG = {
    API_BASE_URL: window.location.origin,
    ALERT_TIMEOUT: 5000,
    DATE_FORMAT: 'fr-FR',
    DATE_INPUT_FORMAT: 'YYYY-MM-DD'
};

// Variables globales (avec restauration depuis le stockage)
let currentUser = null;
let authToken = null;

try {
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('currentUser');
    if (storedToken) authToken = storedToken;
    if (storedUser) currentUser = JSON.parse(storedUser);
} catch (e) {
    // stockage indisponible ou corrompu
}

// Export pour utilisation dans d'autres fichiers
window.CONFIG = CONFIG;
window.currentUser = currentUser;
window.authToken = authToken;

// Variables globales pour compatibilité
window.API_BASE_URL = CONFIG.API_BASE_URL; ''',
            'mime_type': 'text/javascript'
        },
        '/static/js/auth.js': {
            'content': '''// Authentification
async function login(email, password) {
    const body = new URLSearchParams();
    body.append('username', email);
    body.append('password', password);
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body
        });
        
        if (!response.ok) {
            throw new Error('Email ou mot de passe incorrect');
        }
        
        const data = await response.json();
        authToken = data.access_token;
        // Persister le token pour les rechargements
        try {
            localStorage.setItem('authToken', authToken);
        } catch (e) {
            console.warn('Impossible de stocker le token', e);
        }
        
        // Récupérer les infos utilisateur
        currentUser = await apiCall('/users/me');
        // Persister l'utilisateur courant
        try {
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
        } catch (e) {
            console.warn('Impossible de stocker les infos utilisateur', e);
        }
        
        showMainContent();
        showAlert('Connexion réussie !');
        
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    // Nettoyer le localStorage au cas où
    try {
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
    } catch (e) {
        // ignore
    }
    sessionStorage.clear();
    
    // Cacher tous les onglets admin
    const adminTabs = document.querySelectorAll('.admin-only');
    adminTabs.forEach(tab => {
        tab.style.display = 'none';
    });
    
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('main-content').style.display = 'none';
    showAlert('Déconnexion réussie');
    
    // Forcer le rechargement de la page pour éviter les problèmes de cache
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

function showMainContent() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('main-content').style.display = 'block';
    
    // Afficher les infos utilisateur
    const userInfo = document.getElementById('user-info');
    const safeFirst = currentUser && currentUser.first_name ? currentUser.first_name : '';
    const safeLast = currentUser && currentUser.last_name ? currentUser.last_name : '';
    const displayName = (safeFirst || safeLast) ? `${safeFirst} ${safeLast}`.trim() : currentUser.email;
    userInfo.innerHTML = `
        <strong>${displayName}</strong><br>
        <small>${currentUser.email} - ${currentUser.role === 'admin' ? 'Administrateur' : 'Utilisateur'}</small>
    `;
    
    // Forcer l'actualisation de l'interface selon le rôle
    updateUIBasedOnRole();
    
    // Charger le tableau de bord
    loadDashboard();
}

function updateUIBasedOnRole() {
    console.log('Mise à jour UI pour le rôle:', currentUser.role);
    
    // Gérer les onglets admin (afficher pour les admins seulement)
    const adminTabs = document.querySelectorAll('.admin-only');
    adminTabs.forEach(tab => {
        tab.style.display = currentUser.role === 'admin' ? 'block' : 'none';
    });
    
    // Gérer les onglets utilisateur (cacher pour les admins)
    const userTabs = document.querySelectorAll('.user-only');
    userTabs.forEach(tab => {
        tab.style.display = currentUser.role === 'admin' ? 'none' : 'block';
    });
    
    // S'assurer que l'onglet actif est le tableau de bord
    const allTabs = document.querySelectorAll('.nav-tab');
    allTabs.forEach(tab => tab.classList.remove('active'));
    
    const dashboardTab = document.querySelector('.nav-tab[onclick="showTab(\'dashboard\')"]');
    if (dashboardTab) {
        dashboardTab.classList.add('active');
    }
    
    // Afficher le bon contenu
    const allContents = document.querySelectorAll('.tab-content');
    allContents.forEach(content => content.classList.remove('active'));
    
    const dashboardContent = document.getElementById('dashboard');
    if (dashboardContent) {
        dashboardContent.classList.add('active');
    }
}''',
            'mime_type': 'text/javascript'
        },
        '/static/js/dashboard.js': {
            'content': '''// Tableau de bord
async function loadDashboard() {
    const dashboardContent = document.getElementById('dashboard-content');
    
    // Interface différente selon le rôle
    if (currentUser.role === 'admin') {
        // Dashboard pour administrateurs
        let html = '<h3>👨‍💼 Interface Administrateur</h3>';
        
        html += `
            <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin: 20px 0; border-left: 5px solid #34495e;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h4 style="color: #34495e; margin-bottom: 10px;">🔧 Outils d'Administration</h4>
                    <p style="color: #666;">Gérez les utilisateurs et validez les demandes d'absence via les onglets dédiés.</p>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #3498db;">
                        <h5 style="color: #3498db; margin-bottom: 10px;">👥 Utilisateurs</h5>
                        <p style="color: #666; font-size: 14px;">Gérer les comptes utilisateurs</p>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #f39c12;">
                        <h5 style="color: #f39c12; margin-bottom: 10px;">📋 Demandes</h5>
                        <p style="color: #666; font-size: 14px;">Approuver/refuser les demandes</p>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #27ae60;">
                        <h5 style="color: #27ae60; margin-bottom: 10px;">📅 Calendrier</h5>
                        <p style="color: #666; font-size: 14px;">Vue d'ensemble des absences</p>
                    </div>
                    
                </div>
            </div>
        `;
        
        dashboardContent.innerHTML = html;
        
    } else {
        // Dashboard pour utilisateurs normaux
        try {
            // Certaines plateformes (Vercel) exposent l'API sous /api/*
            // On tente d'abord /api/dashboard puis on bascule sur /dashboard/ en fallback pour le dev local
            let dashboardData;
            try {
                dashboardData = await apiCall('/api/dashboard');
            } catch (e) {
                dashboardData = await apiCall('/dashboard/');
            }
            
            // Sécuriser et normaliser les valeurs numériques
            const usedDays = Number(dashboardData.used_leave_days) || 0;
            const totalDays = Number(dashboardData.total_leave_days) || 0;
            const remainingDays = Number(dashboardData.remaining_leave_days ?? (totalDays - usedDays)) || 0;
            
            let html = '<h3>🌴 Compteur de Congés Payés</h3>';
            
            // Calcul du pourcentage de congés utilisés pour la barre de progression
            const percentageUsed = totalDays > 0 ? (usedDays / totalDays) * 100 : 0;
            
            html += `
                <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin: 20px 0; border-left: 5px solid #3498db;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #27ae60;">${remainingDays}</div>
                            <div style="color: #666; font-size: 14px;">Jours restants</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #e74c3c;">${usedDays}</div>
                            <div style="color: #666; font-size: 14px;">Jours utilisés</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #3498db;">${totalDays}</div>
                            <div style="color: #666; font-size: 14px;">Total annuel</div>
                        </div>
                    </div>
                    <div style="background: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #27ae60 0%, #f39c12 70%, #e74c3c 100%); height: 100%; width: ${Math.min(percentageUsed, 100)}%; transition: width 0.3s ease;"></div>
                    </div>
                    <div style="text-align: center; margin-top: 10px; font-size: 14px; color: #666;">
                        ${percentageUsed.toFixed(1)}% des congés utilisés
                    </div>
                </div>
            `;
            
            html += '<h3>📊 Résumé de vos demandes</h3>';
            
            html += `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
                    <div style="background: #f39c12; color: white; padding: 20px; border-radius: 8px; text-align: center;">
                        <h4>En attente</h4>
                        <h2>${Number(dashboardData.pending_requests) || 0}</h2>
                    </div>
                    <div style="background: #27ae60; color: white; padding: 20px; border-radius: 8px; text-align: center;">
                        <h4>Approuvées</h4>
                        <h2>${Number(dashboardData.approved_requests) || 0}</h2>
                    </div>
                </div>
            `;
            
            dashboardContent.innerHTML = html;
            
        } catch (error) {
            dashboardContent.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
        }
    }
}''',
            'mime_type': 'text/javascript'
        },
        '/static/js/calendar.js': {
            'content': '''// Gestion du calendrier (vue mensuelle admin, vue annuelle utilisateur)

class Calendar {
    constructor() {
        this.currentDate = new Date();
        this.currentYear = this.currentDate.getFullYear();
        this.currentMonth = this.currentDate.getMonth();
        this.isAdmin = false;
        this.events = [];
        this.monthNames = [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ];
    }

    async init() {
        this.isAdmin = currentUser && currentUser.role === 'admin';
        
        this.setupEventListeners();
        await this.showCalendar();
    }

    setupEventListeners() {
        const prevBtn = document.getElementById('prev-period');
        const nextBtn = document.getElementById('next-period');
        const todayBtn = document.getElementById('today-btn');
        
        if (prevBtn) prevBtn.addEventListener('click', () => this.navigatePrevious());
        if (nextBtn) nextBtn.addEventListener('click', () => this.navigateNext());
        if (todayBtn) todayBtn.addEventListener('click', () => this.goToToday());

    }

    navigatePrevious() {
        if (this.isAdmin) {
            this.currentMonth--;
            if (this.currentMonth < 0) {
                this.currentMonth = 11;
                this.currentYear--;
            }
        } else {
            this.currentYear--;
        }
        this.showCalendar();
    }

    navigateNext() {
        if (this.isAdmin) {
            this.currentMonth++;
            if (this.currentMonth > 11) {
                this.currentMonth = 0;
                this.currentYear++;
            }
        } else {
            this.currentYear++;
        }
        this.showCalendar();
    }

    goToToday() {
        const today = new Date();
        this.currentYear = today.getFullYear();
        this.currentMonth = today.getMonth();
        this.showCalendar();
    }

    async showCalendar() {
        if (this.isAdmin) {
            await this.showMonthlyView();
        } else {
            await this.showYearlyView();
        }
    }

    async showMonthlyView() {
        document.getElementById('monthly-calendar').style.display = 'block';
        document.getElementById('yearly-calendar').style.display = 'none';
        document.getElementById('calendar-summary').style.display = 'none';

        // Mettre à jour le titre
        const title = `${this.monthNames[this.currentMonth]} ${this.currentYear}`;
        document.getElementById('calendar-title').textContent = title;

        // Charger les événements du mois
        try {
            const data = await apiCall(`/calendar/admin?year=${this.currentYear}&month=${this.currentMonth + 1}`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            this.events = Array.isArray(data) ? data : [];
            this.renderMonthlyCalendar();
        } catch (error) {
            console.error('Erreur:', error);
            showAlert(error.message || 'Erreur lors du chargement du calendrier', 'error');
        }
    }

    async showYearlyView() {
        document.getElementById('monthly-calendar').style.display = 'none';
        document.getElementById('yearly-calendar').style.display = 'block';
        document.getElementById('calendar-summary').style.display = 'block';

        // Mettre à jour le titre
        document.getElementById('calendar-title').textContent = this.currentYear.toString();

        // Charger les événements de l'année et le résumé
        try {
            const [data, summary] = await Promise.all([
                apiCall(`/calendar/user?year=${this.currentYear}`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                }),
                apiCall(`/calendar/summary?year=${this.currentYear}`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                })
            ]);
            this.events = Array.isArray(data) ? data : [];
            
            // Afficher le résumé
            const summaryText = `${summary.used_leave_days}/${summary.total_leave_days} jours utilisés - ${summary.remaining_leave_days} jours restants`;
            document.getElementById('summary-text').textContent = summaryText;

            this.renderYearlyCalendar();
        } catch (error) {
            console.error('Erreur:', error);
            showAlert(error.message || 'Erreur lors du chargement du calendrier', 'error');
        }
    }

    renderMonthlyCalendar() {
        const daysContainer = document.getElementById('calendar-days');
        daysContainer.innerHTML = '';

        const firstDay = new Date(this.currentYear, this.currentMonth, 1);
        const lastDay = new Date(this.currentYear, this.currentMonth + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = (firstDay.getDay() + 6) % 7; // Lundi = 0

        // Ajouter les jours vides du mois précédent
        for (let i = 0; i < startingDayOfWeek; i++) {
            const dayDiv = document.createElement('div');
            dayDiv.className = 'calendar-day empty';
            daysContainer.appendChild(dayDiv);
        }

        // Ajouter les jours du mois
        for (let day = 1; day <= daysInMonth; day++) {
            const dayDiv = document.createElement('div');
            dayDiv.className = 'calendar-day';
            
            const dayNumber = document.createElement('div');
            dayNumber.className = 'day-number';
            dayNumber.textContent = day;
            dayDiv.appendChild(dayNumber);

            // Vérifier si c'est aujourd'hui
            const today = new Date();
            if (today.getFullYear() === this.currentYear && 
                today.getMonth() === this.currentMonth && 
                today.getDate() === day) {
                dayDiv.classList.add('today');
            }

            // Ajouter les événements du jour
            const dayDate = new Date(this.currentYear, this.currentMonth, day);
            const dayEvents = this.getEventsForDate(dayDate);
            
            if (dayEvents.length > 0) {
                const eventsContainer = document.createElement('div');
                eventsContainer.className = 'day-events';
                
                dayEvents.forEach(event => {
                    const eventDiv = document.createElement('div');
                    // Ajouter une classe spéciale pour les déclarations de maladie
                    let eventClass = `event event-${event.status} event-${event.type}`;
                    if (event.event_source === 'sickness_declaration') {
                        eventClass += ' event-sickness-declaration';
                    }
                    eventDiv.className = eventClass;
                    eventDiv.textContent = this.truncateText(event.title, 20);
                    eventDiv.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.showEventModal(event);
                    });
                    eventsContainer.appendChild(eventDiv);
                });
                
                dayDiv.appendChild(eventsContainer);
            }

            daysContainer.appendChild(dayDiv);
        }
    }

    renderYearlyCalendar() {
        const yearGrid = document.querySelector('.year-grid');
        if (!yearGrid) {
            console.error('Element .year-grid not found!');
            return;
        }
        yearGrid.innerHTML = '';
        


        for (let month = 0; month < 12; month++) {
            const monthDiv = document.createElement('div');
            monthDiv.className = 'mini-month';
            
            const monthHeader = document.createElement('div');
            monthHeader.className = 'mini-month-header';
            monthHeader.textContent = this.monthNames[month];
            monthDiv.appendChild(monthHeader);

            const monthGrid = document.createElement('div');
            monthGrid.className = 'mini-month-grid';
            
            // En-têtes des jours de la semaine (version courte)
            const weekdays = ['L', 'M', 'M', 'J', 'V', 'S', 'D'];
            weekdays.forEach(day => {
                const weekdayDiv = document.createElement('div');
                weekdayDiv.className = 'mini-weekday';
                weekdayDiv.textContent = day;
                monthGrid.appendChild(weekdayDiv);
            });

            // Jours du mois
            const firstDay = new Date(this.currentYear, month, 1);
            const lastDay = new Date(this.currentYear, month + 1, 0);
            const daysInMonth = lastDay.getDate();
            const startingDayOfWeek = (firstDay.getDay() + 6) % 7;

            // Jours vides
            for (let i = 0; i < startingDayOfWeek; i++) {
                const emptyDiv = document.createElement('div');
                emptyDiv.className = 'mini-day empty';
                monthGrid.appendChild(emptyDiv);
            }

            // Jours du mois
            for (let day = 1; day <= daysInMonth; day++) {
                const dayDiv = document.createElement('div');
                dayDiv.className = 'mini-day';
                dayDiv.textContent = day;

                // Vérifier si c'est aujourd'hui
                const today = new Date();
                if (today.getFullYear() === this.currentYear && 
                    today.getMonth() === month && 
                    today.getDate() === day) {
                    dayDiv.classList.add('today');
                }

                // Vérifier s'il y a des événements
                const dayDate = new Date(this.currentYear, month, day);
                const dayEvents = this.getEventsForDate(dayDate);
                
                if (dayEvents.length > 0) {
                    dayDiv.classList.add('has-events');
                    // Ajouter une classe pour le type d'événement principal
                    const primaryEvent = dayEvents[0];
                    dayDiv.classList.add(`event-${primaryEvent.status}`, `event-${primaryEvent.type}`);
                    
                    // Ajouter une classe spéciale si c'est une déclaration de maladie
                    if (primaryEvent.event_source === 'sickness_declaration') {
                        dayDiv.classList.add('has-sickness-declaration');
                    }
                    
                    // Ajouter un tooltip ou gérer le clic
                    dayDiv.title = dayEvents.map(e => e.title).join('\n');
                    dayDiv.addEventListener('click', () => {
                        if (dayEvents.length === 1) {
                            this.showEventModal(dayEvents[0]);
                        } else {
                            // Afficher une liste des événements
                            this.showMultipleEventsModal(dayEvents, dayDate);
                        }
                    });
                }

                monthGrid.appendChild(dayDiv);
            }

            monthDiv.appendChild(monthGrid);
            yearGrid.appendChild(monthDiv);
        }
    }

    getEventsForDate(date) {
        if (!Array.isArray(this.events)) return [];
        return this.events.filter(event => {
            // Utiliser les dates en format string pour éviter les problèmes de fuseau horaire
            const dateStr = date.toISOString().split('T')[0]; // Format YYYY-MM-DD
            const eventStart = event.start; // Déjà en format YYYY-MM-DD
            const eventEnd = event.end; // Déjà en format YYYY-MM-DD
            
            return dateStr >= eventStart && dateStr <= eventEnd;
        });
    }

    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    showEventModal(event) {
        document.getElementById('event-title').textContent = event.title;
        document.getElementById('event-user').textContent = event.user_name;
        
        // Différencier l'affichage selon le type d'événement
        if (event.event_source === 'sickness_declaration') {
            document.getElementById('event-type').textContent = 'Déclaration de maladie';
        } else {
            document.getElementById('event-type').textContent = event.type === 'vacances' ? 'Vacances' : 'Maladie';
        }
        
        const startDate = new Date(event.start).toLocaleDateString('fr-FR');
        const endDate = new Date(event.end).toLocaleDateString('fr-FR');
        document.getElementById('event-dates').textContent = startDate === endDate ? startDate : `${startDate} - ${endDate}`;
        
        // Affichage du statut différent pour les déclarations de maladie
        if (event.event_source === 'sickness_declaration') {
            const emailSent = event.title.includes('✉️');
            document.getElementById('event-status').textContent = emailSent ? 'Email envoyé' : 'Email non envoyé';
        } else {
            const statusText = {
                'en_attente': 'En attente',
                'approuve': 'Approuvé',
                'refuse': 'Refusé'
            }[event.status] || event.status;
            document.getElementById('event-status').textContent = statusText;
        }
        
        const reasonRow = document.getElementById('event-reason-row');
        if (event.reason) {
            document.getElementById('event-reason').textContent = event.reason;
            reasonRow.style.display = 'block';
        } else {
            reasonRow.style.display = 'none';
        }

        document.getElementById('event-modal').style.display = 'flex';

        // Activer les actions admin pour les demandes d'absence uniquement
        const isAdmin = currentUser && currentUser.role === 'admin';
        const actionsRow = document.querySelector('#event-modal .admin-only');
        const editBtn = document.getElementById('event-edit-btn');
        const deleteBtn = document.getElementById('event-delete-btn');
        const editForm = document.getElementById('event-edit-form');
        const deleteConfirm = document.getElementById('event-delete-confirm');
        const editStart = document.getElementById('edit-start-date');
        const editEnd = document.getElementById('edit-end-date');
        const editReason = document.getElementById('edit-reason');
        const editStatus = document.getElementById('edit-status');
        const editCancel = document.getElementById('event-edit-cancel');
        const deleteCancel = document.getElementById('event-delete-cancel');
        const deleteConfirmBtn = document.getElementById('event-delete-confirm-btn');
        if (actionsRow && editBtn && deleteBtn) {
            if (isAdmin && event.event_source === 'absence_request') {
                actionsRow.style.display = 'flex';
                // Préremplir le formulaire d'édition
                if (editForm && editStart && editEnd && editReason && editStatus) {
                    editForm.style.display = 'none';
                    deleteConfirm.style.display = 'none';
                    editStart.value = event.start;
                    editEnd.value = event.end;
                    editReason.value = event.reason || '';
                    editStatus.value = event.status || 'en_attente';

                    editForm.onsubmit = (e) => {
                        e.preventDefault();
                        const newStart = editStart.value;
                        const newEnd = editEnd.value;
                        if (!newStart || !newEnd) return;
                        if (new Date(newStart) > new Date(newEnd)) { showAlert('La date de fin doit être postérieure à la date de début', 'error'); return; }
                        const payload = {
                            start_date: newStart,
                            end_date: newEnd,
                            reason: (editReason.value || null),
                            status: editStatus.value
                        };
                        this.updateAbsence(event.id, payload);
                    };
                    if (editCancel) editCancel.onclick = () => { editForm.style.display = 'none'; };
                }
                if (editBtn) editBtn.onclick = () => {
                    if (deleteConfirm) deleteConfirm.style.display = 'none';
                    if (editForm) editForm.style.display = 'block';
                };
                if (deleteBtn) deleteBtn.onclick = () => {
                    if (editForm) editForm.style.display = 'none';
                    if (deleteConfirm) deleteConfirm.style.display = 'block';
                };
                if (deleteCancel) deleteCancel.onclick = () => { if (deleteConfirm) deleteConfirm.style.display = 'none'; };
                if (deleteConfirmBtn) deleteConfirmBtn.onclick = () => this.confirmDelete(event);
            } else {
                actionsRow.style.display = 'none';
                if (editBtn) editBtn.onclick = null;
                if (deleteBtn) deleteBtn.onclick = null;
                if (editForm) editForm.style.display = 'none';
                if (deleteConfirm) deleteConfirm.style.display = 'none';
            }
        }
    }

    

    showMultipleEventsModal(events, date) {
        // Pour simplifier, on affiche juste le premier événement
        // Dans une vraie app, on pourrait créer une modal spéciale pour plusieurs événements
        this.showEventModal(events[0]);
    }

    async confirmDelete(event) {
        try {
            await apiCall(`/absence-requests/admin/${event.id}`, { method: 'DELETE' });
            showAlert('Absence supprimée');
            closeEventModal();
            await this.showCalendar();
            if (typeof window.loadAllRequests === 'function') { window.loadAllRequests(); }
        } catch (e) {
            showAlert(e.message || 'Erreur suppression', 'error');
        }
    }

    // openEditDialog supprimé au profit du formulaire intégré

    async updateAbsence(id, payload) {
        try {
            await apiCall(`/absence-requests/admin/${id}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            showAlert('Absence mise à jour');
            closeEventModal();
            await this.showCalendar();
            if (typeof window.loadAllRequests === 'function') { window.loadAllRequests(); }
        } catch (e) {
            showAlert(e.message || 'Erreur mise à jour', 'error');
        }
    }
}

function closeEventModal() {
    document.getElementById('event-modal').style.display = 'none';
}

// Initialiser le calendrier quand la section est affichée
let calendar = null;

async function showCalendarSection() {
    const calendarSection = document.getElementById('calendar-section');
    if (!calendarSection) {
        console.error('calendar-section element not found!');
        return;
    }
    
    calendarSection.style.display = 'block';
    
    if (!calendar) {
        calendar = new Calendar();
        await calendar.init();
    } else {
        await calendar.showCalendar();
    }
}''',
            'mime_type': 'text/javascript'
        },
        '/static/js/admin.js': {
            'content': '''// Fonctions administrateur
async function loadUsers() {
    const usersList = document.getElementById('users-list');
    
    try {
        const users = await apiCall('/users/');
        
        let html = '<table class="table"><thead><tr><th>Email</th><th>Nom</th><th>Rôle</th><th>Statut</th><th>Congés</th><th>Actions</th></tr></thead><tbody>';
        
        users.forEach(user => {
            // Ne pas permettre à l'admin de gérer son propre compte
            const isCurrentUser = currentUser && user.id === currentUser.id;
            const isAdmin = user.role === 'admin';
            
            let actionsHtml;
            if (isCurrentUser) {
                actionsHtml = '<span class="text-muted">Compte actuel</span>';
            } else if (isAdmin) {
                // Pour les autres admins, ne pas afficher le bouton Détails
                actionsHtml = `<button class="btn btn-warning" onclick="editUser(${user.id})">Modifier</button>
                               <button class="btn btn-danger" onclick="deleteUser(${user.id})">Supprimer</button>`;
            } else {
                // Pour les utilisateurs normaux, afficher tous les boutons
                actionsHtml = `<button class="btn btn-info" onclick="showUserAbsenceSummary(${user.id})" title="Voir le résumé des absences">📊 Détails</button>
                               <button class="btn btn-warning" onclick="editUser(${user.id})">Modifier</button>
                               <button class="btn btn-danger" onclick="deleteUser(${user.id})">Supprimer</button>`;
            }
            
            // Ne pas afficher le décompte de congés pour les administrateurs
            const leaveDisplay = user.role === 'admin' ? 
                '<span class="text-muted">—</span>' : 
                `${user.annual_leave_days || 25} jours`;
            
            html += `
                <tr>
                    <td>${user.email}</td>
                    <td>${user.first_name} ${user.last_name}</td>
                    <td>${user.role === 'admin' ? 'Administrateur' : 'Utilisateur'}</td>
                    <td><span class="status-badge ${user.is_active ? 'status-approuve' : 'status-refuse'}">${user.is_active ? 'Actif' : 'Inactif'}</span></td>
                    <td>${leaveDisplay}</td>
                    <td>
                        ${actionsHtml}
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        usersList.innerHTML = html;
        
    } catch (error) {
        usersList.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    }
}

async function loadAllRequests() {
    const requestsList = document.getElementById('all-requests-list');
    
    try {
        let requests = await apiCall('/absence-requests/all');

        // Si l'API renvoie un objet d'erreur → afficher l'erreur, sinon fallback sur tableau vide
        if (!Array.isArray(requests)) {
            if (requests && (requests.error || requests.detail)) {
                const msg = requests.error || requests.detail;
                requestsList.innerHTML = `<div class="alert alert-error">${msg}</div>`;
                return;
            }
            requests = [];
        }

        if (requests.length === 0) {
            requestsList.innerHTML = '<div class="alert alert-info">Aucune demande de vacances pour le moment.</div>';
            return;
        }
        
        let html = '<h3>🏖️ Demandes de Vacances</h3>';
        
        // Statistiques rapides (sécurisées)
        const arr = Array.isArray(requests) ? requests : [];
        const totalRequests = arr.length;
        const pendingRequests = arr.filter(r => r.status === 'en_attente').length;
        const approvedRequests = arr.filter(r => r.status === 'approuve').length;
        const rejectedRequests = arr.filter(r => r.status === 'refuse').length;
        
        html += `
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; text-align: center;">
                    <div>
                        <div style="font-size: 20px; font-weight: bold; color: #3498db;">${totalRequests}</div>
                        <div style="color: #666; font-size: 12px;">Total</div>
                    </div>
                    <div>
                        <div style="font-size: 20px; font-weight: bold; color: ${pendingRequests > 0 ? '#f39c12' : '#27ae60'};">${pendingRequests}</div>
                        <div style="color: #666; font-size: 12px;">En attente</div>
                    </div>
                    <div>
                        <div style="font-size: 20px; font-weight: bold; color: #27ae60;">${approvedRequests}</div>
                        <div style="color: #666; font-size: 12px;">Approuvées</div>
                    </div>
                    <div>
                        <div style="font-size: 20px; font-weight: bold; color: #e74c3c;">${rejectedRequests}</div>
                        <div style="color: #666; font-size: 12px;">Refusées</div>
                    </div>
                </div>
            </div>
        `;
        
        html += '<table class="table"><thead><tr><th>👤 Utilisateur</th><th>📅 Période</th><th>📝 Raison</th><th>📊 Statut</th><th>🕐 Créée le</th><th>⚡ Actions</th></tr></thead><tbody>';
        
        arr.forEach(request => {
            const startDate = formatDateSafe(request.start_date);
            const endDate = formatDateSafe(request.end_date);
            const createdDate = formatDateSafe(request.created_at);
            
            // Style de la ligne selon le statut
            let rowStyle = '';
            if (request.status === 'en_attente') {
                rowStyle = 'background-color: #fff3cd; border-left: 3px solid #ffc107;';
            } else if (request.status === 'refuse') {
                rowStyle = 'background-color: #f8d7da; border-left: 3px solid #dc3545;';
            }
            
            // Actions possibles
            let actions = '';
            if (request.status === 'en_attente') {
                actions = `<button class="btn btn-sm btn-success" onclick="approveRequest(${request.id})" title="Approuver la demande">✅ Approuver</button>
                           <button class="btn btn-sm btn-danger" onclick="rejectRequest(${request.id})" title="Refuser la demande">❌ Refuser</button>`;
            } else {
                actions = '<span style="color: #666;">—</span>';
            }
            
            const userDisplay = request.user ? `<strong>${request.user.first_name} ${request.user.last_name}</strong><br><small style="color: #666;">${request.user.email}</small>` : '<span style="color:#e74c3c">Utilisateur inconnu</span>';
            html += `
                <tr style="${rowStyle}">
                    <td>${userDisplay}</td>
                    <td><strong>${startDate === endDate ? startDate : `${startDate} - ${endDate}`}</strong></td>
                    <td>${request.reason ? `<em>"${request.reason}"</em>` : '<span style="color: #999;">Non spécifiée</span>'}</td>
                    <td><span class="status-badge status-${request.status}">${request.status.replace('_', ' ')}</span></td>
                    <td><small>${createdDate}</small></td>
                    <td>${actions}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        requestsList.innerHTML = html;
        
    } catch (error) {
        requestsList.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    }
}

// Fonctions pour le formulaire d'absence admin
async function showAdminAbsenceForm() {
    const modal = document.getElementById('admin-absence-modal');
    modal.style.display = 'flex';
    
    // Charger la liste des utilisateurs
    try {
        const users = await apiCall('/users/');
        const userSelect = document.getElementById('admin-absence-user');
        userSelect.innerHTML = '<option value="">Sélectionner un utilisateur...</option>';
        
        users.forEach(user => {
            // Ne pas inclure les admins dans la liste
            if (user.role !== 'admin') {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = `${user.first_name} ${user.last_name} (${user.email})`;
                userSelect.appendChild(option);
            }
        });
        
        // Définir les dates par défaut
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        document.getElementById('admin-start-date').value = tomorrow.toISOString().split('T')[0];
        document.getElementById('admin-end-date').value = tomorrow.toISOString().split('T')[0];
        // Gérer l'option PDF si type maladie
        const typeSelect = document.getElementById('admin-absence-type');
        const pdfGroup = document.getElementById('admin-absence-pdf-group');
        const dropzone = document.getElementById('admin-absence-dropzone');
        const fileInput = document.getElementById('admin-absence-pdf');
        const fileName = document.getElementById('admin-absence-pdf-name');
        const syncVisibility = () => { if (pdfGroup) pdfGroup.style.display = typeSelect.value === 'maladie' ? 'block' : 'none'; };
        if (typeSelect) typeSelect.onchange = syncVisibility;
        syncVisibility();
        if (dropzone && fileInput) {
            dropzone.onclick = () => fileInput.click();
            dropzone.ondragover = (e) => { e.preventDefault(); dropzone.style.background = '#fff8e1'; };
            dropzone.ondragleave = () => { dropzone.style.background = '#fff8e1'; };
            dropzone.ondrop = (e) => {
                e.preventDefault();
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    fileInput.files = e.dataTransfer.files;
                    if (fileName) fileName.textContent = e.dataTransfer.files[0].name;
                }
            };
            fileInput.onchange = () => { if (fileName && fileInput.files && fileInput.files[0]) fileName.textContent = fileInput.files[0].name; };
        }
        
    } catch (error) {
        showAlert('Erreur lors du chargement des utilisateurs: ' + error.message, 'error');
    }
}

function hideAdminAbsenceForm() {
    const modal = document.getElementById('admin-absence-modal');
    modal.style.display = 'none';
    document.getElementById('admin-absence-form-element').reset();
}

// Admin Sickness modal controls
function showAdminSicknessForm() {
    const modal = document.getElementById('admin-sickness-modal');
    modal.style.display = 'flex';
    (async () => {
        try {
            const users = await apiCall('/users/');
            const userSelect = document.getElementById('admin-sickness-user');
            userSelect.innerHTML = '<option value="">Sélectionner un utilisateur...</option>';
            users.forEach(user => {
                if (user.role !== 'admin') {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = `${user.first_name} ${user.last_name} (${user.email})`;
                    userSelect.appendChild(option);
                }
            });
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('admin-sickness-start').value = today;
            document.getElementById('admin-sickness-end').value = today;
        } catch (e) { showAlert('Erreur chargement utilisateurs: ' + e.message, 'error'); }
    })();

    // Dropzone click/drag
    const dropzone = document.getElementById('admin-sickness-dropzone');
    const fileInput = document.getElementById('admin-sickness-pdf');
    dropzone.onclick = () => fileInput.click();
    dropzone.ondragover = (e) => { e.preventDefault(); dropzone.style.background = '#fffbeb'; };
    dropzone.ondragleave = () => { dropzone.style.background = '#fff8e1'; };
    dropzone.ondrop = (e) => {
        e.preventDefault();
        dropzone.style.background = '#fff8e1';
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            fileInput.files = e.dataTransfer.files;
        }
    };
}

function hideAdminSicknessForm() {
    const modal = document.getElementById('admin-sickness-modal');
    modal.style.display = 'none';
    const form = document.getElementById('admin-sickness-form');
    if (form) form.reset();
}

// Submission handler for admin sickness
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-sickness-form');
    if (!form) return;
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const userId = parseInt(document.getElementById('admin-sickness-user').value);
        const start = document.getElementById('admin-sickness-start').value;
        const end = document.getElementById('admin-sickness-end').value;
        const desc = document.getElementById('admin-sickness-description').value;
        const pdf = document.getElementById('admin-sickness-pdf').files[0];
        if (!userId) return showAlert('Sélectionnez un utilisateur', 'error');
        if (!start || !end) return showAlert('Dates requises', 'error');
        if (new Date(start) > new Date(end)) return showAlert('La date de fin doit être postérieure', 'error');
        if (!pdf) return showAlert('Sélectionnez un PDF', 'error');
        if (pdf.type !== 'application/pdf') return showAlert('PDF uniquement', 'error');
        if (pdf.size > 10 * 1024 * 1024) return showAlert('PDF > 10MB', 'error');

        const fd = new FormData();
        fd.append('user_id', String(userId));
        fd.append('start_date', start);
        fd.append('end_date', end);
        if (desc) fd.append('description', desc);
        fd.append('pdf_file', pdf);

        try {
            await fetch(`${CONFIG.API_BASE_URL}/sickness-declarations/admin`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${authToken}` },
                body: fd
            }).then(async r => { if (!r.ok) throw new Error((await r.json()).detail || 'Erreur'); });
            showAlert("Arrêt maladie créé et email envoyé.", 'success');
            hideAdminSicknessForm();
            if (calendar && currentUser.role === 'admin') await calendar.showCalendar();
        } catch (err) {
            showAlert(err.message, 'error');
        }
    });
});

// Expose
window.showAdminSicknessForm = showAdminSicknessForm;
window.hideAdminSicknessForm = hideAdminSicknessForm;
// Fermer la modal en cliquant à l'extérieur
document.addEventListener('DOMContentLoaded', function() {
    const adminAbsenceModal = document.getElementById('admin-absence-modal');
    if (adminAbsenceModal) {
        adminAbsenceModal.addEventListener('click', function(e) {
            if (e.target === adminAbsenceModal) {
                hideAdminAbsenceForm();
            }
        });
    }
});

// Gestionnaire de soumission du formulaire admin
document.addEventListener('DOMContentLoaded', function() {
    const adminAbsenceForm = document.getElementById('admin-absence-form-element');
    if (adminAbsenceForm) {
        adminAbsenceForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const reasonEl = document.getElementById('admin-reason');
            const formData = {
                user_id: parseInt(document.getElementById('admin-absence-user').value),
                type: document.getElementById('admin-absence-type').value,
                start_date: document.getElementById('admin-start-date').value,
                end_date: document.getElementById('admin-end-date').value,
                reason: reasonEl ? (reasonEl.value || null) : null,
                admin_comment: document.getElementById('admin-comment').value || null,
                status: 'approuve'
            };
            
            if (!formData.user_id) {
                showAlert('Veuillez sélectionner un utilisateur', 'error');
                return;
            }
            
            if (new Date(formData.start_date) > new Date(formData.end_date)) {
                showAlert('La date de fin doit être postérieure à la date de début', 'error');
                return;
            }
            
            try {
                const typeVal = document.getElementById('admin-absence-type').value;
                if (typeVal === 'maladie') {
                    const pdf = document.getElementById('admin-absence-pdf')?.files?.[0];
                    if (!pdf) { showAlert('Veuillez joindre un PDF pour un arrêt maladie', 'error'); return; }
                    if (pdf.type !== 'application/pdf') { showAlert('PDF uniquement', 'error'); return; }
                    if (pdf.size > 10 * 1024 * 1024) { showAlert('PDF > 10MB', 'error'); return; }
                    const fd = new FormData();
                    fd.append('user_id', String(formData.user_id));
                    fd.append('start_date', formData.start_date);
                    fd.append('end_date', formData.end_date);
                    if (formData.reason) fd.append('description', formData.reason);
                    fd.append('pdf_file', pdf);
                    await fetch(`${CONFIG.API_BASE_URL}/sickness-declarations/admin`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${authToken}` },
                        body: fd
                    }).then(async r => { if (!r.ok) throw new Error((await r.json()).detail || 'Erreur'); });
                    showAlert('Arrêt maladie créé et email envoyé.', 'success');
                } else {
                    await apiCall('/absence-requests/admin', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });
                    showAlert('Absence créée avec succès', 'success');
                }
                hideAdminAbsenceForm();
                if (calendar && currentUser.role === 'admin') {
                    await calendar.showCalendar();
                }
            } catch (error) {
                showAlert('Erreur lors de la création de l\'absence: ' + error.message, 'error');
            }
        });
    }
});

// Fonction pour afficher le résumé des absences d'un utilisateur
async function showUserAbsenceSummary(userId) {
    const modal = document.getElementById('user-absence-modal');
    const summaryDiv = document.getElementById('user-absence-summary');
    
    modal.style.display = 'flex';
    summaryDiv.innerHTML = '<div class="loading">Chargement...</div>';
    
    try {
        const summary = await apiCall(`/users/${userId}/absence-summary`);
        if (!summary || summary.error || !summary.user) {
            const message = (summary && (summary.error || summary.detail)) ? (summary.error || summary.detail) : 'Résumé introuvable';
            summaryDiv.innerHTML = `<div class="alert alert-error">Erreur: ${message}</div>`;
            return;
        }
        
        const user = summary.user;
        document.getElementById('user-absence-title').textContent = 
            `Résumé des absences - ${user.first_name} ${user.last_name}`;
        
        let html = `
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h4 style="color: #34495e; margin-bottom: 15px;">📊 Statistiques générales</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 15px;">
                    <div style="text-align: center; background: white; padding: 15px; border-radius: 8px; border: 2px solid #3498db;">
                        <div style="font-size: 24px; font-weight: bold; color: #3498db;">${summary.total_absence_days}</div>
                        <div style="color: #666; font-size: 14px;">Jours d'absence total</div>
                    </div>
                    <div style="text-align: center; background: white; padding: 15px; border-radius: 8px; border: 2px solid #27ae60;">
                        <div style="font-size: 24px; font-weight: bold; color: #27ae60;">${summary.vacation_days}</div>
                        <div style="color: #666; font-size: 14px;">Jours de vacances</div>
                    </div>
                    <div style="text-align: center; background: white; padding: 15px; border-radius: 8px; border: 2px solid #e74c3c;">
                        <div style="font-size: 24px; font-weight: bold; color: #e74c3c;">${summary.sick_days}</div>
                        <div style="color: #666; font-size: 14px;">Jours de maladie</div>
                    </div>
                    <div style="text-align: center; background: white; padding: 15px; border-radius: 8px; border: 2px solid #f39c12;">
                        <div style="font-size: 24px; font-weight: bold; color: #f39c12;">${summary.pending_requests}</div>
                        <div style="color: #666; font-size: 14px;">En attente</div>
                    </div>
                    <div style="text-align: center; background: white; padding: 15px; border-radius: 8px; border: 2px solid #9b59b6;">
                        <div style="font-size: 24px; font-weight: bold; color: #9b59b6;">${summary.approved_requests}</div>
                        <div style="color: #666; font-size: 14px;">Approuvées</div>
                    </div>
                </div>
            </div>
        `;
        
        if (Array.isArray(summary.recent_absences) && summary.recent_absences.length > 0) {
            html += `
                <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd;">
                    <h4 style="color: #34495e; margin-bottom: 15px;">📅 Absences récentes</h4>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Période</th>
                                <th>Statut</th>
                                <th>Raison</th>
                                <th>Créée le</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            summary.recent_absences.forEach(absence => {
                const startDate = new Date(absence.start_date).toLocaleDateString('fr-FR');
                const endDate = new Date(absence.end_date).toLocaleDateString('fr-FR');
                const createdDate = new Date(absence.created_at).toLocaleDateString('fr-FR');
                
                const statusText = {
                    'en_attente': 'En attente',
                    'approuve': 'Approuvé',
                    'refuse': 'Refusé'
                }[absence.status] || absence.status;
                
                const typeText = absence.type === 'vacances' ? 'Vacances' : 'Maladie';
                
                html += `
                    <tr>
                        <td><span class="status-badge event-${absence.type}">${typeText}</span></td>
                        <td>${startDate === endDate ? startDate : `${startDate} - ${endDate}`}</td>
                        <td><span class="status-badge status-${absence.status}">${statusText}</span></td>
                        <td>${absence.reason || 'Non spécifiée'}</td>
                        <td>${createdDate}</td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            html += `
                <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd; text-align: center;">
                    <p style="color: #666; margin: 0;">Aucune absence enregistrée pour cet utilisateur.</p>
                </div>
            `;
        }
        
        summaryDiv.innerHTML = html;
        
    } catch (error) {
        summaryDiv.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    }
}

function closeUserAbsenceModal() {
    document.getElementById('user-absence-modal').style.display = 'none';
}

// Fonction pour charger les déclarations de maladie (admin)
async function loadAdminSicknessDeclarations() {
    const sicknessListDiv = document.getElementById('admin-sickness-list');
    
    try {
        sicknessListDiv.innerHTML = '<div class="loading">Chargement...</div>';
        const html = await loadAllSicknessDeclarations();
        sicknessListDiv.innerHTML = html;
        
    } catch (error) {
        sicknessListDiv.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    }
}

// Documents (liste consolidée des PDFs de maladie)
async function loadAdminDocuments() {
    const container = document.getElementById('admin-documents-list');
    if (!container) return;
    try {
        container.innerHTML = '<div class="loading">Chargement...</div>';
        const declarations = await apiCall('/sickness-declarations/');
        const withPdf = declarations.filter(d => d.pdf_filename);
        if (withPdf.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Aucun document disponible.</div>';
            return;
        }
        let html = '<h3>📄 Documents déposés</h3>';
        html += '<table class="table"><thead><tr><th>Nom du fichier</th><th>Utilisateur</th><th>Période</th><th>Créé le</th><th>Action</th></tr></thead><tbody>';
        withPdf.forEach(d => {
            const startDate = formatDateSafe(d.start_date);
            const endDate = formatDateSafe(d.end_date);
            const createdDate = formatDateSafe(d.created_at);
            const url = `${CONFIG.API_BASE_URL}/sickness-declarations/${d.id}/pdf`;
            html += `<tr>
                <td>${d.pdf_filename}</td>
                <td>${d.user ? `${d.user.first_name} ${d.user.last_name} (${d.user.email})` : '—'}</td>
                <td>${startDate === endDate ? startDate : `${startDate} - ${endDate}`}</td>
                <td>${createdDate}</td>
                <td><a class="btn" href="${url}" target="_blank" rel="noopener">Ouvrir</a></td>
            </tr>`;
        });
        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = `<div class="alert alert-error">Erreur: ${e.message}</div>`;
    }
}

async function approveRequest(requestId) {
    try {
        await apiCall(`/absence-requests/${requestId}/status`, {
            method: 'PUT',
            body: JSON.stringify({
                status: 'approuve',
                admin_comment: 'Demande approuvée'
            })
        });
        
        showAlert('Demande approuvée !');
        loadAllRequests();
        if (calendar && currentUser.role === 'admin') await calendar.showCalendar();
        
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

async function rejectRequest(requestId) {
    const reason = prompt('Raison du refus (optionnel):');
    
    try {
        await apiCall(`/absence-requests/${requestId}/status`, {
            method: 'PUT',
            body: JSON.stringify({
                status: 'refuse',
                admin_comment: reason || 'Demande refusée'
            })
        });
        
        showAlert('Demande refusée.');
        loadAllRequests();
        if (calendar && currentUser.role === 'admin') await calendar.showCalendar();
        
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

async function editUser(userId) {
    try {
        const user = await apiCall(`/users/${userId}`);
        
        // Remplir le formulaire avec les données existantes
        document.getElementById('user-email').value = user.email;
        document.getElementById('user-first-name').value = user.first_name;
        document.getElementById('user-last-name').value = user.last_name;
        document.getElementById('user-role').value = user.role;
        
        // Changer le formulaire en mode édition
        const form = document.getElementById('user-form');
        form.setAttribute('data-edit-id', userId);
        
        showNewUserForm();
        
    } catch (error) {
        showAlert(error.message, 'error');
    }
}

async function deleteUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
        return;
    }
    
    try {
        await apiCall(`/users/${userId}`, {
            method: 'DELETE'
        });
        
        showAlert('Utilisateur supprimé avec succès !');
        loadUsers();
        
    } catch (error) {
        showAlert(error.message, 'error');
    }
}''',
            'mime_type': 'text/javascript'
        },
        '/static/js/sickness.js': {
            'content': '''// Fonctions pour les déclarations de maladie

function showSicknessDeclarationForm() {
    // Fermer le formulaire de demande de congé s'il est ouvert
    hideNewRequestForm();
    
    document.getElementById('sickness-declaration-form').style.display = 'block';
    
    // Définir la date par défaut à aujourd'hui
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('sickness-start-date').value = today;
    document.getElementById('sickness-end-date').value = today;
}

function hideSicknessDeclarationForm() {
    document.getElementById('sickness-declaration-form').style.display = 'none';
    document.getElementById('sickness-form').reset();
}

// Gestionnaire de soumission du formulaire de déclaration de maladie
document.addEventListener('DOMContentLoaded', function() {
    const sicknessForm = document.getElementById('sickness-form');
    if (sicknessForm) {
        sicknessForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const startDate = document.getElementById('sickness-start-date').value;
            const endDate = document.getElementById('sickness-end-date').value;
            const description = document.getElementById('sickness-description').value;
            const pdfFile = document.getElementById('sickness-pdf').files[0];
            
            // Validations
            if (!startDate || !endDate) {
                showAlert('Veuillez sélectionner les dates de début et de fin', 'error');
                return;
            }
            
            if (new Date(startDate) > new Date(endDate)) {
                showAlert('La date de fin doit être postérieure à la date de début', 'error');
                return;
            }
            
            if (!pdfFile) {
                showAlert('Veuillez sélectionner un fichier PDF', 'error');
                return;
            }
            
            if (pdfFile.type !== 'application/pdf') {
                showAlert('Seuls les fichiers PDF sont acceptés', 'error');
                return;
            }
            
            if (pdfFile.size > 10 * 1024 * 1024) { // 10MB
                showAlert('Le fichier est trop volumineux (maximum 10MB)', 'error');
                return;
            }
            
            // Préparer les données du formulaire
            const formData = new FormData();
            formData.append('start_date', startDate);
            formData.append('end_date', endDate);
            formData.append('description', description);
            formData.append('pdf_file', pdfFile);
            
            try {
                // Désactiver le bouton de soumission
                const submitBtn = e.target.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                submitBtn.disabled = true;
                submitBtn.textContent = '📧 Envoi en cours...';
                
                const response = await fetch(`${CONFIG.API_BASE_URL}/sickness-declarations/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Erreur lors de l\'envoi de la déclaration');
                }
                
                 const result = await response.json();
                
                showAlert('Déclaration de maladie envoyée avec succès ! Email envoyé aux administrateurs.', 'success');
                hideSicknessDeclarationForm();
                
                // Recharger la liste des demandes si on est sur l'onglet procédure
                if (document.getElementById('procedure').classList.contains('active')) {
                    loadRequests();
                }
                
            } catch (error) {
                showAlert('Erreur lors de l\'envoi de la déclaration: ' + error.message, 'error');
            } finally {
                // Réactiver le bouton
                const submitBtn = e.target.querySelector('button[type="submit"]');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
});

// Fonction pour charger les déclarations de maladie de l'utilisateur
async function loadSicknessDeclarations() {
    try {
        const declarations = await apiCall('/sickness-declarations/');
        
        let html = '<h3>Mes déclarations de maladie</h3>';
        
        if (declarations.length === 0) {
            html += '<p>Aucune déclaration de maladie.</p>';
        } else {
            html += '<table class="table"><thead><tr><th>Période</th><th>Description</th><th>PDF</th><th>Email envoyé</th><th>Créée le</th></tr></thead><tbody>';
            
            declarations.forEach(declaration => {
                const startDate = new Date(declaration.start_date).toLocaleDateString('fr-FR');
                const endDate = new Date(declaration.end_date).toLocaleDateString('fr-FR');
                const createdDate = new Date(declaration.created_at).toLocaleDateString('fr-FR');
                
                const pdfCell = declaration.pdf_filename ? `
                    ✅ <a href="${CONFIG.API_BASE_URL}/sickness-declarations/${declaration.id}/pdf" target="_blank" rel="noopener">${declaration.pdf_filename}</a>
                ` : '❌ Aucun fichier';
                
                html += `
                    <tr>
                        <td>${startDate === endDate ? startDate : `${startDate} - ${endDate}`}</td>
                        <td>${declaration.description || 'Non spécifiée'}</td>
                        <td>${pdfCell}</td>
                        <td><span class="status-badge ${declaration.email_sent ? 'status-approuve' : 'status-refuse'}">${declaration.email_sent ? 'Envoyé' : 'Non envoyé'}</span></td>
                        <td>${createdDate}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
        }
        
        return html;
        
    } catch (error) {
        return `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    }
}

// Prévisualisation PDF dans une popup (modal simple)
function previewPdf(declarationId) {
    const url = `${CONFIG.API_BASE_URL}/sickness-declarations/${declarationId}/pdf`;
    // Ouvre dans un nouvel onglet si le navigateur bloque les modales
    const w = window.open(url, '_blank');
    if (!w) {
        // fallback si popups bloquées
        window.location.href = url;
    }
}

// Fonction pour charger les déclarations de maladie pour les admins
async function loadAllSicknessDeclarations() {
    try {
        let declarations = await apiCall('/sickness-declarations/');
        if (!Array.isArray(declarations)) {
            if (declarations && (declarations.error || declarations.detail)) {
                const msg = declarations.error || declarations.detail;
                return `<div class="alert alert-error">${msg}</div>`;
            }
            declarations = [];
        }
        
        let html = '<h3>🏥 Déclarations de Maladie - Vue Administrateur</h3>';
        
        if (declarations.length === 0) {
            html += '<div class="alert alert-info">Aucune déclaration de maladie pour le moment.</div>';
        } else {
            // Statistiques rapides
            const totalDeclarations = declarations.length;
            const emailsSent = declarations.filter(d => d.email_sent).length;
            const withPdf = declarations.filter(d => d.pdf_filename).length;
            const unviewed = declarations.filter(d => !d.viewed_by_admin).length;
            
            html += `
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; text-align: center;">
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: #3498db;">${totalDeclarations}</div>
                            <div style="color: #666; font-size: 12px;">Total</div>
                        </div>
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: ${emailsSent > 0 ? '#27ae60' : '#e74c3c'};">${emailsSent}</div>
                            <div style="color: #666; font-size: 12px;">Emails envoyés</div>
                        </div>
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: ${withPdf > 0 ? '#27ae60' : '#e74c3c'};">${withPdf}</div>
                            <div style="color: #666; font-size: 12px;">Avec PDF</div>
                        </div>
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: ${unviewed > 0 ? '#f39c12' : '#27ae60'};">${unviewed}</div>
                            <div style="color: #666; font-size: 12px;">Non vues</div>
                        </div>
                    </div>
                </div>
            `;
            
            html += '<table class="table"><thead><tr><th>👤 Utilisateur</th><th>📅 Période</th><th>📝 Description</th><th>📄 Document PDF</th><th>📧 Email</th><th>👁️ Statut Admin</th><th>🕐 Créée le</th><th>⚡ Actions</th></tr></thead><tbody>';
            
            declarations.forEach(declaration => {
                const startDate = new Date(declaration.start_date).toLocaleDateString('fr-FR');
                const endDate = new Date(declaration.end_date).toLocaleDateString('fr-FR');
                const createdDate = new Date(declaration.created_at).toLocaleDateString('fr-FR');
                
                // Style de la ligne selon le statut
                let rowStyle = '';
                if (!declaration.viewed_by_admin) {
                    rowStyle = 'background-color: #fff3cd; border-left: 3px solid #ffc107;';
                }
                
                // Statut du PDF avec plus de détails
                let pdfStatus = '❌ <span style="color: #e74c3c;">Aucun document</span>';
                if (declaration.pdf_filename) {
                    const url = `${CONFIG.API_BASE_URL}/sickness-declarations/${declaration.id}/pdf`;
                    pdfStatus = `✅ <a href="${url}" target="_blank" rel="noopener">${declaration.pdf_filename}</a>`;
                }
                
                // Statut email avec plus de clarté
                const emailStatus = declaration.email_sent ? 
                    '✅ <span style="color: #27ae60; font-weight: bold;">Envoyé</span>' : 
                    '❌ <span style="color: #e74c3c; font-weight: bold;">Non envoyé</span>';
                
                // Actions possibles
                let actions = '';
                if (!declaration.viewed_by_admin) {
                    actions += `<button class="btn btn-sm btn-success" onclick="markSicknessAsViewed(${declaration.id})" title="Marquer comme vue">👁️ Marquer vue</button> `;
                }
                if (declaration.pdf_filename && !declaration.email_sent) {
                    actions += `<button class="btn btn-sm btn-warning" onclick="resendSicknessEmail(${declaration.id})" title="Renvoyer l'email">📧 Renvoyer</button>`;
                }
                if (!actions) {
                    actions = '<span style="color: #666;">—</span>';
                }
                
                html += `
                    <tr style="${rowStyle}">
                        <td><strong>${declaration.user.first_name} ${declaration.user.last_name}</strong><br><small style="color: #666;">${declaration.user.email}</small></td>
                        <td><strong>${startDate === endDate ? startDate : `${startDate} - ${endDate}`}</strong></td>
                        <td>${declaration.description ? `<em>"${declaration.description}"</em>` : '<span style="color: #999;">Non spécifiée</span>'}</td>
                        <td>${pdfStatus}</td>
                        <td>${emailStatus}</td>
                        <td><span class="status-badge ${declaration.viewed_by_admin ? 'status-approuve' : 'status-en_attente'}">${declaration.viewed_by_admin ? '✅ Vue' : '⏳ À voir'}</span></td>
                        <td><small>${createdDate}</small></td>
                        <td>${actions}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
        }
        
        return html;
        
    } catch (error) {
        return `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    }
}

// Fonction pour marquer une déclaration comme vue par l'admin
async function markSicknessAsViewed(declarationId) {
    try {
        await apiCall(`/sickness-declarations/${declarationId}/mark-viewed`, {
            method: 'POST'
        });
        
        showAlert('Déclaration marquée comme vue !', 'success');
        // Recharger la liste
        loadAdminSicknessDeclarations();
        
    } catch (error) {
        showAlert(`Erreur: ${error.message}`, 'error');
    }
}

// Fonction pour renvoyer l'email d'une déclaration
async function resendSicknessEmail(declarationId) {
    if (!confirm('Voulez-vous vraiment renvoyer l\'email de cette déclaration de maladie ?')) {
        return;
    }
    
    try {
        await apiCall(`/sickness-declarations/${declarationId}/resend-email`, {
            method: 'POST'
        });
        
        showAlert('Email renvoyé avec succès !', 'success');
        // Recharger la liste
        loadAdminSicknessDeclarations();
        
    } catch (error) {
        showAlert(`Erreur lors de l'envoi: ${error.message}`, 'error');
    }
}''',
            'mime_type': 'text/javascript'
        },
        '/static/js/utils.js': {
            'content': '''// Utilitaires d'affichage
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, CONFIG.ALERT_TIMEOUT);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString(CONFIG.DATE_FORMAT);
}

// Formatage robuste inter-navigateurs (notamment Safari) pour les dates ISO
function formatDateSafe(value) {
    if (!value) return '—';
    let candidate = value;
    if (typeof candidate === 'string') {
        // Remplacer l'espace par un T si nécessaire
        if (candidate.includes(' ') && !candidate.includes('T')) {
            candidate = candidate.replace(' ', 'T');
        }
        // Supprimer les microsecondes si présentes (Safari peut échouer)
        // Ex: 2025-08-11T12:34:56.123456 -> 2025-08-11T12:34:56
        candidate = candidate.replace(/(\.\d{3,})/, '');
    }
    let d = new Date(candidate);
    if (isNaN(d)) {
        // Fallback: garder uniquement la partie date
        const datePart = String(value).split('T')[0] || String(value).split(' ')[0];
        if (datePart) {
            const d2 = new Date(datePart);
            if (!isNaN(d2)) return d2.toLocaleDateString(CONFIG.DATE_FORMAT);
        }
        return '—';
    }
    return d.toLocaleDateString(CONFIG.DATE_FORMAT);
}

function formatDateForInput(dateString) {
    const date = new Date(dateString);
    return date.toISOString().slice(0, 10); // Format YYYY-MM-DD pour input type="date"
}

// Google Calendar supprimé

// Utilitaires de navigation
function showTab(tabName) {
    // Masquer tous les contenus
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Désactiver tous les onglets
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Activer l'onglet correspondant au tabName (sans dépendre de event)
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => {
        const onclickAttr = tab.getAttribute('onclick') || '';
        if (onclickAttr.includes(`showTab('${tabName}')`) || onclickAttr.includes(`showTab(\"${tabName}\")`)) {
            tab.classList.add('active');
        }
    });
    
    // Afficher le contenu correspondant
    const content = document.getElementById(tabName);
    if (content) {
        content.classList.add('active');
        
        // Charger les données selon l'onglet
        switch(tabName) {
            case 'dashboard':
                loadDashboard();
                break;
            case 'calendar':
                loadCalendar();
                break;
            case 'procedure':
                // Charger les 2 sous-onglets
                loadUserRequests();
                (async () => {
                    try {
                        const declHtml = await loadSicknessDeclarations();
                        const declDiv = document.getElementById('user-sickness-declarations-list');
                        if (declDiv) declDiv.innerHTML = declHtml;
                    } catch {}
                })();
                break;
            case 'admin-users':
                loadUsers();
                break;
            case 'admin-requests':
                // Charger les deux types de demandes
                loadAllRequests();
                loadAdminSicknessDeclarations();
                (async () => { try { await loadAdminDocuments(); } catch {} })();
                break;
        }
    }
}

// Fonction pour gérer les sous-onglets
function showSubTab(subTabName) {
    // Masquer tous les contenus de sous-onglets
    document.querySelectorAll('.sub-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Désactiver tous les sous-onglets
    document.querySelectorAll('.sub-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Activer le sous-onglet correspondant (sans dépendre de event)
    const subTabs = document.querySelectorAll('.sub-tab');
    subTabs.forEach(tab => {
        const onclickAttr = tab.getAttribute('onclick') || '';
        if (onclickAttr.includes(`showSubTab('${subTabName}')`) || onclickAttr.includes(`showSubTab(\"${subTabName}\")`)) {
            tab.classList.add('active');
        }
    });
    
    // Afficher le contenu correspondant
    const content = document.getElementById(subTabName);
    if (content) {
        content.classList.add('active');
        // Charger dynamiquement le contenu associé au sous-onglet sans recharger la page
        switch (subTabName) {
            case 'vacation-requests':
                if (typeof loadAllRequests === 'function') loadAllRequests();
                break;
            case 'sickness-declarations':
                if (typeof loadAdminSicknessDeclarations === 'function') loadAdminSicknessDeclarations();
                break;
            case 'admin-documents':
                if (typeof loadAdminDocuments === 'function') loadAdminDocuments();
                break;
            case 'user-vacation-requests':
                if (typeof loadUserRequests === 'function') loadUserRequests();
                break;
            case 'user-sickness-declarations':
                (async () => {
                    try {
                        if (typeof loadSicknessDeclarations === 'function') {
                            const html = await loadSicknessDeclarations();
                            const div = document.getElementById('user-sickness-declarations-list');
                            if (div) div.innerHTML = html;
                        }
                    } catch (e) {
                        const div = document.getElementById('user-sickness-declarations-list');
                        if (div) div.innerHTML = `<div class="alert alert-error">${e.message}</div>`;
                    }
                })();
                break;
        }
    }
}

// API Calls
async function apiCall(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    if (authToken) {
        config.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Erreur API');
        }
        
        return data;
    } catch (error) {
        console.error('Erreur API:', error);
        throw error;
    }
}

// Utilitaires de formulaire

function showNewUserForm() {
    document.getElementById('new-user-form').style.display = 'block';
}

function hideNewUserForm() {
    document.getElementById('new-user-form').style.display = 'none';
    document.getElementById('user-form').reset();
}

// Fonctions pour les demandes d'absence
function showNewRequestForm() {
    // Fermer le formulaire de déclaration de maladie s'il est ouvert
    hideSicknessDeclarationForm();
    
    document.getElementById('new-request-form').style.display = 'block';
    
    // Définir la date par défaut à demain
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];
    
    document.getElementById('start-date').value = tomorrowStr;
    document.getElementById('end-date').value = tomorrowStr;
}

function hideNewRequestForm() {
    document.getElementById('new-request-form').style.display = 'none';
    document.getElementById('absence-form').reset();
}

// Fonction pour charger les demandes de l'utilisateur
async function loadUserRequests() {
    const requestsListDiv = document.getElementById('user-vacation-requests-list');
    
    try {
        requestsListDiv.innerHTML = '<div class="loading">Chargement...</div>';
        const [requests, sickness] = await Promise.all([
            apiCall('/absence-requests/'),
            apiCall('/sickness-declarations/')
        ]);

        if (!Array.isArray(requests)) {
            const msg = (requests && (requests.error || requests.detail)) ? (requests.error || requests.detail) : 'Données indisponibles';
            requestsListDiv.innerHTML = `<div class="alert alert-error">${msg}</div>`;
            return;
        }

        if (requests.length === 0) {
            requestsListDiv.innerHTML = '<p>Aucune demande de vacances.</p>';
            return;
        }

        let html = '<h4>Vacances et Maladies</h4>';
        html += '<table class="table"><thead><tr><th>Type</th><th>Période</th><th>Statut</th><th>Détails</th><th>Créée le</th></tr></thead><tbody>';

        // Demandes d'absence (vacances/maladie déclarées via demandes)
        (Array.isArray(requests) ? requests : []).forEach(request => {
            const startDate = formatDateSafe(request.start_date);
            const endDate = formatDateSafe(request.end_date);
            const createdDate = formatDateSafe(request.created_at);
            const statusText = {
                'en_attente': 'En attente',
                'approuve': 'Approuvé',
                'refuse': 'Refusé'
            }[request.status] || request.status;
            const typeText = request.type === 'vacances' ? 'Vacances' : 'Maladie';
            html += `
                <tr>
                    <td><span class="status-badge event-${request.type}">${typeText}</span></td>
                    <td>${startDate === endDate ? startDate : `${startDate} - ${endDate}`}</td>
                    <td><span class="status-badge status-${request.status}">${statusText}</span></td>
                    <td>${request.reason || '—'}</td>
                    <td>${createdDate}</td>
                </tr>
            `;
        });

        // On affiche uniquement les demandes de vacances ici; les maladies sont dans l'autre sous-onglet

        html += '</tbody></table>';
        requestsListDiv.innerHTML = html;

    } catch (error) {
        requestsListDiv.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    }
}

// Alias pour compatibilité
function loadRequests() {
    loadUserRequests();
}

// Chargement du calendrier
async function loadCalendar() {
    try {
        await showCalendarSection();
    } catch (error) {
        console.error('Erreur lors du chargement du calendrier:', error);
        showAlert('Erreur lors du chargement du calendrier', 'error');
    }
}''',
            'mime_type': 'text/javascript'
        },
        '/static/js/main.js': {
            'content': '''// Event Listeners et initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Restauration de session si disponible
    (async () => {
        const hasToken = !!window.authToken;
        const hasUser = !!window.currentUser;
        if (hasToken) {
            authToken = window.authToken;
        }
        if (hasUser) {
            currentUser = window.currentUser;
        } else if (hasToken) {
            // Tenter de récupérer l'utilisateur courant si seulement le token est présent
            try {
                currentUser = await apiCall('/users/me');
                try { localStorage.setItem('currentUser', JSON.stringify(currentUser)); } catch {}
                window.currentUser = currentUser;
            } catch (e) {
                // Token invalide/expiré
                try { localStorage.removeItem('authToken'); localStorage.removeItem('currentUser'); } catch {}
                authToken = null;
            }
        }
        if (authToken && currentUser) {
            showMainContent();
        } else {
            document.getElementById('auth-section').style.display = 'block';
            document.getElementById('main-content').style.display = 'none';
        }
    })();
    // Formulaire de connexion
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        login(email, password);
    });
    

    
    // Formulaire de demande d'absence
    const absenceForm = document.getElementById('absence-form');
    if (absenceForm) {
        absenceForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                type: document.getElementById('absence-type').value,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value,
                reason: document.getElementById('reason').value || null
            };
            
            if (!formData.start_date || !formData.end_date) {
                showAlert('Veuillez sélectionner les dates de début et de fin', 'error');
                return;
            }
            
            if (new Date(formData.start_date) > new Date(formData.end_date)) {
                showAlert('La date de fin doit être postérieure à la date de début', 'error');
                return;
            }
            
            try {
                await apiCall('/absence-requests/', {
                    method: 'POST',
                    body: JSON.stringify(formData)
                });
                
                showAlert('Demande d\'absence soumise avec succès !', 'success');
                hideNewRequestForm();
                loadUserRequests(); // Recharger la liste des demandes
                
            } catch (error) {
                showAlert('Erreur lors de la soumission: ' + error.message, 'error');
            }
        });
    }
    
    // Formulaire d'utilisateur
    document.getElementById('user-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            email: document.getElementById('user-email').value,
            first_name: document.getElementById('user-first-name').value,
            last_name: document.getElementById('user-last-name').value,
            role: document.getElementById('user-role').value,
            password: document.getElementById('user-password').value
        };
        
        const editId = this.getAttribute('data-edit-id');
        
        try {
            if (editId) {
                // Mode édition - ne pas envoyer le mot de passe s'il est vide
                if (!formData.password) {
                    delete formData.password;
                }
                await apiCall(`/users/${editId}`, {
                    method: 'PUT',
                    body: JSON.stringify(formData)
                });
                showAlert('Utilisateur modifié avec succès !');
                this.removeAttribute('data-edit-id');
            } else {
                // Mode création
                await apiCall('/users/', {
                    method: 'POST',
                    body: JSON.stringify(formData)
                });
                showAlert('Utilisateur créé avec succès !');
            }
            
            hideNewUserForm();
            loadUsers();
            
        } catch (error) {
            showAlert(error.message, 'error');
        }
    });
});

// Exposer les fonctions globalement pour les boutons onclick
window.showTab = showTab;
window.logout = logout;
window.showNewUserForm = showNewUserForm;
window.hideNewUserForm = hideNewUserForm;
window.editUser = editUser;
window.deleteUser = deleteUser;
window.approveRequest = approveRequest;
window.rejectRequest = rejectRequest;
window.closeEventModal = closeEventModal;
window.showAdminAbsenceForm = showAdminAbsenceForm;
window.hideAdminAbsenceForm = hideAdminAbsenceForm;
window.showUserAbsenceSummary = showUserAbsenceSummary;
window.closeUserAbsenceModal = closeUserAbsenceModal;
window.showSicknessDeclarationForm = showSicknessDeclarationForm;
window.hideSicknessDeclarationForm = hideSicknessDeclarationForm;
window.loadAdminSicknessDeclarations = loadAdminSicknessDeclarations;
window.markSicknessAsViewed = markSicknessAsViewed;
window.resendSicknessEmail = resendSicknessEmail;
window.showNewRequestForm = showNewRequestForm;
window.hideNewRequestForm = hideNewRequestForm;
window.loadUserRequests = loadUserRequests;
window.loadRequests = loadRequests;
window.showSubTab = showSubTab;

async function apiCall(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(options.headers || {})
        },
        ...options
    };

    if (authToken) {
        config.headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(url, config);
    const raw = await response.text();
    let data = {};
    try {
        data = raw ? JSON.parse(raw) : {};
    } catch (_) {
        if (!response.ok) {
            throw new Error(raw?.slice(0, 300) || 'Erreur API');
        }
        return {};
    }
    // Gestion centralisée des erreurs renvoyées en JSON (même si HTTP 200)
    const lowerError = (data && typeof data === 'object' && (data.error || data.detail))
        ? String(data.error || data.detail).toLowerCase()
        : '';
    if (lowerError.includes('forbidden') || lowerError.includes('unauthorized')) {
        // Session expirée / token invalide → forcer une reconnexion propre
        try { localStorage.removeItem('authToken'); localStorage.removeItem('currentUser'); } catch {}
        authToken = null; currentUser = null;
        // Afficher l'écran d'auth et masquer le contenu
        const auth = document.getElementById('auth-section');
        const main = document.getElementById('main-content');
        if (auth && main) { auth.style.display = 'block'; main.style.display = 'none'; }
        throw new Error('Session expirée, veuillez vous reconnecter.');
    }
    if (!response.ok) {
        const msg = data?.detail || data?.error || raw || 'Erreur API';
        throw new Error(typeof msg === 'string' ? msg : 'Erreur API');
    }
    return data;
}''',
            'mime_type': 'text/javascript'
        },
    }
    
    return static_files.get(file_path, None)
