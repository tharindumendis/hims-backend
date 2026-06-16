# PL/SQL Reference Guide for Backend Developers

This document serves as a guide for backend developers interacting with the Oracle 21c Database. It outlines the stored procedures, functions, views, and triggers implemented in the database, including how to invoke them using `python-oracledb`, their expected inputs/outputs, and potential errors.

---

## 1. Stored Procedures (`proc_*`)

Stored procedures are used for complex transactions that modify multiple tables. In FastAPI, invoke them using `cursor.callproc()`.

### `proc_process_prescription`
**Purpose:** Dispenses a prescription. It iterates through all `PRESCRIPTION_ITEM`s, deducts stock by creating `OUT` transactions in `STOCK_TRANSACTION`, and marks the prescription as `Dispensed`.

- **Input Parameters:**
  - `p_prescription_id` (NUMBER): ID of the prescription to process.
- **Output:** None (Commits transaction internally or relies on backend commit).
- **Backend Invocation:**
  ```python
  cursor.callproc('proc_process_prescription', [prescription_id])
  ```
- **Expected Errors (`oracledb.DatabaseError`):**
  - **ORA-02291 (Integrity Constraint Violation):** Prescription ID does not exist.
  - **Custom App Error:** If stock goes negative (if a constraint exists on `STOCK`).

### `proc_create_purchase_order`
**Purpose:** Creates a Draft `PURCHASE_ORDER` and inserts a single `PO_ITEM`. Returns the auto-generated `po_id`.

- **Input Parameters:**
  - `p_supplier_id` (NUMBER)
  - `p_medicine_id` (NUMBER)
  - `p_quantity` (NUMBER)
  - `p_unit_price` (NUMBER)
- **Output Parameter:**
  - `p_po_id` (OUT NUMBER): Returns the newly generated ID.
- **Backend Invocation:**
  ```python
  out_id = cursor.var(oracledb.NUMBER)
  cursor.callproc('proc_create_purchase_order', [supplier_id, medicine_id, quantity, price, out_id])
  po_id = int(out_id.getvalue())
  ```
- **Expected Errors:**
  - **ORA-02291:** Invalid Supplier ID or Medicine ID.

### `proc_receive_purchase_order`
**Purpose:** Receives a PO, loops through its items, generates `IN` transactions for `STOCK_TRANSACTION`, and updates PO status to `Received`.

- **Input Parameters:**
  - `p_po_id` (NUMBER)
- **Backend Invocation:**
  ```python
  cursor.callproc('proc_receive_purchase_order', [po_id])
  ```

---

## 2. User-Defined Functions (`fn_*`)

Functions return a single scalar value. In FastAPI, invoke them using `cursor.callfunc()`.

### `fn_get_age`
**Purpose:** Calculates age based on `date_of_birth`.
- **Input:** `p_date_of_birth` (DATE)
- **Returns:** NUMBER
- **Backend Invocation:**
  ```python
  age = cursor.callfunc('fn_get_age', oracledb.NUMBER, [date_of_birth])
  ```

### `fn_get_stock_status`
**Purpose:** Returns the status of a medicine's stock relative to its reorder level.
- **Input:** `p_medicine_id` (NUMBER)
- **Returns:** VARCHAR2 (`'CRITICAL'`, `'LOW'`, or `'ADEQUATE'`)
- **Backend Invocation:**
  ```python
  status = cursor.callfunc('fn_get_stock_status', oracledb.STRING, [medicine_id])
  ```

---

## 3. Database Views (`vw_*`)

Views should be queried using standard `SELECT * FROM vw_name` using `cursor.execute()`. They are read-only.

- **`vw_low_stock_medicines`**: Lists medicines where `quantity_available < reorder_level`. Used for reorder alerts.
- **`vw_patient_prescription_history`**: Denormalized patient prescription history. Used heavily by the Apriori mining module.
- **`vw_doctor_appointment_summary`**: Aggregated appointment counts grouped by doctor and status.
- **`vw_monthly_stock_consumption`**: Aggregates `OUT` transactions. Used for time-series trend analysis in BI module.
- **`vw_pending_prescriptions`**: Active prescriptions awaiting pharmacy fulfillment.
- **`vw_supplier_performance`**: Aggregated delivery metrics for suppliers.

**Backend Invocation Example:**
```python
cursor.execute("SELECT * FROM vw_pending_prescriptions")
columns = [col[0].lower() for col in cursor.description]
results = [dict(zip(columns, row)) for row in cursor.fetchall()]
```

---

## 4. Triggers (`trg_*`)

Triggers execute automatically in the background. Backend developers do not call them directly but **must handle the errors or side effects** they produce.

- **`trg_update_stock_on_txn`**: Fires `AFTER INSERT` on `STOCK_TRANSACTION`. Adds or subtracts from `STOCK.quantity_available`.
  - **Developer Note:** Never update `STOCK.quantity_available` manually in backend Python code. Always insert a `STOCK_TRANSACTION`.
- **`trg_low_stock_alert`**: Fires `AFTER UPDATE` on `STOCK`. If stock falls below `reorder_level`, it logs an alert.
- **`trg_po_total_update`**: Fires `AFTER INSERT/UPDATE` on `PO_ITEM`. Recalculates `PURCHASE_ORDER.total_amount`.

---

## 5. Standard Error Handling Pattern

Whenever interacting with Oracle DB through `python-oracledb`, wrap executions in a `try-except` block to catch `oracledb.DatabaseError`. Extract the error message and raise an HTTP Exception for the frontend.

```python
import oracledb
from fastapi import HTTPException

try:
    cursor.execute(...)
    conn.commit()
except oracledb.DatabaseError as e:
    error_obj, = e.args
    # error_obj.code contains the ORA-XXXXX error code
    # error_obj.message contains the descriptive text
    raise HTTPException(status_code=400, detail=error_obj.message)
```
