import oracledb
import datetime
from database import get_db_pool, fetch_data

def get_all_doctors():
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        return fetch_data(cursor, 'proc_get_all_doctors', [])

def get_doctor_by_id(doctor_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        rows = fetch_data(cursor, 'fn_get_doctor_by_id', [doctor_id], is_func=True)
        return rows[0] if rows else None

def create_doctor(doctor_data: dict):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        out_id = cursor.var(oracledb.NUMBER)
        
        # Convert date if it is a date object
        h_date = doctor_data['hire_date']
        if isinstance(h_date, str):
            h_date = datetime.datetime.strptime(h_date, '%Y-%m-%d').date()
            
        cursor.callproc('proc_create_doctor', [
            doctor_data['first_name'],
            doctor_data['last_name'],
            doctor_data['specialization'],
            doctor_data['dept_id'],
            doctor_data['phone'],
            doctor_data.get('email'),
            h_date,
            out_id
        ])
        doctor_id = int(out_id.getvalue()[0])
        conn.commit()
        return doctor_id

def get_departments():
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        return fetch_data(cursor, 'proc_get_departments', [])

def get_doctor_summary(doctor_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        return fetch_data(cursor, 'fn_get_doctor_summary', [doctor_id], is_func=True)
