import pytest
from fastapi.testclient import TestClient

class TestAuth:
    def test_login_success(self, client, admin_token):
        """Test connexion réussie"""
        response = client.post("/token", data={"username": "admin@test.com", "password": "testpassword"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, admin_token):
        """Test connexion avec mauvais mot de passe"""
        response = client.post("/token", data={"username": "admin@test.com", "password": "wrongpassword"})
        assert response.status_code == 401
    
    def test_login_wrong_email(self, client):
        """Test connexion avec email inexistant"""
        response = client.post("/token", data={"username": "wrong@test.com", "password": "testpassword"})
        assert response.status_code == 401
    
    def test_get_current_user(self, client, admin_token):
        """Test récupération de l'utilisateur connecté"""
        response = client.get("/users/me", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"
    
    def test_access_without_token(self, client):
        """Test accès sans token"""
        response = client.get("/users/me")
        assert response.status_code == 401
    
    def test_access_with_invalid_token(self, client):
        """Test accès avec token invalide"""
        response = client.get("/users/me", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401