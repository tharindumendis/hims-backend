import pytest

def test_get_all_patients(client):
    response = client.get("/patients/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        patient = data[0]
        assert "patient_id" in patient
        assert "first_name" in patient
        assert "email" in patient

def test_get_patient_by_id(client):
    # Retrieve a patient that exists
    # Use ID 999 since it is stubbed in mocks, or we will query/create one in integration mode
    # For integration mode, we first create a patient to ensure they exist, then get them
    create_payload = {
        "first_name": "test_get_fn",
        "last_name": "test_get_ln",
        "date_of_birth": "1990-01-01",
        "gender": "M",
        "blood_type": "O+",
        "phone": "0771112222",
        "email": "test_get_patient@example.com",
        "address": "test_address"
    }
    create_resp = client.post("/patients/", json=create_payload)
    assert create_resp.status_code == 200
    created_id = create_resp.json()["patient_id"]

    response = client.get(f"/patients/{created_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == created_id
    assert data["email"] == "test_get_patient@example.com"

def test_get_patient_not_found(client):
    response = client.get("/patients/404")
    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"

def test_create_patient(client):
    payload = {
        "first_name": "test_create_fn",
        "last_name": "test_create_ln",
        "date_of_birth": "1995-10-25",
        "gender": "F",
        "blood_type": "B-",
        "phone": "0773334444",
        "email": "test_create_patient@example.com",
        "address": "test_address"
    }
    response = client.post("/patients/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "patient_id" in data
    assert data["first_name"] == "test_create_fn"
    assert data["email"] == "test_create_patient@example.com"

def test_create_patient_validation(client):
    # Invalid gender field (should fail pattern validation)
    payload = {
        "first_name": "test_fail_fn",
        "last_name": "test_fail_ln",
        "date_of_birth": "1995-10-25",
        "gender": "X",  # Invalid
        "blood_type": "B-",
        "phone": "0773334444",
        "email": "invalid-email", # Invalid
        "address": "test_address"
    }
    response = client.post("/patients/", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (Validation Error)

def test_get_patient_prescriptions(client):
    # Create patient first to query
    create_payload = {
        "first_name": "test_presc_fn",
        "last_name": "test_presc_ln",
        "date_of_birth": "1988-08-08",
        "gender": "O",
        "blood_type": "AB+",
        "phone": "0775556666",
        "email": "test_presc_patient@example.com",
        "address": "test_address"
    }
    create_resp = client.post("/patients/", json=create_payload)
    assert create_resp.status_code == 200
    patient_id = create_resp.json()["patient_id"]

    response = client.get(f"/patients/{patient_id}/prescriptions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
