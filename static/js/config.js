// Configuration centralisée de l'application
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
window.API_BASE_URL = CONFIG.API_BASE_URL; 