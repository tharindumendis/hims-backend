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
        return rows[0] if rows else None

def create_stock_transaction(txn: StockTransactionBase):
    pool = get_db_pool()
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        txn_id = cursor.callfunc('fn_create_stock_txn', oracledb.NUMBER, [txn.medicine_id, txn.txn_type, txn.quantity, txn.reference_id, txn.performed_by])
        conn.commit()
        print(f"Transaction ID: {txn_id}")
        print(f"Medicine ID: {txn.medicine_id}")
        print(f"Transaction Type: {txn.txn_type}")
        print(f"Quantity: {txn.quantity}")
        print(f"Reference ID: {txn.reference_id}")
        print(f"Performed By: {txn.performed_by}")
        return get_stock_txn_by_id(txn_id)

        
    #     out_id = cursor.var(oracledb.NUMBER)

        
    #     cursor.callproc('proc_create_stock_txnn', [
    #         txn.medicine_id,
    #         txn.txn_type,
    #         txn.quantity,
    #         txn.reference_id,
    #         txn.performed_by,
    #         out_id
    #     ])
    #     txn_id = int(out_id.getvalue())
    #     conn.commit()
    # return get_stock_txn_by_id(txn_id)
