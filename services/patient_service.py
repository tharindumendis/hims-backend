from models.schemas import PatientOut
import oracledb
import datetime
from database import get_db_pool, fetch_data
from models.schemas import PatientCreate

import oracledb
        
def get_all_patients():
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        return fetch_data(cursor, 'proc_get_all_patients', [])


def get_patient_by_id(patient_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        
        rows = fetch_data(cursor, 'fn_get_patient_by_id', [patient_id], is_func=True)
        
        return rows[0] if rows else None

def create_patient(patient: PatientCreate):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        out_id = cursor.var(oracledb.NUMBER)
        
        dob = patient.date_of_birth
        if isinstance(dob, str):
            dob = datetime.datetime.strptime(dob, '%Y-%m-%d').date()

        cursor.callproc('proc_create_patient', [
            patient.first_name,
            patient.last_name,
            dob,
            patient.gender,
            patient.blood_type,
            patient.phone,
            patient.email,
            patient.address,
            out_id
        ])
        patient_id = int(out_id.getvalue())
        conn.commit()
        
    return get_patient_by_id(patient_id)

def get_patient_prescriptions(patient_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        return fetch_data(cursor, 'fn_get_patient_presc', [patient_id], is_func=True)
