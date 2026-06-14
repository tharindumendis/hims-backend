import pytest

def test_inventory_stock(client):
    response = client.get("/inventory/stock")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    item = data[0]
    assert "stock_id" in item
    assert "medicine_id" in item
    assert "medicine_name" in item
    assert "quantity_available" in item
    assert "stock_status" in item
    assert item["stock_status"] == "ADEQUATE"

def test_inventory_expiring(client):
    response = client.get("/inventory/expiring")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    item = data[0]
    assert "medicine_id" in item
    assert "medicine_name" in item
    assert "batch_number" in item
    assert "days_until_expiry" in item
    assert item["batch_number"] == "N/A"

def test_analytics_trends(client):
    response = client.get("/analytics/trends")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    item = data[0]
    assert "medicine_id" in item
    assert "medicine_name" in item
    assert "txn_year" in item
    assert "total_out_quantity" in item

def test_analytics_suppliers(client):
    response = client.get("/analytics/suppliers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    item = data[0]
    assert "supplier_id" in item
    assert "supplier_name" in item
    assert "on_time_delivery_rate" in item
    assert "total_order_value" in item
    assert item["supplier_name"] == "Test Supplier"

def test_analytics_monthly_trend_compatibility(client):
    response = client.get("/analytics/monthly-trend")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    item = data[0]
    assert "medicine_name" in item
    assert "year" in item
    assert "month" in item
    assert "total_consumed" in item
    assert item["medicine_name"] == "Test Medicine"
