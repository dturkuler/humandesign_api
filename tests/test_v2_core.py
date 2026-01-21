import pytest
from fastapi.testclient import TestClient
from humandesign.api import app
from humandesign.dependencies import verify_token
from humandesign.services.masking import OutputMaskingService

# Bypass token verification
app.dependency_overrides[verify_token] = lambda: True
client = TestClient(app)

TEST_BODY = {
    "year": 1968,
    "month": 2,
    "day": 21,
    "hour": 11,
    "minute": 0,
    "place": "Europe/Istanbul",
    "gender": "male"
}

def test_masking_service_basic():
    """Verify library logic for masking dictionaries."""
    data = {"a": 1, "b": 2, "c": 3}
    
    # Include only
    assert OutputMaskingService.apply_mask(data, include=["a"]) == {"a": 1}
    # Exclude only
    assert OutputMaskingService.apply_mask(data, exclude=["b"]) == {"a": 1, "c": 3}
    # Both (Include wins, then exclude applies)
    assert OutputMaskingService.apply_mask(data, include=["a", "b"], exclude=["b"]) == {"a": 1}

def test_v2_calculate_verbose_default():
    """Verify V2 returns all sections by default."""
    response = client.post("/v2/calculate", json=TEST_BODY)
    assert response.status_code == 200
    data = response.json()
    assert "general" in data
    assert "gates" in data
    assert "channels" in data
    # mechanics and advanced are excluded because they are None
    assert "mechanics" not in data
    assert "advanced" not in data

def test_v2_calculate_include_masking():
    """Verify V2 respects the 'include' filter."""
    body = TEST_BODY.copy()
    body["include"] = ["general"]
    
    response = client.post("/v2/calculate", json=body)
    assert response.status_code == 200
    data = response.json()
    assert "general" in data
    assert "gates" not in data
    assert "channels" not in data

def test_v2_calculate_exclude_masking():
    """Verify V2 respects the 'exclude' filter."""
    body = TEST_BODY.copy()
    body["exclude"] = ["gates", "channels", "mechanics", "advanced"]
    
    response = client.post("/v2/calculate", json=body)
    assert response.status_code == 200
    data = response.json()
    assert "general" in data
    assert "gates" not in data
    assert "channels" not in data

def test_v2_calculate_invalid_json():
    """Verify V2 handles bad input."""
    response = client.post("/v2/calculate", json={"year": "invalid"})
    assert response.status_code == 422 # Pydantic validation error
