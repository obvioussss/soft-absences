// Authentification
async function login(email, password) {
    try {
        // 1) Essai principal: endpoint JSON dédié
        const jsonResp = await fetch(`${CONFIG.API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        let jsonData = null;
        try { jsonData = await jsonResp.json(); } catch (_) { jsonData = null; }
        if (jsonResp.ok && jsonData && jsonData.access_token) {
            authToken = jsonData.access_token;
            // Stocker token + user si fourni
            try { localStorage.setItem('authToken', authToken); } catch (_) {}
            currentUser = jsonData.user || await apiCall('/users/me');
            try { localStorage.setItem('currentUser', JSON.stringify(currentUser)); } catch (_) {}
            showMainContent();
            showAlert('Connexion réussie !');
            return;
        }

        // 2) Fallback: flux OAuth2 standard /token (x-www-form-urlencoded)
        const body = new URLSearchParams();
        body.append('username', email);
        body.append('password', password);
        const tokenResp = await fetch(`${CONFIG.API_BASE_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body
        });
        let tokenData = null;
        try { tokenData = await tokenResp.json(); } catch (_) { tokenData = null; }
        if (!tokenResp.ok || !tokenData || !tokenData.access_token) {
            const apiMessage = (jsonData && (jsonData.error || jsonData.message || jsonData.detail))
                || (tokenData && (tokenData.error || tokenData.message || tokenData.detail));
            throw new Error(apiMessage || 'Email ou mot de passe incorrect');
        }
        authToken = tokenData.access_token;
        try { localStorage.setItem('authToken', authToken); } catch (_) {}
        currentUser = await apiCall('/users/me');
        try { localStorage.setItem('currentUser', JSON.stringify(currentUser)); } catch (_) {}
        showMainContent();
        showAlert('Connexion réussie !');
    } catch (error) {
        showAlert(error.message || 'Erreur de connexion', 'error');
    }
}

function logout() {
    // Arrêter la mise à jour périodique du badge
    if (typeof stopBadgeUpdateInterval === 'function') {
        stopBadgeUpdateInterval();
    }
    
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
    
    // Mettre à jour le badge de notification pour les admins
    if (currentUser.role === 'admin' && typeof updatePendingRequestsBadge === 'function') {
        updatePendingRequestsBadge();
        // Démarrer la mise à jour périodique du badge
        if (typeof startBadgeUpdateInterval === 'function') {
            startBadgeUpdateInterval();
        }
    }
    
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