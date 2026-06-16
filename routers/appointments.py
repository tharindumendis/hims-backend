from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List

from models.schemas import AppointmentCreate, AppointmentOut
from dependencies.auth_dependency import RoleChecker
from services import appointment_service
import oracledb

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/", response_model=AppointmentOut, dependencies=[Depends(RoleChecker(["RECEPTIONIST", "ADMIN"]))])
def create_appointment(appt: AppointmentCreate):
    try:
        appt_id = appointment_service.create_appointment(appt)
        return appointment_service.get_appointment_by_id(appt_id)
    except oracledb.DatabaseError as e:
        error, = e.args
        raise HTTPException(status_code=400, detail=error.message)

@router.get("/patient/{patient_id}", response_model=List[AppointmentOut], dependencies=[Depends(RoleChecker(["RECEPTIONIST", "DOCTOR", "ADMIN"]))])
def get_appointments_by_patient(patient_id: int):
    return appointment_service.get_appointments_by_patient(patient_id)

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentOut])
def get_appointments_by_doctor(doctor_id: int):
    return appointment_service.get_appointments_by_doctor(doctor_id)

@router.put("/{appt_id}/status", response_model=AppointmentOut)
def update_appointment_status(appt_id: int, status: str = Body(..., embed=True)):
    if status not in ["Scheduled", "Completed", "Cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    try:
        appointment_service.update_appointment_status(appt_id, status)
        updated_appt = appointment_service.get_appointment_by_id(appt_id)
        if not updated_appt:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return updated_appt
    except oracledb.DatabaseError as e:
        error, = e.args
        raise HTTPException(status_code=400, detail=error.message)
