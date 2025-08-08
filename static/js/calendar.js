// Gestion du calendrier (vue mensuelle admin, vue annuelle utilisateur)

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
            const response = await fetch(`${CONFIG.API_BASE_URL}/calendar/admin?year=${this.currentYear}&month=${this.currentMonth + 1}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            if (!response.ok) {
                throw new Error('Erreur lors du chargement du calendrier');
            }

            const data = await response.json();
            this.events = Array.isArray(data) ? data : [];
            this.renderMonthlyCalendar();
        } catch (error) {
            console.error('Erreur:', error);
            showAlert('Erreur lors du chargement du calendrier', 'error');
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
            const [eventsResponse, summaryResponse] = await Promise.all([
                fetch(`${CONFIG.API_BASE_URL}/calendar/user?year=${this.currentYear}`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                }),
                fetch(`${CONFIG.API_BASE_URL}/calendar/summary?year=${this.currentYear}`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                })
            ]);

            if (!eventsResponse.ok || !summaryResponse.ok) {
                throw new Error('Erreur lors du chargement du calendrier');
            }

            const data = await eventsResponse.json();
            this.events = Array.isArray(data) ? data : [];
            const summary = await summaryResponse.json();
            
            // Afficher le résumé
            const summaryText = `${summary.used_leave_days}/${summary.total_leave_days} jours utilisés - ${summary.remaining_leave_days} jours restants`;
            document.getElementById('summary-text').textContent = summaryText;

            this.renderYearlyCalendar();
        } catch (error) {
            console.error('Erreur:', error);
            showAlert('Erreur lors du chargement du calendrier', 'error');
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
        if (actionsRow && editBtn && deleteBtn) {
            if (isAdmin && event.event_source === 'absence_request') {
                actionsRow.style.display = 'flex';
                editBtn.onclick = () => this.openEditDialog(event);
                deleteBtn.onclick = () => this.confirmDelete(event);
            } else {
                actionsRow.style.display = 'none';
                editBtn.onclick = null;
                deleteBtn.onclick = null;
            }
        }
    }

    

    showMultipleEventsModal(events, date) {
        // Pour simplifier, on affiche juste le premier événement
        // Dans une vraie app, on pourrait créer une modal spéciale pour plusieurs événements
        this.showEventModal(events[0]);
    }

    async confirmDelete(event) {
        if (!confirm('Supprimer cette absence ?')) return;
        try {
            await apiCall(`/absence-requests/admin/${event.id}`, { method: 'DELETE' });
            showAlert('Absence supprimée');
            closeEventModal();
            await this.showCalendar();
            loadAllRequests && loadAllRequests();
        } catch (e) {
            showAlert(e.message || 'Erreur suppression', 'error');
        }
    }

    openEditDialog(event) {
        const newStart = prompt('Nouvelle date de début (YYYY-MM-DD):', event.start);
        if (!newStart) return;
        const newEnd = prompt('Nouvelle date de fin (YYYY-MM-DD):', event.end);
        if (!newEnd) return;
        const newReason = prompt('Raison (optionnel):', event.reason || '');
        const statusMap = { 'en_attente': 'en_attente', 'approuve': 'approuve', 'refuse': 'refuse' };
        const newStatus = prompt('Statut (en_attente/approuve/refuse):', event.status);
        const normalizedStatus = statusMap[newStatus] ? newStatus : undefined;
        this.updateAbsence(event.id, {
            start_date: newStart,
            end_date: newEnd,
            reason: newReason || null,
            status: normalizedStatus
        });
    }

    async updateAbsence(id, payload) {
        try {
            await apiCall(`/absence-requests/admin/${id}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            showAlert('Absence mise à jour');
            closeEventModal();
            await this.showCalendar();
            loadAllRequests && loadAllRequests();
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
}