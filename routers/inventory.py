from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import MedicineCreate, MedicineOut, StockTransactionBase, StockTransactionOut
from services import inventory_service

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/medicines", response_model=List[MedicineOut])
def get_all_medicines():
    return inventory_service.get_all_medicines()

@router.post("/medicines", response_model=MedicineOut)
def create_medicine(medicine: MedicineCreate):
    return inventory_service.create_medicine(medicine)

@router.get("/low-stock")
def get_low_stock_medicines():
    return inventory_service.get_low_stock_medicines()

@router.post("/transactions", response_model=StockTransactionOut)
def create_stock_transaction(txn: StockTransactionBase):
    return inventory_service.create_stock_transaction(txn)
