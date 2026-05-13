from fastapi import APIRouter

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])

@router.get("/")
def get_all_prescriptions():
    return []
