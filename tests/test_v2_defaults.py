from fastapi.testclient import TestClient
from humandesign.api import app
from humandesign.dependencies import verify_token

app.dependency_overrides[verify_token] = lambda: True
client = TestClient(app)

def test_v2_calculate_empty_body_defaults():
    """Verify V2 works with an empty body using defaults."""
    response = client.post("/v2/calculate", json={})
    assert response.status_code == 200
    data = response.json()
    
    # Check if a known value for the default date is present
    # 1968-02-21 11:00 has Personality Sun in Gate 55
    assert data["personality_gates"]["Sun"]["gate"] == 55
    # 1968-02-21 11:00 has Design Sun in Gate 34
    assert data["design_gates"]["Sun"]["gate"] == 34
    assert data["general"]["birth_place"] == "Kirikkale, Turkey"
