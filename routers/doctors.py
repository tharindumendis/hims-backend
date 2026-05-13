from fastapi import APIRouter

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("/")
def get_all_doctors():
    return []
