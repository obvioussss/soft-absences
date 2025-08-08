// Event Listeners et initialisation
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
    if (!response.ok) {
        const msg = data?.detail || data?.error || raw || 'Erreur API';
        throw new Error(typeof msg === 'string' ? msg : 'Erreur API');
    }
    return data;
}