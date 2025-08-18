// Tableau de bord
async function loadDashboard() {
    const dashboardContent = document.getElementById('dashboard-content');
    
    // Interface différente selon le rôle
    if (currentUser.role === 'admin') {
        // Dashboard pour administrateurs
        let html = '<h3>👨‍💼 Interface Administrateur</h3>';
        
        html += `
            <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin: 20px 0; border-left: 5px solid #34495e;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h4 style="color: #34495e; margin-bottom: 10px;">🔧 Outils d'Administration</h4>
                    <p style="color: #666;">Gérez les utilisateurs et validez les demandes d'absence via les onglets dédiés.</p>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #3498db;">
                        <h5 style="color: #3498db; margin-bottom: 10px;">👥 Utilisateurs</h5>
                        <p style="color: #666; font-size: 14px;">Gérer les comptes utilisateurs</p>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #f39c12;">
                        <h5 style="color: #f39c12; margin-bottom: 10px;">📋 Demandes</h5>
                        <p style="color: #666; font-size: 14px;">Approuver/refuser les demandes</p>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #27ae60;">
                        <h5 style="color: #27ae60; margin-bottom: 10px;">📅 Calendrier</h5>
                        <p style="color: #666; font-size: 14px;">Vue d'ensemble des absences</p>
                    </div>
                    
                </div>
            </div>
        `;
        
        dashboardContent.innerHTML = html;
        
    } else {
        // Dashboard pour utilisateurs normaux
        try {
			            // Appel direct à l'endpoint dashboard
			const dashboardData = await apiCall('/dashboard/');
            
			// Sécuriser et normaliser les valeurs numériques
			const usedDays = Number(dashboardData.used_leave_days) || 0;
			const totalDays = Number(dashboardData.total_leave_days) || 0;
			const remainingDays = Number(dashboardData.remaining_leave_days ?? (totalDays - usedDays)) || 0;
			const sickDays = Number(dashboardData.sick_days) || 0;
			
			let html = '<h3>🌴 Compteur de Congés Payés</h3>';
            
            // Calcul du pourcentage de congés utilisés pour la barre de progression
			const percentageUsed = totalDays > 0 ? (usedDays / totalDays) * 100 : 0;
            
            html += `
                <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin: 20px 0; border-left: 5px solid #3498db;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div style="text-align: center;">
							<div style="font-size: 24px; font-weight: bold; color: #27ae60;">${remainingDays}</div>
                            <div style="color: #666; font-size: 14px;">Jours restants</div>
                        </div>
                        <div style="text-align: center;">
							<div style="font-size: 24px; font-weight: bold; color: #e74c3c;">${usedDays}</div>
                            <div style="color: #666; font-size: 14px;">Jours utilisés</div>
                        </div>
                        <div style="text-align: center;">
							<div style="font-size: 24px; font-weight: bold; color: #3498db;">${totalDays}</div>
                            <div style="color: #666; font-size: 14px;">Total annuel</div>
                        </div>
                    </div>
                    <div style="background: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #27ae60 0%, #f39c12 70%, #e74c3c 100%); height: 100%; width: ${Math.min(percentageUsed, 100)}%; transition: width 0.3s ease;"></div>
                    </div>
                    <div style="text-align: center; margin-top: 10px; font-size: 14px; color: #666;">
                        ${percentageUsed.toFixed(1)}% des congés utilisés
                    </div>
                </div>
            `;
            
            // Section jours de maladie
            html += '<h3>🤒 Jours de Maladie</h3>';
            html += `
                <div style="background: #fff3cd; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 5px solid #ffc107;">
                    <div style="text-align: center;">
                        <div style="font-size: 28px; font-weight: bold; color: #856404;">${sickDays}</div>
                        <div style="color: #856404; font-size: 16px; margin-top: 5px;">Jours de maladie cette année</div>
                        <div style="color: #6c757d; font-size: 12px; margin-top: 5px;">
                            Inclut les demandes d'absence maladie et les déclarations avec certificat médical
                        </div>
                    </div>
                </div>
            `;
            
            html += '<h3>📊 Résumé de vos demandes</h3>';
            
            html += `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
                    <div style="background: #f39c12; color: white; padding: 20px; border-radius: 8px; text-align: center;">
                        <h4>En attente</h4>
						<h2>${Number(dashboardData.pending_requests) || 0}</h2>
                    </div>
                    <div style="background: #27ae60; color: white; padding: 20px; border-radius: 8px; text-align: center;">
                        <h4>Approuvées</h4>
						<h2>${Number(dashboardData.approved_requests) || 0}</h2>
                    </div>
                </div>
            `;
            
            dashboardContent.innerHTML = html;
            
        } catch (error) {
            dashboardContent.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
        }
    }
}