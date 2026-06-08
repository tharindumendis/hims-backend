from models.schemas import AppointmentCreate
import oracledb
import datetime
from database import get_db_pool, fetch_data

# def create_appointment(appt_data: AppointmentCreate):
#     print("I am in appointment service",appt_data)
#     pool = get_db_pool()
#     with pool.get_connection() as conn:
#         cursor = conn.cursor()
#         out_id = cursor.var(oracledb.NUMBER)
#         a_date = (2026, 5, 13)
#         if isinstance(a_date, str):
#             a_date = datetime.datetime.strptime(a_date, '%Y-%m-%d').date()

#         cursor.callproc('proc_create_appointment', [
#             1,  # NUMBER
#             1,   # NUMBER
#             (2026, 5, 13),   # DATE (Pydantic converts this to a python datetime.date)
#             "12:00",   # VARCHAR2 (The missing string parameter!)
#             "Scheduled",      # VARCHAR2
#             "Test Notes",       # VARCHAR2
#             out_id
#         ])
#         appt_id = int(out_id.getvalue()[0])
#         conn.commit()
#         return appt_id

def create_appointment(appt_data: AppointmentCreate):
    print("I am in appointment service", appt_data)
    pool = get_db_pool()
    
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Create the bucket to catch the returning ID
        out_id = cursor.var(oracledb.NUMBER)

        # 2. Call the procedure with exactly 7 arguments in the correct order
        cursor.callproc('proc_create_appointment', [
            appt_data.patient_id,  # NUMBER
            appt_data.doctor_id,   # NUMBER
            appt_data.appt_date,   # DATE (Pydantic converts this to a python datetime.date)
            appt_data.appt_time,   # VARCHAR2 (The missing string parameter!)
            appt_data.status,      # VARCHAR2
            appt_data.notes,       # VARCHAR2
            out_id                 # OUT NUMBER
        ])
        
        # 3. Extract the ID that Oracle generated
        val = out_id.getvalue()
        # Depending on the oracledb version, getvalue might return a list or float
        appt_id = int(val[0]) if isinstance(val, list) else int(val)
        
        # 4. Save the changes to the database
        conn.commit()
        
        return appt_id

def get_appointment_by_id(appt_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        rows = fetch_data(cursor, 'fn_get_appointment_by_id', [appt_id], is_func=True)
        return rows[0] if rows else None

def get_appointments_by_patient(patient_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        return fetch_data(cursor, 'fn_get_appts_by_patient', [patient_id], is_func=True)

def get_appointments_by_doctor(doctor_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        return fetch_data(cursor, 'fn_get_appts_by_doctor', [doctor_id], is_func=True)

def update_appointment_status(appt_id: int, status: str):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.callproc('proc_update_appt_status', [appt_id, status])
        conn.commit()
