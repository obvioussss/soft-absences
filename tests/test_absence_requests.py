import pytest
from datetime import datetime, timedelta, date
from unittest.mock import patch, MagicMock
# Les fixtures sont maintenant dans conftest.py

class TestAbsenceRequests:
    def test_create_absence_request(self, client, user_token):
        """Test création d'une demande d'absence"""
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=3)
        
        request_data = {
            "type": "vacances",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "reason": "Vacances d'été"
        }
        
        response = client.post(
            "/absence-requests/",
            json=request_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "vacances"
        assert data["status"] == "en_attente"
        assert data["reason"] == "Vacances d'été"
    
    def test_get_my_requests_as_user(self, client, user_token):
        """Test récupération de ses propres demandes par un utilisateur"""
        response = client.get("/absence-requests/", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_all_requests_as_admin(self, client, admin_token):
        """Test récupération de toutes les demandes par un admin"""
        response = client.get("/absence-requests/", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_request_status_as_admin(self, client, admin_token, user_token):
        """Test mise à jour du statut d'une demande par un admin"""
        # Créer d'abord une demande
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=3)
        
        request_data = {
            "type": "vacances",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "reason": "Vacances d'été"
        }
        
        response = client.post(
            "/absence-requests/",
            json=request_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        request_id = response.json()["id"]
        
        # Approuver la demande
        status_update = {
            "status": "approuve",
            "admin_comment": "Demande approuvée"
        }
        
        response = client.put(
            f"/absence-requests/{request_id}/status",
            json=status_update,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approuve"
        assert data["admin_comment"] == "Demande approuvée"
    
    def test_update_request_status_as_user_forbidden(self, client, user_token):
        """Test mise à jour du statut d'une demande par un utilisateur (interdit)"""
        status_update = {
            "status": "approuve"
        }
        
        response = client.put(
            "/absence-requests/1/status",
            json=status_update,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
    
    def test_update_own_request_as_user(self, client, user_token):
        """Test modification de sa propre demande par un utilisateur"""
        # Créer d'abord une demande
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=3)
        
        request_data = {
            "type": "vacances",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "reason": "Vacances d'été"
        }
        
        response = client.post(
            "/absence-requests/",
            json=request_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        request_id = response.json()["id"]
        
        # Modifier la demande
        update_data = {
            "reason": "Vacances modifiées"
        }
        
        response = client.put(
            f"/absence-requests/{request_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reason"] == "Vacances modifiées"
    
    def test_delete_own_request_as_user(self, client, user_token):
        """Test suppression de sa propre demande par un utilisateur"""
        # Créer d'abord une demande
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=3)
        
        request_data = {
            "type": "vacances",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "reason": "Vacances d'été"
        }
        
        response = client.post(
            "/absence-requests/",
            json=request_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        request_id = response.json()["id"]
        
        # Supprimer la demande
        response = client.delete(
            f"/absence-requests/{request_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        
        # Vérifier que la demande n'existe plus
        response = client.get(
            f"/absence-requests/{request_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 404
    
    def test_get_calendar_events(self, client, admin_token, user_token):
        """Test récupération des événements du calendrier"""
        # Créer et approuver une demande
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=3)
        
        request_data = {
            "type": "vacances",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "reason": "Vacances d'été"
        }
        
        # Créer la demande
        response = client.post(
            "/absence-requests/",
            json=request_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        request_id = response.json()["id"]
        
        # Approuver la demande
        status_update = {
            "status": "approuve",
            "admin_comment": "Demande approuvée"
        }
        
        client.put(
            f"/absence-requests/{request_id}/status",
            json=status_update,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Récupérer les événements du calendrier pour l'utilisateur
        current_year = datetime.now().year
        
        response = client.get(
            f"/calendar/user?year={current_year}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # Au moins notre événement approuvé
    
    @patch('app.email_service.email_service.send_absence_modification_notification')
    def test_update_request_sends_admin_notification(self, mock_email, client, user_token):
        """Test que la modification d'une demande envoie une notification aux admins"""
        # Créer d'abord une demande
        start_date = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=3)
        
        request_data = {
            "type": "vacances",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "reason": "Vacances d'été"
        }
        
        response = client.post(
            "/absence-requests/",
            json=request_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        request_id = response.json()["id"]
        
        # Modifier la demande
        update_data = {
            "reason": "Vacances modifiées"
        }
        
        response = client.put(
            f"/absence-requests/{request_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        
        # Vérifier que la notification a été envoyée
        mock_email.assert_called_once()
        call_args = mock_email.call_args
        assert call_args[1]['absence_type'] == 'vacances'
        assert call_args[1]['reason'] == 'Vacances modifiées'
        assert call_args[1]['request_id'] == request_id
    
    @patch('app.email_service.email_service.send_absence_deletion_notification')
    def test_delete_request_sends_admin_notification(self, mock_email, client, user_token):
        """Test que la suppression d'une demande envoie une notification aux admins"""
        # Créer d'abord une demande
        start_date = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=3)
        
        request_data = {
            "type": "maladie",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "reason": "Grippe"
        }
        
        response = client.post(
            "/absence-requests/",
            json=request_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        request_id = response.json()["id"]
        
        # Supprimer la demande
        response = client.delete(
            f"/absence-requests/{request_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        
        # Vérifier que la notification a été envoyée
        mock_email.assert_called_once()
        call_args = mock_email.call_args
        assert call_args[1]['absence_type'] == 'maladie'
        assert call_args[1]['reason'] == 'Grippe'
        assert call_args[1]['request_id'] == request_id