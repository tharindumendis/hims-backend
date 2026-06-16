from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

# ----------------- USER (for authentication) -----------------
class UserBase(BaseModel):
    username: str
    role: str = Field(..., pattern="^(RECEPTIONIST|DOCTOR|PHARMACIST|ADMIN)$")
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    user_id: int
    created_at: datetime

class UserInDB(UserBase):
    user_id: int
    hashed_password: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


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
    
class PrescriptionFullOut(PrescriptionBase):
    prescription_id: int
    prescribed_date: datetime
    patient_fname: str
    patient_lname: str
    doctor_fname: str
    doctor_lname: str
    items: List[PrescriptionItemOut]
    appt_id: int
    patient_id: int

## Oracle DB Return Type 
class PrescriptionRow(BaseModel):
    prescription_id: int
    record_id: int
    doctor_id: int
    status: str
    prescribed_date: datetime
    appt_id: int
    patient_id: int
    patient_fname: str
    patient_lname: str
    doctor_fname: str
    doctor_lname: str
    medicine_id: int
    dosage: str
    duration_days: int
    quantity: int
    item_id: int | None = None  # if available

# Output model: grouped prescription
class PrescriptionFullOut(BaseModel):
    prescription_id: int
    record_id: int
    doctor_id: int
    status: str
    prescribed_date: datetime
    appt_id: int
    patient_id: int
    patient_fname: str
    patient_lname: str
    doctor_fname: str
    doctor_lname: str
    items: List[PrescriptionItemOut]

    @classmethod
    def from_rows(cls, rows: List[PrescriptionRow]):
        if not rows:
            raise ValueError("No rows found")

        header = rows[0]
        items = [
            PrescriptionItemOut(
                item_id=row.item_id or 0,
                prescription_id=row.prescription_id,
                medicine_id=row.medicine_id,
                dosage=row.dosage,
                duration_days=row.duration_days,
                quantity=row.quantity
            )
            for row in rows
        ]

        return cls(
            prescription_id=header.prescription_id,
            record_id=header.record_id,
            doctor_id=header.doctor_id,
            status=header.status,
            prescribed_date=header.prescribed_date,
            appt_id=header.appt_id,
            patient_id=header.patient_id,
            patient_fname=header.patient_fname,
            patient_lname=header.patient_lname,
            doctor_fname=header.doctor_fname,
            doctor_lname=header.doctor_lname,
            items=items
        )

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
    txn_type: str = Field(..., pattern="^(INN|OUT)$")
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
