import os
import sys
import datetime
from unittest.mock import MagicMock
import pytest

# Ensure backend directory is in sys.path so imports resolve correctly
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Determine testing mode
TEST_MODE = os.getenv("TEST_MODE", "mock").lower()

# In-memory mock database state
MOCK_DATA = {
    "patients": {
        999: {
            "patient_id": 999,
            "first_name": "Test",
            "last_name": "Patient",
            "date_of_birth": datetime.date(1990, 1, 1),
            "gender": "M",
            "blood_type": "O+",
            "phone": "0771234567",
            "email": "test_patient@example.com",
            "address": "Test Address",
            "created_at": datetime.datetime.now(),
            "age": 36
        }
    },
    "doctors": {
        999: {
            "doctor_id": 999,
            "first_name": "Test",
            "last_name": "Doctor",
            "specialization": "General Medicine",
            "dept_id": 1,
            "phone": "0777654321",
            "email": "test_doctor@example.com",
            "hire_date": datetime.date(2020, 1, 1)
        }
    },
    "appointments": {
        999: {
            "appt_id": 999,
            "patient_id": 999,
            "doctor_id": 999,
            "appt_date": datetime.date(2026, 6, 15),
            "appt_time": "10:30",
            "status": "Scheduled",
            "notes": "Test appointment notes"
        }
    },
    "medical_records": {
        999: {
            "record_id": 999,
            "appt_id": 999,
            "patient_id": 999,
            "doctor_id": 999,
            "diagnosis": "Common Cold",
            "notes": "Rest and fluids",
            "record_date": datetime.datetime.now()
        }
    },
    "prescriptions": {
        999: {
            "prescription_id": 999,
            "record_id": 999,
            "doctor_id": 999,
            "status": "Active",
            "prescribed_date": datetime.datetime.now()
        }
    },
    "prescription_items": [
        {
            "item_id": 999,
            "prescription_id": 999,
            "medicine_id": 999,
            "dosage": "1 daily",
            "duration_days": 10,
            "quantity": 10
        }
    ],
    "medicines": {
        999: {
            "medicine_id": 999,
            "medicine_name": "Test Medicine",
            "generic_name": "Test Generic",
            "category": "Test Category",
            "unit": "Tablet",
            "reorder_level": 50,
            "unit_price": 10.0
        }
    },
    "transactions": {}
}

# Subclass int to support index lookup like doctor_id = int(out_id.getvalue()[0])
class IndexableInt(int):
    def __getitem__(self, index):
        return self

# Mock setup (only applied when NOT running integration tests)
if TEST_MODE != "integration":
    import database
    import oracledb
    
    # Mock lifespan database initialization
    async def mock_init_db():
        pass

    async def mock_close_db():
        pass

    database.init_db = mock_init_db
    database.close_db = mock_close_db

    # Mock variables for stored procedures returning OUT parameters
    class MockVar:
        def __init__(self, val=999):
            self.val = val
        def getvalue(self):
            return self.val

    class MockCursor:
        def __init__(self):
            self.arraysize = 100
            self.description = [("COL1",)]
        def execute(self, query, params=None):
            pass
        def fetchall(self):
            return []
        def var(self, type_val, *args, **kwargs):
            return MockVar(IndexableInt(999))
        def callproc(self, name, args=None):
            name = name.lower()
            if name == 'proc_create_patient':
                new_id = len(MOCK_DATA["patients"]) + 1001
                args[-1].val = IndexableInt(new_id)
                MOCK_DATA["patients"][new_id] = {
                    "patient_id": new_id,
                    "first_name": args[0],
                    "last_name": args[1],
                    "date_of_birth": args[2],
                    "gender": args[3],
                    "blood_type": args[4],
                    "phone": args[5],
                    "email": args[6],
                    "address": args[7],
                    "created_at": datetime.datetime.now(),
                    "age": 30
                }
            elif name == 'proc_create_doctor':
                new_id = len(MOCK_DATA["doctors"]) + 1001
                args[-1].val = IndexableInt(new_id)
                MOCK_DATA["doctors"][new_id] = {
                    "doctor_id": new_id,
                    "first_name": args[0],
                    "last_name": args[1],
                    "specialization": args[2],
                    "dept_id": args[3],
                    "phone": args[4],
                    "email": args[5],
                    "hire_date": args[6]
                }
            elif name == 'proc_create_appointment':
                new_id = len(MOCK_DATA["appointments"]) + 1001
                args[-1].val = IndexableInt(new_id)
                MOCK_DATA["appointments"][new_id] = {
                    "appt_id": new_id,
                    "patient_id": args[0],
                    "doctor_id": args[1],
                    "appt_date": args[2],
                    "appt_time": args[3],
                    "status": args[4],
                    "notes": args[5]
                }
            elif name == 'proc_update_appt_status':
                appt_id = args[0]
                if appt_id in MOCK_DATA["appointments"]:
                    MOCK_DATA["appointments"][appt_id]["status"] = args[1]
            elif name == 'proc_create_medical_record':
                new_id = len(MOCK_DATA["medical_records"]) + 1001
                args[-1].val = IndexableInt(new_id)
                MOCK_DATA["medical_records"][new_id] = {
                    "record_id": new_id,
                    "appt_id": args[0],
                    "patient_id": args[1],
                    "doctor_id": args[2],
                    "diagnosis": args[3],
                    "notes": args[4],
                    "record_date": datetime.datetime.now()
                }
            elif name == 'proc_create_presc_header':
                new_id = len(MOCK_DATA["prescriptions"]) + 1001
                args[-1].val = IndexableInt(new_id)
                MOCK_DATA["prescriptions"][new_id] = {
                    "prescription_id": new_id,
                    "record_id": args[0],
                    "doctor_id": args[1],
                    "status": args[2],
                    "prescribed_date": datetime.datetime.now()
                }
            elif name == 'proc_create_presc_item':
                new_id = len(MOCK_DATA["prescription_items"]) + 1001
                MOCK_DATA["prescription_items"].append({
                    "item_id": new_id,
                    "prescription_id": args[0],
                    "medicine_id": args[1],
                    "dosage": args[2],
                    "duration_days": args[3],
                    "quantity": args[4]
                })
            elif name == 'proc_create_medicine':
                new_id = len(MOCK_DATA["medicines"]) + 1001
                args[-1].val = IndexableInt(new_id)
                MOCK_DATA["medicines"][new_id] = {
                    "medicine_id": new_id,
                    "medicine_name": args[0],
                    "generic_name": args[1],
                    "category": args[2],
                    "unit": args[3],
                    "reorder_level": args[4],
                    "unit_price": args[5]
                }
            elif name == 'proc_create_stock_txn':
                new_id = len(MOCK_DATA["transactions"]) + 1001
                args[-1].val = IndexableInt(new_id)
                MOCK_DATA["transactions"][new_id] = {
                    "txn_id": new_id,
                    "medicine_id": args[0],
                    "txn_type": args[1],
                    "quantity": args[2],
                    "reference_id": args[3],
                    "performed_by": args[4],
                    "txn_date": datetime.datetime.now()
                }
            elif name == 'proc_process_prescription':
                presc_id = args[0]
                if presc_id in MOCK_DATA["prescriptions"]:
                    MOCK_DATA["prescriptions"][presc_id]["status"] = "Dispensed"
            return args
        def callfunc(self, name, return_type, args=None):
            return []
        def close(self):
            pass

    class MockConnection:
        def cursor(self):
            return MockCursor()
        def commit(self):
            pass
        def close(self):
            pass

    class MockPool:
        def get_connection(self):
            class MockConnectionCM:
                def __enter__(self):
                    return MockConnection()
                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass
            return MockConnectionCM()

        def execute_query(self, query, params=None):
            if "select 1" in query.lower():
                return [(1,)]
            return []

        def execute_update(self, query, params=None):
            return 1

        def get_pool_stats(self):
            return {
                'opened': 5,
                'in_use': 1,
                'available': 4,
                'max_connections': 20,
            }

    def mock_get_db_pool():
        return MockPool()

    database.get_db_pool = mock_get_db_pool
    database.OracleConnectionPool = MockPool

    # Mock fetch_data to return pre-defined mock datasets dynamically
    def mock_fetch_data(cursor, obj_name, args, is_func=False):
        name = obj_name.lower()

        # Patients
        if name == 'proc_get_all_patients':
            return list(MOCK_DATA["patients"].values())
        elif name == 'fn_get_patient_by_id':
            patient_id = args[0]
            if patient_id in MOCK_DATA["patients"]:
                return [MOCK_DATA["patients"][patient_id]]
            return []
        elif name == 'fn_get_patient_presc':
            patient_id = args[0]
            # Match prescriptions for the patient
            results = []
            for presc in MOCK_DATA["prescriptions"].values():
                rec = MOCK_DATA["medical_records"].get(presc["record_id"])
                if rec and rec["patient_id"] == patient_id:
                    # Find items
                    for item in MOCK_DATA["prescription_items"]:
                        if item["prescription_id"] == presc["prescription_id"]:
                            med = MOCK_DATA["medicines"].get(item["medicine_id"], {})
                            results.append({
                                "prescription_id": presc["prescription_id"],
                                "record_id": presc["record_id"],
                                "doctor_id": presc["doctor_id"],
                                "status": presc["status"],
                                "prescribed_date": presc["prescribed_date"],
                                "medicine_id": item["medicine_id"],
                                "medicine_name": med.get("medicine_name", "Test Medicine"),
                                "dosage": item["dosage"],
                                "duration_days": item["duration_days"],
                                "quantity": item["quantity"]
                            })
            return results

        # Doctors
        elif name == 'proc_get_all_doctors':
            return list(MOCK_DATA["doctors"].values())
        elif name == 'fn_get_doctor_by_id':
            doctor_id = args[0]
            if doctor_id in MOCK_DATA["doctors"]:
                return [MOCK_DATA["doctors"][doctor_id]]
            return []
        elif name == 'proc_get_departments':
            return [
                {
                    "dept_id": 1,
                    "dept_name": "Outpatient",
                    "location": "Floor 1",
                    "head_doctor_id": None
                }
            ]
        elif name == 'fn_get_doctor_summary':
            return [
                {
                    "total_appointments": 10,
                    "completed_appointments": 8,
                    "pending_appointments": 2,
                    "unique_patients": 5
                }
            ]

        # Appointments
        elif name == 'fn_get_appointment_by_id':
            appt_id = args[0]
            if appt_id in MOCK_DATA["appointments"]:
                return [MOCK_DATA["appointments"][appt_id]]
            return []
        elif name in ['fn_get_appts_by_patient', 'fn_get_appointments_by_patient']:
            patient_id = args[0]
            return [a for a in MOCK_DATA["appointments"].values() if a["patient_id"] == patient_id]
        elif name in ['fn_get_appts_by_doctor', 'fn_get_appointments_by_doctor']:
            doctor_id = args[0]
            return [a for a in MOCK_DATA["appointments"].values() if a["doctor_id"] == doctor_id]

        # Prescriptions & Records
        elif name == 'fn_get_medical_record':
            rec_id = args[0]
            if rec_id in MOCK_DATA["medical_records"]:
                return [MOCK_DATA["medical_records"][rec_id]]
            return []
        elif name == 'fn_get_prescription':
            presc_id = args[0]
            if presc_id in MOCK_DATA["prescriptions"]:
                return [MOCK_DATA["prescriptions"][presc_id]]
            return []
        elif name == 'fn_get_prescription_full':
            presc_id = args[0]
            if presc_id not in MOCK_DATA["prescriptions"]:
                return []
            presc = MOCK_DATA["prescriptions"][presc_id]
            rec = MOCK_DATA["medical_records"].get(presc["record_id"])
            if not rec:
                return []
            pat = MOCK_DATA["patients"].get(rec["patient_id"], {})
            doc = MOCK_DATA["doctors"].get(presc["doctor_id"], {})
            
            p_items = [it for it in MOCK_DATA["prescription_items"] if it["prescription_id"] == presc_id]
            if not p_items:
                return [{
                    "prescription_id": presc_id,
                    "record_id": presc["record_id"],
                    "doctor_id": presc["doctor_id"],
                    "status": presc["status"],
                    "prescribed_date": presc["prescribed_date"],
                    "appt_id": rec["appt_id"],
                    "patient_id": rec["patient_id"],
                    "patient_fname": pat.get("first_name", "Test"),
                    "patient_lname": pat.get("last_name", "Patient"),
                    "doctor_fname": doc.get("first_name", "Test"),
                    "doctor_lname": doc.get("last_name", "Doctor"),
                    "medicine_id": 999,
                    "dosage": "1 daily",
                    "duration_days": 10,
                    "quantity": 10,
                    "item_id": 999
                }]
            rows = []
            for item in p_items:
                rows.append({
                    "prescription_id": presc_id,
                    "record_id": presc["record_id"],
                    "doctor_id": presc["doctor_id"],
                    "status": presc["status"],
                    "prescribed_date": presc["prescribed_date"],
                    "appt_id": rec["appt_id"],
                    "patient_id": rec["patient_id"],
                    "patient_fname": pat.get("first_name", "Test"),
                    "patient_lname": pat.get("last_name", "Patient"),
                    "doctor_fname": doc.get("first_name", "Test"),
                    "doctor_lname": doc.get("last_name", "Doctor"),
                    "medicine_id": item["medicine_id"],
                    "dosage": item["dosage"],
                    "duration_days": item["duration_days"],
                    "quantity": item["quantity"],
                    "item_id": item["item_id"]
                })
            return rows
        elif name in ['proc_get_pending_presc', 'proc_get_pending_prescriptions']:
            results = []
            for presc in MOCK_DATA["prescriptions"].values():
                if presc["status"] == "Active":
                    rec = MOCK_DATA["medical_records"].get(presc["record_id"], {})
                    pat = MOCK_DATA["patients"].get(rec.get("patient_id"), {})
                    doc = MOCK_DATA["doctors"].get(presc["doctor_id"], {})
                    results.append({
                        "prescription_id": presc["prescription_id"],
                        "patient_fname": pat.get("first_name", "Test"),
                        "patient_lname": pat.get("last_name", "Patient"),
                        "doctor_fname": doc.get("first_name", "Test"),
                        "doctor_lname": doc.get("last_name", "Doctor"),
                        "prescribed_date": presc["prescribed_date"]
                    })
            return results

        # Inventory
        elif name == 'proc_get_all_medicines':
            return list(MOCK_DATA["medicines"].values())
        elif name == 'proc_get_low_stock':
            # return medicines with low quantity
            return [
                {
                    "medicine_id": m["medicine_id"],
                    "medicine_name": m["medicine_name"],
                    "quantity_available": 10,
                    "reorder_level": m["reorder_level"]
                }
                for m in MOCK_DATA["medicines"].values() if m["medicine_id"] == 999
            ]
        elif name == 'fn_get_medicine_by_id':
            med_id = args[0]
            if med_id in MOCK_DATA["medicines"]:
                return [MOCK_DATA["medicines"][med_id]]
            return []
        elif name == 'proc_get_stock_txn':
            txn_id = args[0]
            if txn_id in MOCK_DATA["transactions"]:
                return [MOCK_DATA["transactions"][txn_id]]
            return []

        # Analytics
        elif name == 'proc_get_apriori_data':
            return [
                {"prescription_id": 1, "medicine_name": "Test Medicine A"},
                {"prescription_id": 1, "medicine_name": "Test Medicine B"},
                {"prescription_id": 2, "medicine_name": "Test Medicine A"},
            ]
        elif name == 'proc_get_monthly_trend':
            return [
                {
                    "medicine_name": "Test Medicine",
                    "yr": 2026,
                    "mo": 6,
                    "total_consumed": 100
                }
            ]

        return []

    database.fetch_data = mock_fetch_data


# Session client fixture
@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as c:
        yield c


# Clean up database after each integration test
@pytest.fixture(autouse=True)
def db_cleanup():
    yield
    if TEST_MODE == "integration":
        from database import get_db_pool
        pool = get_db_pool()
        try:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete items for test prescriptions
                cursor.execute("""
                    DELETE FROM prescription_item 
                    WHERE prescription_id IN (
                        SELECT prescription_id FROM prescription p
                        JOIN medical_record r ON p.record_id = r.record_id
                        JOIN patient pat ON r.patient_id = pat.patient_id
                        WHERE pat.email LIKE 'test_%' OR pat.email LIKE 'integration_%'
                    )
                """)
                
                # Delete stock transactions created by tests, or referencing test medicines/prescriptions
                cursor.execute("""
                    DELETE FROM stock_transaction 
                    WHERE performed_by LIKE 'test_%' 
                       OR performed_by LIKE 'integration_%'
                       OR performed_by = 'string'
                       OR performed_by = 'debug_runner'
                       OR performed_by = 'test_user'
                       OR medicine_id IN (
                           SELECT medicine_id FROM medicine 
                           WHERE medicine_name LIKE 'test_%' OR medicine_name LIKE 'integration_%'
                       )
                       OR reference_id IN (
                           SELECT prescription_id FROM prescription p
                           JOIN medical_record r ON p.record_id = r.record_id
                           JOIN patient pat ON r.patient_id = pat.patient_id
                           WHERE pat.email LIKE 'test_%' OR pat.email LIKE 'integration_%'
                       )
                """)
                
                # Delete prescriptions for test records
                cursor.execute("""
                    DELETE FROM prescription 
                    WHERE record_id IN (
                        SELECT record_id FROM medical_record r
                        JOIN patient pat ON r.patient_id = pat.patient_id
                        WHERE pat.email LIKE 'test_%' OR pat.email LIKE 'integration_%'
                    )
                """)
                
                # Delete medical records for test appointments
                cursor.execute("""
                    DELETE FROM medical_record 
                    WHERE patient_id IN (
                        SELECT patient_id FROM patient
                        WHERE email LIKE 'test_%' OR email LIKE 'integration_%'
                    )
                """)
                
                # Delete appointments for test patients/doctors
                cursor.execute("""
                    DELETE FROM appointment 
                    WHERE patient_id IN (
                        SELECT patient_id FROM patient
                        WHERE email LIKE 'test_%' OR email LIKE 'integration_%'
                    )
                """)
                
                # Delete test patients
                cursor.execute("DELETE FROM patient WHERE email LIKE 'test_%' OR email LIKE 'integration_%'")
                
                # Delete test doctors
                cursor.execute("DELETE FROM doctor WHERE email LIKE 'test_%' OR email LIKE 'integration_%'")
                
                # Delete test stock entries
                cursor.execute("""
                    DELETE FROM stock 
                    WHERE medicine_id IN (
                        SELECT medicine_id FROM medicine 
                        WHERE medicine_name LIKE 'test_%' OR medicine_name LIKE 'integration_%'
                    )
                """)

                # Delete test medicines
                cursor.execute("DELETE FROM medicine WHERE medicine_name LIKE 'test_%' OR medicine_name LIKE 'integration_%'")
                
                conn.commit()
        except Exception as e:
            print(f"Error during integration test DB cleanup: {e}")
