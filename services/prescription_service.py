from models.schemas import PrescriptionRow
from models.schemas import PrescriptionFullOut
from models.schemas import MedicalRecordCreate
import oracledb
from database import get_db_pool, fetch_data

def create_medical_record(record_data: MedicalRecordCreate):
    print("record_data",record_data)
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        out_id = cursor.var(oracledb.NUMBER)
        print("I am in prescription service",f"id: {out_id}", record_data)
        cursor.callproc('proc_create_medical_record', [
            record_data.appt_id,
            record_data.patient_id,
            record_data.doctor_id,
            record_data.diagnosis,
            record_data.notes,
            out_id
        ])
        record_id = int(out_id.getvalue())
        conn.commit()
        return record_id
import oracledb

def type_handler(cursor, metadata):
    # Check if the column type is a CLOB
    if metadata.type_code == oracledb.DB_TYPE_CLOB:
        return cursor.var(oracledb.DB_TYPE_LONG_NVARCHAR, arraysize=cursor.arraysize)

def get_medical_record_by_id(record_id: int):
    print("record_id",record_id)
    pool = get_db_pool()
    with pool.get_connection() as conn:
        conn.outputtypehandler = type_handler
        cursor = conn.cursor()
        rows = fetch_data(cursor, 'fn_get_medical_record', [record_id], is_func=True)
        print("rows",rows)
        return rows[0] if rows else None

def create_prescription(presc_data: dict):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        out_id = cursor.var(oracledb.NUMBER)
        
        # Insert prescription header
        cursor.callproc('proc_create_presc_header', [
            presc_data['record_id'],
            presc_data['doctor_id'],
            presc_data['status'],
            out_id
        ])
        presc_id = int(out_id.getvalue())
        
        # Insert items
        items = presc_data.get('items', [])
        for item in items:
            cursor.callproc('proc_create_presc_item', [
                presc_id,
                item['medicine_id'],
                item['dosage'],
                item['duration_days'],
                item['quantity']
            ])
            
        conn.commit()
        return presc_id

def get_prescription_by_id(presc_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        rows = fetch_data(cursor, 'fn_get_prescription', [presc_id], is_func=True)
        return rows[0] if rows else None

def get_pending_prescriptions():
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        return fetch_data(cursor, 'proc_get_pending_presc', [] )

def get_prescription_full_by_id(presc_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        rows = fetch_data(cursor, 'fn_get_prescription_full', [presc_id], is_func=True)
        if not rows:
            return None
        row_models = [PrescriptionRow(**row) for row in rows]
        return PrescriptionFullOut.from_rows(row_models)

def dispense_prescription(presc_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.callproc('proc_process_prescription', [presc_id])
        conn.commit()
