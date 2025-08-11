// Fonctions pour les déclarations de maladie

function showSicknessDeclarationForm() {
    // Fermer le formulaire de demande de congé s'il est ouvert
    hideNewRequestForm();
    
    document.getElementById('sickness-declaration-form').style.display = 'block';
    
    // Définir la date par défaut à aujourd'hui
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('sickness-start-date').value = today;
    document.getElementById('sickness-end-date').value = today;
}

function hideSicknessDeclarationForm() {
    document.getElementById('sickness-declaration-form').style.display = 'none';
    document.getElementById('sickness-form').reset();
}

// Gestionnaire de soumission du formulaire de déclaration de maladie
document.addEventListener('DOMContentLoaded', function() {
    const sicknessForm = document.getElementById('sickness-form');
    if (sicknessForm) {
        sicknessForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const startDate = document.getElementById('sickness-start-date').value;
            const endDate = document.getElementById('sickness-end-date').value;
            const description = document.getElementById('sickness-description').value;
            const pdfFile = document.getElementById('sickness-pdf').files[0];
            
            // Validations
            if (!startDate || !endDate) {
                showAlert('Veuillez sélectionner les dates de début et de fin', 'error');
                return;
            }
            
            if (new Date(startDate) > new Date(endDate)) {
                showAlert('La date de fin doit être postérieure à la date de début', 'error');
                return;
            }
            
            if (!pdfFile) {
                showAlert('Veuillez sélectionner un fichier PDF', 'error');
                return;
            }
            
            if (pdfFile.type !== 'application/pdf') {
                showAlert('Seuls les fichiers PDF sont acceptés', 'error');
                return;
            }
            
            if (pdfFile.size > 10 * 1024 * 1024) { // 10MB
                showAlert('Le fichier est trop volumineux (maximum 10MB)', 'error');
                return;
            }
            
            // Préparer les données du formulaire
            const formData = new FormData();
            formData.append('start_date', startDate);
            formData.append('end_date', endDate);
            formData.append('description', description);
            formData.append('pdf_file', pdfFile);
            
            try {
                // Désactiver le bouton de soumission
                const submitBtn = e.target.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                submitBtn.disabled = true;
                submitBtn.textContent = '📧 Envoi en cours...';
                
                const response = await fetch(`${CONFIG.API_BASE_URL}/sickness-declarations/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Erreur lors de l\'envoi de la déclaration');
                }
                
                 const result = await response.json();
                
                showAlert('Déclaration de maladie envoyée avec succès ! Email envoyé aux administrateurs.', 'success');
                hideSicknessDeclarationForm();
                
                // Recharger la liste des demandes si on est sur l'onglet procédure
                if (document.getElementById('procedure').classList.contains('active')) {
                    loadRequests();
                }
                
            } catch (error) {
                showAlert('Erreur lors de l\'envoi de la déclaration: ' + error.message, 'error');
            } finally {
                // Réactiver le bouton
                const submitBtn = e.target.querySelector('button[type="submit"]');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
});

// Fonction pour charger les déclarations de maladie de l'utilisateur
async function loadSicknessDeclarations() {
    try {
        const declarations = await apiCall('/sickness-declarations/');
        
        let html = '<h3>Mes déclarations de maladie</h3>';
        
        if (declarations.length === 0) {
            html += '<p>Aucune déclaration de maladie.</p>';
        } else {
            html += '<table class="table"><thead><tr><th>Période</th><th>Description</th><th>PDF</th><th>Email envoyé</th><th>Créée le</th></tr></thead><tbody>';
            
            declarations.forEach(declaration => {
                const startDate = new Date(declaration.start_date).toLocaleDateString('fr-FR');
                const endDate = new Date(declaration.end_date).toLocaleDateString('fr-FR');
                const createdDate = new Date(declaration.created_at).toLocaleDateString('fr-FR');
                
                const pdfCell = declaration.pdf_filename ? `
                    ✅ <a href="${CONFIG.API_BASE_URL}/sickness-declarations/${declaration.id}/pdf" target="_blank" rel="noopener">${declaration.pdf_filename}</a>
                ` : '❌ Aucun fichier';
                
                html += `
                    <tr>
                        <td>${startDate === endDate ? startDate : `${startDate} - ${endDate}`}</td>
                        <td>${declaration.description || 'Non spécifiée'}</td>
                        <td>${pdfCell}</td>
                        <td><span class="status-badge ${declaration.email_sent ? 'status-approuve' : 'status-refuse'}">${declaration.email_sent ? 'Envoyé' : 'Non envoyé'}</span></td>
                        <td>${createdDate}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
        }
        
        return html;
        
    } catch (error) {
        return `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    }
}

// Prévisualisation PDF dans une popup (modal simple)
function previewPdf(declarationId) {
    const url = `${CONFIG.API_BASE_URL}/sickness-declarations/${declarationId}/pdf`;
    // Ouvre dans un nouvel onglet si le navigateur bloque les modales
    const w = window.open(url, '_blank');
    if (!w) {
        // fallback si popups bloquées
        window.location.href = url;
    }
}

// Fonction pour charger les déclarations de maladie pour les admins
async function loadAllSicknessDeclarations() {
    try {
        let declarations = await apiCall('/sickness-declarations/');
        if (!Array.isArray(declarations)) {
            if (declarations && (declarations.error || declarations.detail)) {
                const msg = declarations.error || declarations.detail;
                return `<div class="alert alert-error">${msg}</div>`;
            }
            declarations = [];
        }
        
        let html = '<h3>🏥 Déclarations de Maladie - Vue Administrateur</h3>';
        
        if (declarations.length === 0) {
            html += '<div class="alert alert-info">Aucune déclaration de maladie pour le moment.</div>';
        } else {
            // Statistiques rapides
            const totalDeclarations = declarations.length;
            const emailsSent = declarations.filter(d => d.email_sent).length;
            const withPdf = declarations.filter(d => d.pdf_filename).length;
            const unviewed = declarations.filter(d => !d.viewed_by_admin).length;
            
            html += `
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; text-align: center;">
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: #3498db;">${totalDeclarations}</div>
                            <div style="color: #666; font-size: 12px;">Total</div>
                        </div>
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: ${emailsSent > 0 ? '#27ae60' : '#e74c3c'};">${emailsSent}</div>
                            <div style="color: #666; font-size: 12px;">Emails envoyés</div>
                        </div>
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: ${withPdf > 0 ? '#27ae60' : '#e74c3c'};">${withPdf}</div>
                            <div style="color: #666; font-size: 12px;">Avec PDF</div>
                        </div>
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: ${unviewed > 0 ? '#f39c12' : '#27ae60'};">${unviewed}</div>
                            <div style="color: #666; font-size: 12px;">Non vues</div>
                        </div>
                    </div>
                </div>
            `;
            
            html += '<table class="table"><thead><tr><th>👤 Utilisateur</th><th>📅 Période</th><th>📝 Description</th><th>📄 Document PDF</th><th>📧 Email</th><th>👁️ Statut Admin</th><th>🕐 Créée le</th><th>⚡ Actions</th></tr></thead><tbody>';
            
            declarations.forEach(declaration => {
                const startDate = new Date(declaration.start_date).toLocaleDateString('fr-FR');
                const endDate = new Date(declaration.end_date).toLocaleDateString('fr-FR');
                const createdDate = new Date(declaration.created_at).toLocaleDateString('fr-FR');
                
                // Style de la ligne selon le statut
                let rowStyle = '';
                if (!declaration.viewed_by_admin) {
                    rowStyle = 'background-color: #fff3cd; border-left: 3px solid #ffc107;';
                }
                
                // Statut du PDF avec plus de détails
                let pdfStatus = '❌ <span style="color: #e74c3c;">Aucun document</span>';
                if (declaration.pdf_filename) {
                    const url = `${CONFIG.API_BASE_URL}/sickness-declarations/${declaration.id}/pdf`;
                    pdfStatus = `✅ <a href="${url}" target="_blank" rel="noopener">${declaration.pdf_filename}</a>`;
                }
                
                // Statut email avec plus de clarté
                const emailStatus = declaration.email_sent ? 
                    '✅ <span style="color: #27ae60; font-weight: bold;">Envoyé</span>' : 
                    '❌ <span style="color: #e74c3c; font-weight: bold;">Non envoyé</span>';
                
                // Actions possibles
                let actions = '';
                if (!declaration.viewed_by_admin) {
                    actions += `<button class="btn btn-sm btn-success" onclick="markSicknessAsViewed(${declaration.id})" title="Marquer comme vue">👁️ Marquer vue</button> `;
                }
                if (declaration.pdf_filename && !declaration.email_sent) {
                    actions += `<button class="btn btn-sm btn-warning" onclick="resendSicknessEmail(${declaration.id})" title="Renvoyer l'email">📧 Renvoyer</button>`;
                }
                if (!actions) {
                    actions = '<span style="color: #666;">—</span>';
                }
                
                html += `
                    <tr style="${rowStyle}">
                        <td><strong>${declaration.user.first_name} ${declaration.user.last_name}</strong><br><small style="color: #666;">${declaration.user.email}</small></td>
                        <td><strong>${startDate === endDate ? startDate : `${startDate} - ${endDate}`}</strong></td>
                        <td>${declaration.description ? `<em>"${declaration.description}"</em>` : '<span style="color: #999;">Non spécifiée</span>'}</td>
                        <td>${pdfStatus}</td>
                        <td>${emailStatus}</td>
                        <td><span class="status-badge ${declaration.viewed_by_admin ? 'status-approuve' : 'status-en_attente'}">${declaration.viewed_by_admin ? '✅ Vue' : '⏳ À voir'}</span></td>
                        <td><small>${createdDate}</small></td>
                        <td>${actions}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
        }
        
        return html;
        
    } catch (error) {
        return `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    }
}

// Fonction pour marquer une déclaration comme vue par l'admin
async function markSicknessAsViewed(declarationId) {
    try {
        await apiCall(`/sickness-declarations/${declarationId}/mark-viewed`, {
            method: 'POST'
        });
        
        showAlert('Déclaration marquée comme vue !', 'success');
        // Recharger la liste
        loadAdminSicknessDeclarations();
        
    } catch (error) {
        showAlert(`Erreur: ${error.message}`, 'error');
    }
}

// Fonction pour renvoyer l'email d'une déclaration
async function resendSicknessEmail(declarationId) {
    if (!confirm('Voulez-vous vraiment renvoyer l\'email de cette déclaration de maladie ?')) {
        return;
    }
    
    try {
        await apiCall(`/sickness-declarations/${declarationId}/resend-email`, {
            method: 'POST'
        });
        
        showAlert('Email renvoyé avec succès !', 'success');
        // Recharger la liste
        loadAdminSicknessDeclarations();
        
    } catch (error) {
        showAlert(`Erreur lors de l'envoi: ${error.message}`, 'error');
    }
}