/**
 * Interface d'administration pour Google Calendar
 */

class GoogleCalendarAdmin {
    constructor() {
        this.init();
    }

    async init() {
        await this.checkStatus();
        this.bindEvents();
    }

    async checkStatus() {
        try {
            const response = await fetch('/google-calendar/status', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateStatusDisplay(data);
            } else {
                this.showError('Erreur lors de la vérification du statut');
            }
        } catch (error) {
            this.showError('Erreur de connexion');
        }
    }

    updateStatusDisplay(data) {
        const statusElement = document.getElementById('calendar-status');
        const actionsElement = document.getElementById('calendar-actions');

        if (data.enabled) {
            statusElement.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i>
                    <strong>Google Calendar activé</strong><br>
                    Calendrier: ${data.calendar_id}<br>
                    ${data.message}
                </div>
            `;
            actionsElement.style.display = 'block';
        } else {
            statusElement.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Google Calendar non configuré</strong><br>
                    ${data.message}<br>
                    <small>Consultez GOOGLE_CALENDAR_SETUP.md pour la configuration</small>
                </div>
            `;
            actionsElement.style.display = 'none';
        }
    }

    bindEvents() {
        // Bouton de test
        const testBtn = document.getElementById('test-calendar-btn');
        if (testBtn) {
            testBtn.addEventListener('click', () => this.testCalendar());
        }

        // Bouton de synchronisation
        const syncBtn = document.getElementById('sync-requests-btn');
        if (syncBtn) {
            syncBtn.addEventListener('click', () => this.syncApprovedRequests());
        }

        // Bouton de nettoyage
        const cleanBtn = document.getElementById('clean-events-btn');
        if (cleanBtn) {
            cleanBtn.addEventListener('click', () => this.cleanOrphanedEvents());
        }

        // Bouton d'actualisation
        const refreshBtn = document.getElementById('refresh-status-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.checkStatus());
        }
    }

    async testCalendar() {
        const button = document.getElementById('test-calendar-btn');
        const originalText = button.textContent;
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Test en cours...';

        try {
            const response = await fetch('/google-calendar/test-event', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess(`Test réussi ! Événement créé : ${data.event_id}`);
            } else {
                this.showError(`Erreur lors du test : ${data.detail}`);
            }
        } catch (error) {
            this.showError('Erreur de connexion lors du test');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    async syncApprovedRequests() {
        const button = document.getElementById('sync-requests-btn');
        const originalText = button.textContent;
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Synchronisation...';

        try {
            const response = await fetch('/google-calendar/sync-approved-requests', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                let message = `${data.synced_count}/${data.total_requests} demandes synchronisées`;
                if (data.errors.length > 0) {
                    message += `\nErreurs : ${data.errors.join(', ')}`;
                }
                this.showSuccess(message);
            } else {
                this.showError(`Erreur lors de la synchronisation : ${data.detail}`);
            }
        } catch (error) {
            this.showError('Erreur de connexion lors de la synchronisation');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    async cleanOrphanedEvents() {
        if (!confirm('Êtes-vous sûr de vouloir supprimer les événements orphelins ? Cette action est irréversible.')) {
            return;
        }

        const button = document.getElementById('clean-events-btn');
        const originalText = button.textContent;
        
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Nettoyage...';

        try {
            const response = await fetch('/google-calendar/orphaned-events', {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                let message = `${data.deleted_count} événements orphelins supprimés`;
                if (data.errors.length > 0) {
                    message += `\nErreurs : ${data.errors.join(', ')}`;
                }
                this.showSuccess(message);
            } else {
                this.showError(`Erreur lors du nettoyage : ${data.detail}`);
            }
        } catch (error) {
            this.showError('Erreur de connexion lors du nettoyage');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    showMessage(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        
        const messageElement = document.getElementById('calendar-messages');
        messageElement.innerHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <i class="fas ${icon}"></i>
                ${message.replace(/\n/g, '<br>')}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                const alert = messageElement.querySelector('.alert');
                if (alert) {
                    alert.remove();
                }
            }, 5000);
        }
    }
}

// Initialiser l'interface d'administration Google Calendar
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('google-calendar-admin')) {
        new GoogleCalendarAdmin();
    }
});