// Fonctions administrateur
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
        const requests = await apiCall('/absence-requests/all');
        
        if (requests.length === 0) {
            requestsList.innerHTML = '<div class="alert alert-info">Aucune demande de vacances en attente.</div>';
            return;
        }
        
        let html = '<h3>🏖️ Demandes de Vacances</h3>';
        
        // Statistiques rapides
        const totalRequests = requests.length;
        const pendingRequests = requests.filter(r => r.status === 'en_attente').length;
        const approvedRequests = requests.filter(r => r.status === 'approuve').length;
        const rejectedRequests = requests.filter(r => r.status === 'refuse').length;
        
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
        
        requests.forEach(request => {
            const startDate = new Date(request.start_date).toLocaleDateString('fr-FR');
            const endDate = new Date(request.end_date).toLocaleDateString('fr-FR');
            const createdDate = new Date(request.created_at).toLocaleDateString('fr-FR');
            
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
            
            html += `
                <tr style="${rowStyle}">
                    <td><strong>${request.user.first_name} ${request.user.last_name}</strong><br><small style="color: #666;">${request.user.email}</small></td>
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
        
    } catch (error) {
        showAlert('Erreur lors du chargement des utilisateurs: ' + error.message, 'error');
    }
}

function hideAdminAbsenceForm() {
    const modal = document.getElementById('admin-absence-modal');
    modal.style.display = 'none';
    document.getElementById('admin-absence-form-element').reset();
}

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
            
            const formData = {
                user_id: parseInt(document.getElementById('admin-absence-user').value),
                type: document.getElementById('admin-absence-type').value,
                start_date: document.getElementById('admin-start-date').value,
                end_date: document.getElementById('admin-end-date').value,
                reason: document.getElementById('admin-reason').value || null,
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
                await apiCall('/absence-requests/admin', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                showAlert('Absence créée avec succès', 'success');
                hideAdminAbsenceForm();
                
                // Recharger le calendrier si on est sur la vue calendrier
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
        
        if (summary.recent_absences && summary.recent_absences.length > 0) {
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
}