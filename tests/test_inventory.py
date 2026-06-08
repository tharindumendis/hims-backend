import pytest

def test_inventory_medicines_flow(client):
    # 1. Create a Medicine
    payload = {
        "medicine_name": "test_inv_medicine",
        "generic_name": "test_inv_generic",
        "category": "Painkiller",
        "unit": "Tablet",
        "reorder_level": 50,
        "unit_price": 5.5
    }
    create_resp = client.post("/inventory/medicines", json=payload)
    assert create_resp.status_code == 200
    med_data = create_resp.json()
    assert "medicine_id" in med_data
    assert med_data["medicine_name"] == "test_inv_medicine"
    medicine_id = med_data["medicine_id"]

    # 2. Get All Medicines
    get_all_resp = client.get("/inventory/medicines")
    assert get_all_resp.status_code == 200
    meds_list = get_all_resp.json()
    assert isinstance(meds_list, list)
    assert any(m["medicine_id"] == medicine_id for m in meds_list)

    # 3. Get Low Stock
    low_stock_resp = client.get("/inventory/low-stock")
    assert low_stock_resp.status_code == 200
    assert isinstance(low_stock_resp.json(), list)

    # 4. Create Stock Transaction (IN)
    txn_payload = {
        "medicine_id": medicine_id,
        "txn_type": "INN",
        "quantity": 100,
        "reference_id": None,
        "performed_by": "test_runner"
    }
    txn_resp = client.post("/inventory/transactions", json=txn_payload)
    assert txn_resp.status_code == 200
    txn_data = txn_resp.json()
    assert "txn_id" in txn_data
    assert txn_data["txn_type"] == "INN"
    assert txn_data["quantity"] == 100
