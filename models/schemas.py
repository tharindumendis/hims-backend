from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

# ----------------- PATIENT -----------------
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str = Field(..., pattern="^[MFO]$")
    blood_type: Optional[str] = None
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientOut(PatientBase):
    patient_id: int
    created_at: datetime
    age: Optional[int] = None

# ----------------- DEPARTMENT -----------------
class DepartmentBase(BaseModel):
    dept_name: str
    location: Optional[str] = None
    head_doctor_id: Optional[int] = None

class DepartmentOut(DepartmentBase):
    dept_id: int

# ----------------- DOCTOR -----------------
class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    specialization: str
    dept_id: int
    phone: str
    email: Optional[EmailStr] = None
    hire_date: date

class DoctorCreate(DoctorBase):
    pass

class DoctorOut(DoctorBase):
    doctor_id: int
    
# ----------------- APPOINTMENT -----------------
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appt_date: date
    appt_time: str
    status: str = Field(..., pattern="^(Scheduled|Completed|Cancelled)$")
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentOut(AppointmentBase):
    appt_id: int

# ----------------- MEDICAL RECORD -----------------
class MedicalRecordBase(BaseModel):
    appt_id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    notes: Optional[str] = None

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordOut(MedicalRecordBase):
    record_id: int
    record_date: datetime

# ----------------- MEDICINE -----------------
class MedicineBase(BaseModel):
    medicine_name: str
    generic_name: Optional[str] = None
    category: str
    unit: str
    reorder_level: int = 50
    unit_price: float

class MedicineCreate(MedicineBase):
    pass

class MedicineOut(MedicineBase):
    medicine_id: int

# ----------------- PRESCRIPTION & ITEM -----------------
class PrescriptionItemBase(BaseModel):
    medicine_id: int
    dosage: str
    duration_days: int
    quantity: int

class PrescriptionItemOut(PrescriptionItemBase):
    item_id: int
    prescription_id: int

class PrescriptionBase(BaseModel):
    record_id: int
    doctor_id: int
    status: str = Field(..., pattern="^(Active|Dispensed|Cancelled)$")

class PrescriptionCreate(PrescriptionBase):
    items: List[PrescriptionItemBase]

class PrescriptionOut(PrescriptionBase):
    prescription_id: int
    prescribed_date: datetime

# ----------------- STOCK & TRANSACTION -----------------
class StockOut(BaseModel):
    stock_id: int
    medicine_id: int
    quantity_available: int
    expiry_date: Optional[date] = None
    storage_location: Optional[str] = None
    last_updated: datetime

class StockTransactionBase(BaseModel):
    medicine_id: int
    txn_type: str = Field(..., pattern="^(IN|OUT)$")
    quantity: int
    reference_id: Optional[int] = None
    performed_by: Optional[str] = None

class StockTransactionOut(StockTransactionBase):
    txn_id: int
    txn_date: datetime

# ----------------- SUPPLIER & PO -----------------
class SupplierBase(BaseModel):
    supplier_name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    status: str = Field(default="Active", pattern="^(Active|Inactive)$")

class SupplierOut(SupplierBase):
    supplier_id: int

class POItemBase(BaseModel):
    medicine_id: int
    quantity_ordered: int
    unit_price: float

class POItemOut(POItemBase):
    po_item_id: int
    po_id: int
    quantity_received: int = 0

class PurchaseOrderBase(BaseModel):
    supplier_id: int
    expected_date: Optional[date] = None
    status: str = Field(..., pattern="^(Draft|Approved|Received|Cancelled)$")

class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[POItemBase]

class PurchaseOrderOut(PurchaseOrderBase):
    po_id: int
    order_date: datetime
    total_amount: float
