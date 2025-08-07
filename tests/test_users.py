import pytest
# Les fixtures sont maintenant dans conftest.py

class TestUsers:
    def test_create_user_as_admin(self, client, admin_token):
        """Test création d'utilisateur par un admin"""
        user_data = {
            "email": "newuser@test.com",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
            "role": "user"
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["role"] == user_data["role"]
    
    def test_create_user_as_user_forbidden(self, client, user_token):
        """Test création d'utilisateur par un utilisateur normal (interdit)"""
        user_data = {
            "email": "newuser2@test.com",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
            "role": "user"
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
    
    def test_create_user_duplicate_email(self, client, admin_token):
        """Test création d'utilisateur avec email existant"""
        user_data = {
            "email": "admin@test.com",  # Email déjà utilisé
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
            "role": "user"
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
    
    def test_get_users_as_admin(self, client, admin_token):
        """Test récupération de la liste des utilisateurs par un admin"""
        response = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # Au moins l'admin
    
    def test_get_users_as_user_forbidden(self, client, user_token):
        """Test récupération de la liste des utilisateurs par un utilisateur normal (interdit)"""
        response = client.get("/users/", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 403
    
    def test_get_user_by_id_as_admin(self, client, admin_token):
        """Test récupération d'un utilisateur par ID par un admin"""
        response = client.get("/users/1", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
    
    def test_get_nonexistent_user(self, client, admin_token):
        """Test récupération d'un utilisateur inexistant"""
        response = client.get("/users/999", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 404
    
    def test_update_user_as_admin(self, client, admin_token):
        """Test mise à jour d'un utilisateur par un admin"""
        # D'abord créer un utilisateur
        user_data = {
            "email": "updateuser@test.com",
            "password": "password",
            "first_name": "Original",
            "last_name": "User",
            "role": "user"
        }
        
        create_response = client.post(
            "/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        user_id = create_response.json()["id"]
        
        # Maintenant mettre à jour l'utilisateur
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        
        response = client.put(
            f"/users/{user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
    
    def test_update_user_as_user_forbidden(self, client, user_token):
        """Test mise à jour d'un utilisateur par un utilisateur normal (interdit)"""
        update_data = {
            "first_name": "Updated"
        }
        
        response = client.put(
            "/users/1",
            json=update_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403