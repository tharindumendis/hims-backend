from fastapi import APIRouter, Depends, HTTPException
from typing import List
from dependencies.auth_dependency import RoleChecker
from models.schemas import MedicineCreate, MedicineOut, StockTransactionBase, StockTransactionOut, StockDetailsOut, ExpiringStockOut
from services import inventory_service

router = APIRouter(prefix="/inventory", tags=["Inventory"], dependencies=[Depends(RoleChecker(["PHARMACIST", "ADMIN"]))])

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

@router.get("/stock", response_model=List[StockDetailsOut])
def get_stock():
    return inventory_service.get_stock()

@router.get("/expiring", response_model=List[ExpiringStockOut])
def get_expiring_stock():
    return inventory_service.get_expiring_stock()
