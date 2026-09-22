import sys
import os
from fastapi.testclient import TestClient

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import app

client = TestClient(app)

def run_tests():
    print("============================================================")
    print(" ORCA Backend - Day 2, 3, 4 Verification")
    print("============================================================")
    results = []

    # Test 1: GET /api/marine/forecast
    response = client.get("/api/marine/forecast?lat=19.13&lon=72.81&date=2026-09-17")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("GET /api/marine/forecast", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 2: GET /api/weather/forecast
    response = client.get("/api/weather/forecast?lat=19.13&lon=72.81&date=2026-09-17")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("GET /api/weather/forecast", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 3: GET /api/pfz/nearby
    response = client.get("/api/pfz/nearby?lat=19.13&lon=72.81")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("GET /api/pfz/nearby", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 4: GET /api/alerts/nearby
    response = client.get("/api/alerts/nearby?lat=19.13&lon=72.81&radius_km=50")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("GET /api/alerts/nearby", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 5: GET /api/geospatial/zones
    response = client.get("/api/geospatial/zones?bbox=72.0,19.0,73.0,20.0")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("GET /api/geospatial/zones", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 6: POST /api/chat (Bhashini Fallback Test)
    response = client.post("/api/chat", data={"text": "test query"})
    status = "PASSED" if response.status_code == 200 else "FAILED"
    payload = response.json() if response.status_code == 200 else response.text
    if status == "PASSED":
        try:
            intent = payload.get("received_intent", {})
            assert intent.get("language_detected") == "mr-IN"
            assert intent.get("intent") == "fishing_safety"
        except AssertionError:
            status = "FAILED"
            payload = "Assertion Error: Fallback JSON structure invalid."
    results.append(("POST /api/chat (Bhashini)", status, response.status_code, payload))

    # Test 6.5: Evidence Engine Component Test
    from agents.evidence_engine import EvidenceEngine
    engine = EvidenceEngine()
    engine_status = "PASSED"
    try:
        rec = engine.synthesize_recommendation({
            "metrics": {"sst_trend": "+1C", "chlorophyll_trend": "-0.5"}, 
            "source": "test_src", 
            "confidence": 0.99
        })
        assert "metadata" in rec
        assert "timestamp" in rec["metadata"]
        assert rec["metadata"]["confidence"] == 0.99
        assert "possible contributing factors" in rec["recommendation"]
    except Exception as e:
        engine_status = "FAILED"
        rec = str(e)
    results.append(("Evidence Engine (Component)", engine_status, "N/A", rec))

    # Test 7: GET /api/data-sources/catalog
    response = client.get("/api/data-sources/catalog")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("GET /api/data-sources/catalog", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 8: GET /api/data-sources/status
    response = client.get("/api/data-sources/status")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("GET /api/data-sources/status", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 9: POST /api/trends/fishing-productivity
    response = client.post("/api/trends/fishing-productivity", json={"region": {"lat": 19.1, "lon": 72.8}, "start_date": "2026-01-01", "end_date": "2026-09-01"})
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("POST /api/trends/fishing-productivity", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 10: POST /api/sar/create
    response = client.post("/api/sar/create", json={"object_type": "capsized_hull", "people_count": 4, "last_known_lat": 19.1, "last_known_lon": 72.8, "vessel_id": "V123"})
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("POST /api/sar/create", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 11: POST /api/sar/location
    response = client.post("/api/sar/location", json={"lat": 19.1, "lon": 72.8, "accuracy": 10.0, "source": "gps"})
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("POST /api/sar/location", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 12: POST /api/sar/predict-drift
    response = client.post("/api/sar/predict-drift", json={"incident_id": "sar-uuid-1234"})
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("POST /api/sar/predict-drift", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 13: GET /api/sar/{id}
    response = client.get("/api/sar/sar-uuid-1234")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("GET /api/sar/{id}", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 14: GET /api/sar/{id}/search-zones
    response = client.get("/api/sar/sar-uuid-1234/search-zones")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("GET /api/sar/{id}/search-zones", status, response.status_code, response.json() if status=="PASSED" else response.text))

    # Test 15: POST /api/sar/{id}/brief
    response = client.post("/api/sar/sar-uuid-1234/brief")
    status = "PASSED" if response.status_code == 200 else "FAILED"
    results.append(("POST /api/sar/{id}/brief", status, response.status_code, response.json() if status=="PASSED" else response.text))

    print("\n[ RESULTS ]")
    print(f"{'ENDPOINT':<40} | {'STATUS':<8} | {'CODE'}")
    print("-" * 65)
    for endpoint, status, code, _ in results:
        print(f"{endpoint:<40} | {status:<8} | {code}")
        
    print("\n[ DETAILED JSON PAYLOADS (PASSED) ]")
    for endpoint, status, code, payload in results:
        if status == "PASSED":
            print(f"\n{endpoint}")
            print(payload)

    print("\n[ PAYLOADS FOR FAILED ENDPOINTS ]")
    for endpoint, status, code, payload in results:
        if status == "FAILED":
            print(f"\n{endpoint} - HTTP {code}")
            print(payload)

if __name__ == "__main__":
    run_tests()
