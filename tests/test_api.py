"""Tests for PlatformSLOBoard FastAPI endpoints."""

from fastapi.testclient import TestClient
from sloboard.api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


def test_list_slos_endpoint() -> None:
    response = client.get("/slos")
    assert response.status_code == 200
    data = response.json()
    assert "slos" in data
    assert "summary" in data
    assert data["count"] > 0


def test_list_services_endpoint() -> None:
    response = client.get("/services")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert data["count"] > 0


def test_get_slo_not_found() -> None:
    response = client.get("/slos/nonexistent-slo")
    assert response.status_code == 404


def test_get_error_budgets() -> None:
    response = client.get("/budget")
    assert response.status_code == 200
    data = response.json()
    assert "budgets" in data
    assert len(data["budgets"]) > 0


def test_get_summary() -> None:
    response = client.get("/summary")
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "total_slos" in data
    assert 0 <= data["overall_score"] <= 100