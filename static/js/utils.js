// Utilitaires d'affichage
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

function formatDateForInput(dateString) {
    const date = new Date(dateString);
    return date.toISOString().slice(0, 10); // Format YYYY-MM-DD pour input type="date"
}

// Fonction pour ouvrir l'administration Google Calendar
function openGoogleCalendarAdmin() {
    // Ouvrir dans un nouvel onglet
    window.open('/static/templates/google-calendar-admin.html', '_blank');
}

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
                loadUserRequests();
                break;
            case 'admin-users':
                loadUsers();
                break;
            case 'admin-requests':
                // Charger les deux types de demandes
                loadAllRequests();
                loadAdminSicknessDeclarations();
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
    const requestsListDiv = document.getElementById('user-requests-list');
    
    try {
        requestsListDiv.innerHTML = '<div class="loading">Chargement...</div>';
        const requests = await apiCall('/absence-requests/');
        
        if (requests.length === 0) {
            requestsListDiv.innerHTML = '<p>Aucune demande d\'absence.</p>';
            return;
        }
        
        let html = '<table class="table"><thead><tr><th>Type</th><th>Période</th><th>Statut</th><th>Raison</th><th>Créée le</th></tr></thead><tbody>';
        
        requests.forEach(request => {
            const startDate = new Date(request.start_date).toLocaleDateString('fr-FR');
            const endDate = new Date(request.end_date).toLocaleDateString('fr-FR');
            const createdDate = new Date(request.created_at).toLocaleDateString('fr-FR');
            
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
                    <td>${request.reason || 'Non spécifiée'}</td>
                    <td>${createdDate}</td>
                </tr>
            `;
        });
        
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
}