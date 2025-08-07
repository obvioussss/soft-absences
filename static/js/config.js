// Configuration centralisée de l'application
const CONFIG = {
    API_BASE_URL: window.location.origin, // Utilise l'URL actuelle pour Vercel
    ALERT_TIMEOUT: 5000,
    DATE_FORMAT: 'fr-FR',
    DATE_INPUT_FORMAT: 'YYYY-MM-DD'
};

// Variables globales
let currentUser = null;
let authToken = null;

// Export pour utilisation dans d'autres fichiers
window.CONFIG = CONFIG;
window.currentUser = currentUser;
window.authToken = authToken;

// Variables globales pour compatibilité
window.API_BASE_URL = CONFIG.API_BASE_URL; 