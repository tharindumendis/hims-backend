from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.schemas import PatientCreate, PatientOut
from services import patient_service
from dependencies.auth_dependency import RoleChecker

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/", response_model=List[PatientOut], dependencies=[Depends(RoleChecker(["RECEPTIONIST", "DOCTOR", "ADMIN", "PHARMACIST"]))])
def get_all_patients():
    return patient_service.get_all_patients()

@router.get("/{patient_id}", response_model=PatientOut, dependencies=[Depends(RoleChecker(["RECEPTIONIST", "DOCTOR", "ADMIN", "PHARMACIST"]))])
def get_patient(patient_id: int):
    patient = patient_service.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.post("/", response_model=PatientOut, dependencies=[Depends(RoleChecker(["RECEPTIONIST", "ADMIN"]))])
def create_patient(patient: PatientCreate):
    return patient_service.create_patient(patient)

@router.get("/{patient_id}/prescriptions", dependencies=[Depends(RoleChecker(["RECEPTIONIST", "DOCTOR", "ADMIN", "PHARMACIST"]))])
def get_patient_prescriptions(patient_id: int):
    return patient_service.get_patient_prescriptions(patient_id)
