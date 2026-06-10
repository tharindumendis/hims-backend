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


# def get_patient_by_id(patient_id: int):
#     pool = get_db_pool()
#     with pool.get_connection() as conn:
#         cursor = conn.cursor()
#         rows = _fetch_cursor(cursor, 'proc_get_patient_by_id', [patient_id])
#         return rows[0] if rows else None

# def get_patient_by_id(patient_id: int):
#     print(f"Executing raw SQL fetch for ID: {patient_id}")
    
#     # Define the raw query manually
#     # Note: Oracle uses :1, :2 for positional parameters
#     query = """
#         SELECT patient_id, first_name, last_name, date_of_birth, gender, 
#                blood_type, phone, email, address, created_at,
#                fn_get_age(date_of_birth) as age
#         FROM PATIENT 
#         WHERE patient_id = :1
#     """
    
#     pool = get_db_pool()
#     try:
#         # Use the execute_query method from your OracleConnectionPool class
#         # It handles connection acquire/release and fetchall()
#         rows = pool.execute_query(query, (patient_id,))
        
#         if not rows:
#             print("No patient found.")
#             return None
            
#         # execute_query returns a list of tuples. 
#         # We need to map it to a dict for the Response Model.
#         row = rows[0]
#         columns = [
#             'patient_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 
#             'blood_type', 'phone', 'email', 'address', 'created_at', 'age'
#         ]
#         patient_data = dict(zip(columns, row))
        
#         print("Raw SQL Fetch successful!")
#         return patient_data

#     except Exception as e:
#         print(f"Raw SQL Fetch failed: {e}")
#         return None

# def get_patient_by_id(patient_id: int):
#     print("fun trigered")
#     pool = get_db_pool()
#     # Explicitly use a fresh connection for the ID lookup
#     with pool.get_connection() as conn:
#         cursor = conn.cursor()
#         # Ensure we pass the ID as a clean integer
#         rows = _fetch_cursor(cursor, 'proc_get_patient_by_id', [patient_id])
#         return rows[0] if rows else None