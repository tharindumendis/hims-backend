import pytest

def test_create_and_manage_appointment(client):
    # 1. Create a patient
    patient_payload = {
        "first_name": "test_appt_pf",
        "last_name": "test_appt_pl",
        "date_of_birth": "1992-02-02",
        "gender": "F",
        "blood_type": "A-",
        "phone": "0770001111",
        "email": "test_appt_pat@example.com",
        "address": "test_address"
    }
    pat_resp = client.post("/patients/", json=patient_payload)
    assert pat_resp.status_code == 200
    patient_id = pat_resp.json()["patient_id"]

    # 2. Create a doctor
    dept_resp = client.get("/doctors/departments")
    assert dept_resp.status_code == 200
    depts = dept_resp.json()
    dept_id = depts[0]["dept_id"] if depts else 1

    doctor_payload = {
        "first_name": "test_appt_df",
        "last_name": "test_appt_dl",
        "specialization": "Pediatrics",
        "dept_id": dept_id,
        "phone": "0771110000",
        "email": "test_appt_doc@example.com",
        "hire_date": "2024-01-01"
    }
    doc_resp = client.post("/doctors/", json=doctor_payload)
    assert doc_resp.status_code == 200
    doctor_id = doc_resp.json()["doctor_id"]

    # 3. Create appointment
    appt_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appt_date": "2026-06-20",
        "appt_time": "09:00",
        "status": "Scheduled",
        "notes": "test_appointment_notes"
    }
    appt_resp = client.post("/appointments/", json=appt_payload)
    assert appt_resp.status_code == 200
    appt_data = appt_resp.json()
    assert "appt_id" in appt_data
    appt_id = appt_data["appt_id"]

    # 4. Fetch by Patient
    by_pat_resp = client.get(f"/appointments/patient/{patient_id}")
    assert by_pat_resp.status_code == 200
    by_pat_data = by_pat_resp.json()
    assert isinstance(by_pat_data, list)
    assert any(a["appt_id"] == appt_id for a in by_pat_data)

    # 5. Fetch by Doctor
    by_doc_resp = client.get(f"/appointments/doctor/{doctor_id}")
    assert by_doc_resp.status_code == 200
    by_doc_data = by_doc_resp.json()
    assert isinstance(by_doc_data, list)
    assert any(a["appt_id"] == appt_id for a in by_doc_data)

    # 6. Update Status
    update_resp = client.put(f"/appointments/{appt_id}/status", json={"status": "Completed"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "Completed"

def test_update_appointment_invalid_status(client):
    # Use 999 as appt_id (stubbed or dummy)
    response = client.put("/appointments/999/status", json={"status": "InvalidStatus"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid status"

def test_update_appointment_not_found(client):
    response = client.put("/appointments/404/status", json={"status": "Cancelled"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"
