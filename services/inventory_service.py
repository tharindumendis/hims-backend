from fastapi import HTTPException
import oracledb
from database import get_db_pool, fetch_data
from models.schemas import MedicineCreate, StockTransactionBase

def get_all_medicines():
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        return fetch_data(cursor, 'proc_get_all_medicines', [])

def get_medicine_by_id(medicine_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        rows = fetch_data(cursor, 'fn_get_medicine_by_id', [medicine_id], is_func=True)
        return rows[0] if rows else None

def create_medicine(medicine: MedicineCreate):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        out_id = cursor.var(oracledb.NUMBER)
        
        cursor.callproc('proc_create_medicine', [
            medicine.medicine_name,
            medicine.generic_name,
            medicine.category,
            medicine.unit,
            medicine.reorder_level,
            medicine.unit_price,
            out_id
        ])
        medicine_id = int(out_id.getvalue())
        conn.commit()
    return get_medicine_by_id(medicine_id)

def get_low_stock_medicines():
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        try:
            return fetch_data(cursor, 'proc_get_low_stock', [])
        except Exception as e:
            print(f"Error in getting low stock medicines: {e}")
            return []

def get_stock_txn_by_id(txn_id: int):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        rows = fetch_data(cursor, 'fn_get_stock_txn', [txn_id],True)
        print("ROWS:", rows)
        return rows[0] if rows else None

def create_stock_transaction(txn: StockTransactionBase):
    pool = get_db_pool()
    print(f"Creating stock transaction: {txn}")
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        txn_id = cursor.callfunc('fn_create_stock_txn', oracledb.NUMBER, [txn.medicine_id, txn.txn_type, txn.quantity, txn.reference_id, txn.performed_by])
        conn.commit()
        print("TXN ID:", txn_id)
        result = get_stock_txn_by_id(txn_id)

        if result is None:
            raise HTTPException(status_code=500, detail="Transaction not found after insert")

        return result

        
def get_stock():
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.stock_id,
                s.medicine_id,
                m.medicine_name,
                m.generic_name,
                m.category,
                s.quantity_available,
                m.reorder_level,
                s.expiry_date,
                s.storage_location,
                s.last_updated,
                fn_get_stock_status(m.medicine_id) AS stock_status
            FROM STOCK s
            JOIN MEDICINE m ON s.medicine_id = m.medicine_id
            ORDER BY m.medicine_name
        """)
        cols = [col[0].lower() for col in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

def get_expiring_stock():
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vw_expiring_stock")
        cols = [col[0].lower() for col in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
