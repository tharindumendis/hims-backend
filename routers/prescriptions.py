from models.schemas import PrescriptionFullOut
from fastapi import APIRouter, HTTPException
from typing import List, Any
from models.schemas import MedicalRecordCreate, MedicalRecordOut, PrescriptionCreate, PrescriptionOut
from services import prescription_service
import oracledb

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions & Records"])

@router.post("/record", response_model=MedicalRecordOut)
def create_medical_record(record: MedicalRecordCreate):
    try:
        record_id = prescription_service.create_medical_record(record)
        return prescription_service.get_medical_record_by_id(record_id)
    except oracledb.DatabaseError as e:
        error, = e.args
        raise HTTPException(status_code=400, detail=error.message)

@router.get("/record/{record_id}", response_model=MedicalRecordOut)
def get_medical_record_by_id(record_id: int):
    record = prescription_service.get_medical_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record

@router.post("/", response_model=PrescriptionOut)
def create_prescription(presc: PrescriptionCreate):
    try:
        presc_id = prescription_service.create_prescription(presc.model_dump())
        return prescription_service.get_prescription_by_id(presc_id)
    except oracledb.DatabaseError as e:
        error, = e.args
        raise HTTPException(status_code=400, detail=error.message)

@router.get("/pending", response_model=List[Any])
def get_pending_prescriptions():
    # Returns rows from vw_pending_prescriptions view
    return prescription_service.get_pending_prescriptions()

@router.get("/{presc_id}/full", response_model=PrescriptionFullOut)
def get_prescription_full_by_id(presc_id: int):
    prescription = prescription_service.get_prescription_full_by_id(presc_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@router.post("/{presc_id}/dispense")
def dispense_prescription(presc_id: int):
    try:
        prescription_service.dispense_prescription(presc_id)
        return {"status": "success", "message": f"Prescription {presc_id} dispensed successfully."}
    except oracledb.DatabaseError as e:
        error, = e.args
        raise HTTPException(status_code=400, detail=error.message)
