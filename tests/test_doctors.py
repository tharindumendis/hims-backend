import pytest

def test_get_departments(client):
    response = client.get("/doctors/departments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "dept_id" in data[0]
        assert "dept_name" in data[0]

def test_get_all_doctors(client):
    response = client.get("/doctors/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        doctor = data[0]
        assert "doctor_id" in doctor
        assert "first_name" in doctor
        assert "specialization" in doctor

def test_create_and_get_doctor(client):
    # Fetch departments dynamically to get a valid dept_id
    dept_resp = client.get("/doctors/departments")
    assert dept_resp.status_code == 200
    depts = dept_resp.json()
    
    # Use the first dept_id, or default to 1 if empty (mock mode will have 1)
    dept_id = depts[0]["dept_id"] if depts else 1

    payload = {
        "first_name": "test_doc_fn",
        "last_name": "test_doc_ln",
        "specialization": "Pediatrics",
        "dept_id": dept_id,
        "phone": "0778888888",
        "email": "test_doctor@example.com",
        "hire_date": "2025-05-20"
    }

    # Create doctor
    create_resp = client.post("/doctors/", json=payload)
    assert create_resp.status_code == 200
    created_doctor = create_resp.json()
    assert "doctor_id" in created_doctor
    assert created_doctor["first_name"] == "test_doc_fn"
    doctor_id = created_doctor["doctor_id"]

    # Get doctor by id
    get_resp = client.get(f"/doctors/{doctor_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["doctor_id"] == doctor_id

def test_get_doctor_not_found(client):
    response = client.get("/doctors/404")
    assert response.status_code == 404
    assert response.json()["detail"] == "Doctor not found"

def test_get_doctor_summary(client):
    # Use created doctor or 999
    response = client.get("/doctors/999/summary")
    assert response.status_code == 200
    summary = response.json()
    assert isinstance(summary, list)
    if summary:
        assert "total_appointments" in summary[0]
        assert "unique_patients" in summary[0]
