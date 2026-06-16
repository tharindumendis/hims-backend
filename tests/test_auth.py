import os
import pytest
from fastapi.testclient import TestClient
from models.schemas import (
    UserCreate,
    ChangePasswordRequest,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest
)

TEST_MODE = os.getenv("TEST_MODE", "mock").lower()

MOCK_USERS = {}

@pytest.fixture(autouse=True)
def setup_mock_auth():
    if TEST_MODE != "integration":
        from tests.conftest import MOCK_DATA
        from core.security import get_password_hash
        import datetime
        
        MOCK_DATA["users"].clear()
        
        # Seed default admin in mock DB
        MOCK_DATA["users"]["admin"] = {
            "user_id": 1,
            "username": "admin",
            "hashed_password": get_password_hash("admin123"),
            "role": "ADMIN",
            "is_active": 1,
            "created_at": datetime.datetime.now()
        }

@pytest.fixture(autouse=True)
def integration_cleanup():
    yield
    if TEST_MODE == "integration":
        from database import get_db_pool
        pool = get_db_pool()
        try:
            with pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Clean up all created test users
                    cursor.execute("DELETE FROM users WHERE username LIKE 'test_%'")
                    conn.commit()
        except Exception as e:
            print(f"Error cleaning up test users: {e}")

def test_admin_seeding(client):
    # Call health check or trigger app startup so admin is seeded
    # We call database seed directly or make sure admin exists
    if TEST_MODE == "integration":
        from routers.auth import seed_admin_user
        seed_admin_user()
    
    # Login as admin
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    token = response.json()
    assert "access_token" in token

def test_register_user_by_admin(client):
    # Log in as admin
    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    admin_token = login_resp.json()["access_token"]
    
    # Register receptionist
    payload = {
        "username": "test_receptionist",
        "role": "RECEPTIONIST",
        "password": "receptionistpassword",
        "is_active": True
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/auth/register", json=payload, headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "test_receptionist"
    assert user_data["role"] == "RECEPTIONIST"

def test_register_user_by_non_admin_fails(client):
    # Log in as admin
    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    admin_token = login_resp.json()["access_token"]
    
    # Register receptionist
    payload = {
        "username": "test_receptionist2",
        "role": "RECEPTIONIST",
        "password": "receptionistpassword",
        "is_active": True
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    client.post("/auth/register", json=payload, headers=headers)
    
    # Login as receptionist
    login_resp = client.post(
        "/auth/token",
        data={"username": "test_receptionist2", "password": "receptionistpassword"}
    )
    receptionist_token = login_resp.json()["access_token"]
    
    # Try to register a doctor as receptionist
    payload2 = {
        "username": "test_doctor",
        "role": "DOCTOR",
        "password": "doctorpassword",
        "is_active": True
    }
    headers2 = {"Authorization": f"Bearer {receptionist_token}"}
    response = client.post("/auth/register", json=payload2, headers=headers2)
    assert response.status_code == 403

def test_change_password(client):
    # Admin creates user test_changepwd
    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    admin_token = login_resp.json()["access_token"]
    
    payload = {
        "username": "test_changepwd",
        "role": "PHARMACIST",
        "password": "oldpassword123",
        "is_active": True
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    client.post("/auth/register", json=payload, headers=headers)
    
    # Login as user
    login_resp = client.post(
        "/auth/token",
        data={"username": "test_changepwd", "password": "oldpassword123"}
    )
    user_token = login_resp.json()["access_token"]
    
    # Change password
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post(
        "/auth/change-password",
        json={"old_password": "oldpassword123", "new_password": "newpassword123"},
        headers=headers
    )
    assert response.status_code == 200
    
    # Login with new password
    new_login_resp = client.post(
        "/auth/token",
        data={"username": "test_changepwd", "password": "newpassword123"}
    )
    assert new_login_resp.status_code == 200
    assert "access_token" in new_login_resp.json()

def test_change_password_invalid_old_fails(client):
    # Admin creates user test_changepwd_fail
    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    admin_token = login_resp.json()["access_token"]
    
    payload = {
        "username": "test_changepwd_fail",
        "role": "PHARMACIST",
        "password": "oldpassword123",
        "is_active": True
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    client.post("/auth/register", json=payload, headers=headers)
    
    # Login as user
    login_resp = client.post(
        "/auth/token",
        data={"username": "test_changepwd_fail", "password": "oldpassword123"}
    )
    user_token = login_resp.json()["access_token"]
    
    # Change password with wrong old password
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post(
        "/auth/change-password",
        json={"old_password": "wrongpassword", "new_password": "newpassword123"},
        headers=headers
    )
    assert response.status_code == 400

def test_deactivate_user_by_admin(client):
    # Admin registers user test_deactivate
    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    admin_token = login_resp.json()["access_token"]
    
    payload = {
        "username": "test_deactivate",
        "role": "DOCTOR",
        "password": "password123",
        "is_active": True
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    client.post("/auth/register", json=payload, headers=headers)
    
    # Admin deactivates user
    response = client.put(
        "/auth/users/test_deactivate/status",
        json={"is_active": False},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Login fails for deactivated user
    login_resp = client.post(
        "/auth/token",
        data={"username": "test_deactivate", "password": "password123"}
    )
    assert login_resp.status_code == 403
    assert "deactivated" in login_resp.json()["detail"].lower()

def test_self_deactivation_guard(client):
    # Log in as admin
    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    admin_token = login_resp.json()["access_token"]
    
    # Try to self-deactivate
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(
        "/auth/users/admin/status",
        json={"is_active": False},
        headers=headers
    )
    assert response.status_code == 400
    assert "cannot deactivate their own account" in response.json()["detail"].lower()

def test_change_role_by_admin(client):
    # Admin registers user test_rolechange
    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    admin_token = login_resp.json()["access_token"]
    
    payload = {
        "username": "test_rolechange",
        "role": "RECEPTIONIST",
        "password": "password123",
        "is_active": True
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    client.post("/auth/register", json=payload, headers=headers)
    
    # Admin changes user role to PHARMACIST
    response = client.put(
        "/auth/users/test_rolechange/role",
        json={"role": "PHARMACIST"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["role"] == "PHARMACIST"

def test_register_doctor_with_valid_doctor_id(client):
    # Log in as admin
    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    admin_token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get a valid doctor_id
    doctor_id = 999  # default for mock mode
    if TEST_MODE == "integration":
        doc_resp = client.get("/doctors/", headers=headers)
        assert doc_resp.status_code == 200
        docs = doc_resp.json()
        if docs:
            doctor_id = docs[0]["doctor_id"]
        else:
            dept_resp = client.get("/doctors/departments", headers=headers)
            depts = dept_resp.json()
            dept_id = depts[0]["dept_id"] if depts else 1
            
            payload_doc = {
                "first_name": "test_doc_fn",
                "last_name": "test_doc_ln",
                "specialization": "Pediatrics",
                "dept_id": dept_id,
                "phone": "0778888888",
                "email": "test_doctor@example.com",
                "hire_date": "2025-05-20"
            }
            create_resp = client.post("/doctors/", json=payload_doc, headers=headers)
            assert create_resp.status_code == 200
            doctor_id = create_resp.json()["doctor_id"]
            
    # Register doctor user linked to that doctor_id
    payload = {
        "username": "test_doctor_user",
        "role": "DOCTOR",
        "password": "doctorpassword",
        "is_active": True,
        "doctor_id": doctor_id
    }
    response = client.post("/auth/register", json=payload, headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "test_doctor_user"
    assert user_data["role"] == "DOCTOR"
    assert user_data["doctor_id"] == doctor_id
    
    # Login as this doctor
    login_resp = client.post(
        "/auth/token",
        data={"username": "test_doctor_user", "password": "doctorpassword"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()
    assert "access_token" in token
    
    # Verify token payload includes doctor_id
    from jose import jwt
    from core.security import SECRET_KEY, ALGORITHM
    payload = jwt.decode(token["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("doctor_id") == doctor_id

def test_register_doctor_with_invalid_doctor_id_fails(client):
    # Log in as admin
    login_resp = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    admin_token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to register a doctor linked to invalid doctor_id (99999)
    payload = {
        "username": "test_doctor_invalid",
        "role": "DOCTOR",
        "password": "doctorpassword",
        "is_active": True,
        "doctor_id": 99999
    }
    response = client.post("/auth/register", json=payload, headers=headers)
    assert response.status_code == 400
    assert "doctor" in response.json()["detail"].lower()
