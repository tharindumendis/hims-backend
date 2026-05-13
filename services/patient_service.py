from database import get_db_pool
from models.schemas import PatientCreate

def get_all_patients():
    pool = get_db_pool()
    query = """
        SELECT patient_id, first_name, last_name, date_of_birth, gender, 
               blood_type, phone, email, address, created_at,
               fn_get_patient_age(patient_id) as age
        FROM PATIENT
        ORDER BY last_name
    """
    rows = pool.execute_query(query)
    results = []
    for row in rows:
        results.append({
            "patient_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "date_of_birth": row[3],
            "gender": row[4],
            "blood_type": row[5],
            "phone": row[6],
            "email": row[7],
            "address": row[8],
            "created_at": row[9],
            "age": row[10]
        })
    return results

def get_patient_by_id(patient_id: int):
    pool = get_db_pool()
    query = """
        SELECT patient_id, first_name, last_name, date_of_birth, gender, 
               blood_type, phone, email, address, created_at,
               fn_get_patient_age(patient_id) as age
        FROM PATIENT
        WHERE patient_id = :1
    """
    rows = pool.execute_query(query, (patient_id,))
    if not rows:
        return None
    row = rows[0]
    return {
        "patient_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "date_of_birth": row[3],
        "gender": row[4],
        "blood_type": row[5],
        "phone": row[6],
        "email": row[7],
        "address": row[8],
        "created_at": row[9],
        "age": row[10]
    }

def create_patient(patient: PatientCreate):
    pool = get_db_pool()
    id_query = "SELECT seq_patient.nextval FROM DUAL"
    patient_id = pool.execute_query(id_query)[0][0]
    
    insert_query = """
        INSERT INTO PATIENT (patient_id, first_name, last_name, date_of_birth, gender, blood_type, phone, email, address)
        VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
    """
    params = (
        patient_id,
        patient.first_name,
        patient.last_name,
        patient.date_of_birth,
        patient.gender,
        patient.blood_type,
        patient.phone,
        patient.email,
        patient.address
    )
    pool.execute_update(insert_query, params)
    return get_patient_by_id(patient_id)

def get_patient_prescriptions(patient_id: int):
    pool = get_db_pool()
    query = """
        SELECT record_id, prescription_id, medicine_name, dosage, duration_days, quantity, status
        FROM vw_patient_prescription_history
        WHERE patient_id = :1
    """
    try:
        rows = pool.execute_query(query, (patient_id,))
        results = []
        for row in rows:
            results.append({
                "record_id": row[0],
                "prescription_id": row[1],
                "medicine_name": row[2],
                "dosage": row[3],
                "duration_days": row[4],
                "quantity": row[5],
                "status": row[6]
            })
        return results
    except Exception as e:
        return []
