from database import get_db_pool
from models.schemas import MedicineCreate, StockTransactionBase

def get_all_medicines():
    pool = get_db_pool()
    query = """
        SELECT medicine_id, medicine_name, generic_name, category, unit, reorder_level, unit_price
        FROM MEDICINE
        ORDER BY medicine_name
    """
    rows = pool.execute_query(query)
    return [
        {
            "medicine_id": row[0],
            "medicine_name": row[1],
            "generic_name": row[2],
            "category": row[3],
            "unit": row[4],
            "reorder_level": row[5],
            "unit_price": row[6]
        } for row in rows
    ]

def get_medicine_by_id(medicine_id: int):
    pool = get_db_pool()
    query = """
        SELECT medicine_id, medicine_name, generic_name, category, unit, reorder_level, unit_price
        FROM MEDICINE
        WHERE medicine_id = :1
    """
    rows = pool.execute_query(query, (medicine_id,))
    if not rows:
        return None
    row = rows[0]
    return {
        "medicine_id": row[0],
        "medicine_name": row[1],
        "generic_name": row[2],
        "category": row[3],
        "unit": row[4],
        "reorder_level": row[5],
        "unit_price": row[6]
    }

def create_medicine(medicine: MedicineCreate):
    pool = get_db_pool()
    id_query = "SELECT seq_medicine.nextval FROM DUAL"
    medicine_id = pool.execute_query(id_query)[0][0]
    
    insert_query = """
        INSERT INTO MEDICINE (medicine_id, medicine_name, generic_name, category, unit, reorder_level, unit_price)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
    """
    params = (
        medicine_id,
        medicine.medicine_name,
        medicine.generic_name,
        medicine.category,
        medicine.unit,
        medicine.reorder_level,
        medicine.unit_price
    )
    pool.execute_update(insert_query, params)
    
    # Also create an initial stock record for this medicine
    stock_id_query = "SELECT seq_stock.nextval FROM DUAL"
    stock_id = pool.execute_query(stock_id_query)[0][0]
    stock_insert = """
        INSERT INTO STOCK (stock_id, medicine_id, quantity_available)
        VALUES (:1, :2, 0)
    """
    pool.execute_update(stock_insert, (stock_id, medicine_id))
    
    return get_medicine_by_id(medicine_id)

def get_low_stock_medicines():
    pool = get_db_pool()
    query = """
        SELECT medicine_id, medicine_name, category, quantity_available, reorder_level, shortage_qty, stock_status
        FROM vw_low_stock_medicines
    """
    try:
        rows = pool.execute_query(query)
        return [
            {
                "medicine_id": row[0],
                "medicine_name": row[1],
                "category": row[2],
                "quantity_available": row[3],
                "reorder_level": row[4],
                "shortage_qty": row[5],
                "stock_status": row[6]
            } for row in rows
        ]
    except Exception as e:
        return []

def create_stock_transaction(txn: StockTransactionBase):
    pool = get_db_pool()
    id_query = "SELECT seq_stock_txn.nextval FROM DUAL"
    txn_id = pool.execute_query(id_query)[0][0]
    
    insert_query = """
        INSERT INTO STOCK_TRANSACTION (txn_id, medicine_id, txn_type, quantity, reference_id, performed_by)
        VALUES (:1, :2, :3, :4, :5, :6)
    """
    params = (
        txn_id,
        txn.medicine_id,
        txn.txn_type,
        txn.quantity,
        txn.reference_id,
        txn.performed_by
    )
    pool.execute_update(insert_query, params)
    
    # Get the created transaction
    select_query = """
        SELECT txn_id, medicine_id, txn_type, quantity, reference_id, performed_by, txn_date
        FROM STOCK_TRANSACTION
        WHERE txn_id = :1
    """
    row = pool.execute_query(select_query, (txn_id,))[0]
    return {
        "txn_id": row[0],
        "medicine_id": row[1],
        "txn_type": row[2],
        "quantity": row[3],
        "reference_id": row[4],
        "performed_by": row[5],
        "txn_date": row[6]
    }
