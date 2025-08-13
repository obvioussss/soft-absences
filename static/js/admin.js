// Fonctions administrateur
async function loadUsers() {
    const usersList = document.getElementById('users-list');
    
    try {
    const users = await apiCall('/users');
        
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
        let requests = await apiCall('/absence-requests/all');

        // Si l'API renvoie un objet d'erreur → afficher l'erreur, sinon fallback sur tableau vide
        if (!Array.isArray(requests)) {
            if (requests && (requests.error || requests.detail)) {
                const msg = requests.error || requests.detail;
                requestsList.innerHTML = `<div class="alert alert-error">${msg}</div>`;
                return;
            }
            requests = [];
        }

        if (requests.length === 0) {
            requestsList.innerHTML = '<div class="alert alert-info">Aucune demande de vacances pour le moment.</div>';
            return;
        }
        
        let html = '<h3>🏖️ Demandes de Vacances</h3>';
        
        // Statistiques rapides (sécurisées)
        const arr = Array.isArray(requests) ? requests : [];
        const totalRequests = arr.length;
        const pendingRequests = arr.filter(r => r.status === 'en_attente').length;
        const approvedRequests = arr.filter(r => r.status === 'approuve').length;
        const rejectedRequests = arr.filter(r => r.status === 'refuse').length;
        
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
        
        arr.forEach(request => {
            const startDate = formatDateSafe(request.start_date);
            const endDate = formatDateSafe(request.end_date);
            const createdDate = formatDateSafe(request.created_at);
            
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
            
            const userDisplay = request.user ? `<strong>${request.user.first_name} ${request.user.last_name}</strong><br><small style="color: #666;">${request.user.email}</small>` : '<span style="color:#e74c3c">Utilisateur inconnu</span>';
            html += `
                <tr style="${rowStyle}">
                    <td>${userDisplay}</td>
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
    const users = await apiCall('/users');
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
        // Gérer l'option PDF si type maladie
        const typeSelect = document.getElementById('admin-absence-type');
        const pdfGroup = document.getElementById('admin-absence-pdf-group');
        const dropzone = document.getElementById('admin-absence-dropzone');
        const fileInput = document.getElementById('admin-absence-pdf');
        const fileName = document.getElementById('admin-absence-pdf-name');
        const syncVisibility = () => { if (pdfGroup) pdfGroup.style.display = typeSelect.value === 'maladie' ? 'block' : 'none'; };
        if (typeSelect) typeSelect.onchange = syncVisibility;
        syncVisibility();
        if (dropzone && fileInput) {
            dropzone.onclick = () => fileInput.click();
            dropzone.ondragover = (e) => { e.preventDefault(); dropzone.style.background = '#fff8e1'; };
            dropzone.ondragleave = () => { dropzone.style.background = '#fff8e1'; };
            dropzone.ondrop = (e) => {
                e.preventDefault();
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    fileInput.files = e.dataTransfer.files;
                    if (fileName) fileName.textContent = e.dataTransfer.files[0].name;
                }
            };
            fileInput.onchange = () => { if (fileName && fileInput.files && fileInput.files[0]) fileName.textContent = fileInput.files[0].name; };
        }
        
    } catch (error) {
        showAlert('Erreur lors du chargement des utilisateurs: ' + error.message, 'error');
    }
}

function hideAdminAbsenceForm() {
    const modal = document.getElementById('admin-absence-modal');
    modal.style.display = 'none';
    document.getElementById('admin-absence-form-element').reset();
}

// Admin Sickness modal controls
function showAdminSicknessForm() {
    const modal = document.getElementById('admin-sickness-modal');
    modal.style.display = 'flex';
    (async () => {
        try {
    const users = await apiCall('/users');
            const userSelect = document.getElementById('admin-sickness-user');
            userSelect.innerHTML = '<option value="">Sélectionner un utilisateur...</option>';
            users.forEach(user => {
                if (user.role !== 'admin') {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = `${user.first_name} ${user.last_name} (${user.email})`;
                    userSelect.appendChild(option);
                }
            });
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('admin-sickness-start').value = today;
            document.getElementById('admin-sickness-end').value = today;
        } catch (e) { showAlert('Erreur chargement utilisateurs: ' + e.message, 'error'); }
    })();

    // Dropzone click/drag
    const dropzone = document.getElementById('admin-sickness-dropzone');
    const fileInput = document.getElementById('admin-sickness-pdf');
    dropzone.onclick = () => fileInput.click();
    dropzone.ondragover = (e) => { e.preventDefault(); dropzone.style.background = '#fffbeb'; };
    dropzone.ondragleave = () => { dropzone.style.background = '#fff8e1'; };
    dropzone.ondrop = (e) => {
        e.preventDefault();
        dropzone.style.background = '#fff8e1';
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            fileInput.files = e.dataTransfer.files;
        }
    };
}

function hideAdminSicknessForm() {
    const modal = document.getElementById('admin-sickness-modal');
    modal.style.display = 'none';
    const form = document.getElementById('admin-sickness-form');
    if (form) form.reset();
}

// Submission handler for admin sickness
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-sickness-form');
    if (!form) return;
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const userId = parseInt(document.getElementById('admin-sickness-user').value);
        const start = document.getElementById('admin-sickness-start').value;
        const end = document.getElementById('admin-sickness-end').value;
        const desc = document.getElementById('admin-sickness-description').value;
        const pdf = document.getElementById('admin-sickness-pdf').files[0];
        if (!userId) return showAlert('Sélectionnez un utilisateur', 'error');
        if (!start || !end) return showAlert('Dates requises', 'error');
        if (new Date(start) > new Date(end)) return showAlert('La date de fin doit être postérieure', 'error');
        if (!pdf) return showAlert('Sélectionnez un PDF', 'error');
        if (pdf.type !== 'application/pdf') return showAlert('PDF uniquement', 'error');
        if (pdf.size > 10 * 1024 * 1024) return showAlert('PDF > 10MB', 'error');

        const fd = new FormData();
        fd.append('user_id', String(userId));
        fd.append('start_date', start);
        fd.append('end_date', end);
        if (desc) fd.append('description', desc);
        fd.append('pdf_file', pdf);

        try {
            await fetch(`${CONFIG.API_BASE_URL}/sickness-declarations/admin`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${authToken}` },
                body: fd
            }).then(async r => { if (!r.ok) throw new Error((await r.json()).detail || 'Erreur'); });
            showAlert("Arrêt maladie créé et email envoyé.", 'success');
            hideAdminSicknessForm();
            if (calendar && currentUser.role === 'admin') await calendar.showCalendar();
        } catch (err) {
            showAlert(err.message, 'error');
        }
    });
});

// Expose
window.showAdminSicknessForm = showAdminSicknessForm;
window.hideAdminSicknessForm = hideAdminSicknessForm;
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
            
            const reasonEl = document.getElementById('admin-reason');
            const formData = {
                user_id: parseInt(document.getElementById('admin-absence-user').value),
                type: document.getElementById('admin-absence-type').value,
                start_date: document.getElementById('admin-start-date').value,
                end_date: document.getElementById('admin-end-date').value,
                reason: reasonEl ? (reasonEl.value || null) : null,
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
                const typeVal = document.getElementById('admin-absence-type').value;
                if (typeVal === 'maladie') {
                    const pdf = document.getElementById('admin-absence-pdf')?.files?.[0];
                    if (!pdf) { showAlert('Veuillez joindre un PDF pour un arrêt maladie', 'error'); return; }
                    if (pdf.type !== 'application/pdf') { showAlert('PDF uniquement', 'error'); return; }
                    if (pdf.size > 10 * 1024 * 1024) { showAlert('PDF > 10MB', 'error'); return; }
                    const fd = new FormData();
                    fd.append('user_id', String(formData.user_id));
                    fd.append('start_date', formData.start_date);
                    fd.append('end_date', formData.end_date);
                    if (formData.reason) fd.append('description', formData.reason);
                    fd.append('pdf_file', pdf);
                    await fetch(`${CONFIG.API_BASE_URL}/sickness-declarations/admin`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${authToken}` },
                        body: fd
                    }).then(async r => {
                        if (!r.ok) {
                            let msg = 'Erreur';
                            try {
                                const raw = await r.text();
                                try {
                                    const j = raw ? JSON.parse(raw) : {};
                                    msg = j.error || j.detail || raw || msg;
                                } catch (_) {
                                    msg = raw || msg;
                                }
                            } catch (_) {}
                            throw new Error(msg);
                        }
                    });
                    showAlert('Arrêt maladie créé et email envoyé.', 'success');
                } else {
                    await apiCall('/absence-requests/admin', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });
                    showAlert('Absence créée avec succès', 'success');
                }
                hideAdminAbsenceForm();
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
        if (!summary || summary.error || !summary.user) {
            const message = (summary && (summary.error || summary.detail)) ? (summary.error || summary.detail) : 'Résumé introuvable';
            summaryDiv.innerHTML = `<div class="alert alert-error">Erreur: ${message}</div>`;
            return;
        }
        
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
        
        if (Array.isArray(summary.recent_absences) && summary.recent_absences.length > 0) {
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

// Documents (liste consolidée des PDFs de maladie)
async function loadAdminDocuments() {
    const container = document.getElementById('admin-documents-list');
    if (!container) return;
    try {
        container.innerHTML = '<div class="loading">Chargement...</div>';
const declarations = await apiCall('/sickness-declarations');
        const withPdf = declarations.filter(d => d.pdf_filename);
        if (withPdf.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Aucun document disponible.</div>';
            return;
        }
        let html = '<h3>📄 Documents déposés</h3>';
        html += '<table class="table"><thead><tr><th>Nom du fichier</th><th>Utilisateur</th><th>Période</th><th>Créé le</th><th>Action</th></tr></thead><tbody>';
        withPdf.forEach(d => {
            const startDate = formatDateSafe(d.start_date);
            const endDate = formatDateSafe(d.end_date);
            const createdDate = formatDateSafe(d.created_at);
            const url = `${CONFIG.API_BASE_URL}/sickness-declarations/${d.id}/pdf`;
            html += `<tr>
                <td>${d.pdf_filename}</td>
                <td>${d.user ? `${d.user.first_name} ${d.user.last_name} (${d.user.email})` : '—'}</td>
                <td>${startDate === endDate ? startDate : `${startDate} - ${endDate}`}</td>
                <td>${createdDate}</td>
                <td><a class="btn" href="${url}" target="_blank" rel="noopener">Ouvrir</a></td>
            </tr>`;
        });
        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = `<div class="alert alert-error">Erreur: ${e.message}</div>`;
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
        if (calendar && currentUser.role === 'admin') await calendar.showCalendar();
        
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
        if (calendar && currentUser.role === 'admin') await calendar.showCalendar();
        
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