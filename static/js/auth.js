// Authentification
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
}