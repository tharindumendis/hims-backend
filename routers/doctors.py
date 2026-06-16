from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.schemas import DoctorCreate, DoctorOut, DepartmentOut
from services import doctor_service
from dependencies.auth_dependency import RoleChecker
import oracledb

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("/", response_model=List[DoctorOut], dependencies=[Depends(RoleChecker(["RECEPTIONIST", "DOCTOR", "ADMIN", "PHARMACIST"]))])
def get_all_doctors():
    return doctor_service.get_all_doctors()

@router.get("/departments", response_model=List[DepartmentOut], dependencies=[Depends(RoleChecker(["RECEPTIONIST", "DOCTOR", "ADMIN", "PHARMACIST"]))])
def get_departments():
    return doctor_service.get_departments()

@router.get("/{doctor_id}", response_model=DoctorOut, dependencies=[Depends(RoleChecker(["RECEPTIONIST", "DOCTOR", "ADMIN", "PHARMACIST"]))])
def get_doctor_by_id(doctor_id: int):
    doctor = doctor_service.get_doctor_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.post("/", response_model=DoctorOut, dependencies=[Depends(RoleChecker(["ADMIN"]))])
def create_doctor(doctor: DoctorCreate):
    try:
        doctor_id = doctor_service.create_doctor(doctor.model_dump())
        return doctor_service.get_doctor_by_id(doctor_id)
    except oracledb.DatabaseError as e:
        error, = e.args
        raise HTTPException(status_code=400, detail=error.message)

@router.get("/{doctor_id}/summary", dependencies=[Depends(RoleChecker(["RECEPTIONIST", "DOCTOR", "ADMIN", "PHARMACIST"]))])
def get_doctor_summary(doctor_id: int):
    return doctor_service.get_doctor_summary(doctor_id)
