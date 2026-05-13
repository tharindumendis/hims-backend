from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import PatientCreate, PatientOut
from services import patient_service

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/", response_model=List[PatientOut])
def get_all_patients():
    return patient_service.get_all_patients()

@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int):
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.post("/", response_model=PatientOut)
def create_patient(patient: PatientCreate):
    return patient_service.create_patient(patient)

@router.get("/{patient_id}/prescriptions")
def get_patient_prescriptions(patient_id: int):
    return patient_service.get_patient_prescriptions(patient_id)
