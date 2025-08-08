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

        if (requests.length === 0) {
            requestsListDiv.innerHTML = '<p>Aucune demande de vacances.</p>';
            return;
        }

        let html = '<h4>Vacances et Maladies</h4>';
        html += '<table class="table"><thead><tr><th>Type</th><th>Période</th><th>Statut</th><th>Détails</th><th>Créée le</th></tr></thead><tbody>';

        // Demandes d'absence (vacances/maladie déclarées via demandes)
        requests.forEach(request => {
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
}