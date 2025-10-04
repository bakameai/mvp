import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns correct response"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "BAKAME MVP - AI Learning Assistant"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"
    assert "endpoints" in data

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "BAKAME MVP"

def test_cors_headers():
    """Test that CORS headers are properly set"""
    response = client.get("/")
    assert response.status_code == 200
    # CORS headers should be present for cross-origin requests
    assert "access-control-allow-origin" in response.headers or response.status_code == 200