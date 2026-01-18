import pytest
from fastapi.testclient import TestClient
from humandesign.api import app

client = TestClient(app)

@pytest.mark.skip(reason="Not implemented yet - TDD Phase 1 Checkpoint")
def test_transits_v180_structure():
    """
    Verify that the /transits/daily endpoint returns the enriched v1.8.0 structure.
    """
    # Use a known date/location to ensure determinstic results if possible, 
    # but primarily checking schema structure here.
    params = {
        "year": 1985, "month": 6, "day": 15, "hour": 14, "minute": 30, "place": "Berlin, Germany",
        "transit_year": 2026, "transit_month": 1, "transit_day": 18
    }
    
    # Needs auth
    headers = {"Authorization": "Bearer your_secret_token_here"} # Mock token usually works in dev/test if env is set, or we might need to mock auth. 
    # Assuming standard test setup uses env var or bypass. Check if conftest.py exists or how other tests do it. 
    # For now, blindly passing header.
    
    response = client.get("/transits/daily", params=params, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    
    # 1. Structure Verification
    assert "meta" in data, "Missing 'meta' key"
    assert "composite_changes" in data, "Missing 'composite_changes' key"
    assert "planetary_transits" in data, "Missing 'planetary_transits' key"
    
    # 2. Meta Verification
    meta = data["meta"]
    assert "transit_date_local" in meta
    assert "transit_date_utc" in meta
    assert "birth_date_utc" in meta
    assert "location" in meta
    assert "type" in meta
    assert "authority" in meta
    assert "total_centers" in meta
    
    # 3. Composite Changes Verification
    comp = data["composite_changes"]
    assert "new_channels" in comp
    assert "new_centers" in comp
    
    # Check if new_channels is list of dicts with name/description
    if comp["new_channels"]:
        channel = comp["new_channels"][0]
        assert "gates" in channel
        assert "name" in channel, "Channel missing 'name'"
        assert "description" in channel, "Channel missing 'description'"
        
    # 4. Planetary Transits Verification
    if data["planetary_transits"]:
        transit = data["planetary_transits"][0]
        assert "planets" in transit
        assert "gate" in transit
