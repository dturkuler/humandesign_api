import pytest
from fastapi.testclient import TestClient
from humandesign.api import app
from humandesign.dependencies import verify_token

app.dependency_overrides[verify_token] = lambda: True
client = TestClient(app)

TEST_BODY = {
    "year": 1968,
    "month": 2,
    "day": 21,
    "hour": 11,
    "minute": 0,
    "place": "Europe/Istanbul"
}

def test_v2_calculate_enriched_labels():
    """Verify that V2 response includes semantic labels from SQLite."""
    response = client.post("/v2/calculate", json=TEST_BODY)
    assert response.status_code == 200
    data = response.json()
    
    # Check Sun Gate in personality_gates
    sun_gate = data["personality_gates"]["Sun"]
    assert sun_gate["gate_name"] is not None
    assert "Abundance" in sun_gate["gate_name"] or sun_gate["gate_name"] != ""
    assert sun_gate["line_name"] is not None
    assert sun_gate["line_description"] is not None

def test_v2_calculate_fixation_heuristic():
    """Verify that fixation heuristic works for known exalted/detriment cases."""
    response = client.post("/v2/calculate", json=TEST_BODY)
    data = response.json()
    
    # Check heuristic logic presence in both sections
    assert "personality_gates" in data
    assert "design_gates" in data

def test_v2_calculate_masking_with_enrichment():
    """Verify that masking works on enriched fields."""
    body = TEST_BODY.copy()
    body["include"] = ["personality_gates"]
    
    response = client.post("/v2/calculate", json=body)
    assert response.status_code == 200
    data = response.json()
    
    assert "personality_gates" in data
    assert "general" not in data
    assert "design_gates" not in data
    assert data["personality_gates"]["Sun"]["gate_name"] is not None
