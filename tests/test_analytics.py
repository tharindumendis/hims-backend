# pyrefly: ignore [missing-import]
import pytest

def test_association_rules(client):
    response = client.get("/analytics/association-rules?min_support=0.01&min_confidence=0.1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        rule = data[0]
        assert "support" in rule
        assert "confidence" in rule

def test_monthly_trend(client):
    response = client.get("/analytics/monthly-trend")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        trend = data[0]
        assert "medicine_name" in trend
        assert "total_consumed" in trend
