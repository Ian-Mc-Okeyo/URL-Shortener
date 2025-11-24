import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def create_short_url(alias=None):
	payload = {"original_url": "https://example.com/analytics"}
	if alias:
		payload["alias"] = alias
	resp = client.post("/shorten", json=payload)
	assert resp.status_code == 200
	return resp.json()["short_url"].split("/")[-1]

def test_analytics_not_found():
	resp = client.get("/analytics/nonexistentcode")
	assert resp.status_code == 404

def test_analytics_no_clicks():
	code = create_short_url("noclicks")
	resp = client.get(f"/analytics/{code}")
	assert resp.status_code == 200
	data = resp.json()
	assert data["total_clicks"] == 0

def test_analytics_with_clicks():
	code = create_short_url("withclicks")
	# Simulate clicks with different user agents
	for ua in ["TestAgentA", "TestAgentB", "TestAgentA"]:
		client.get(f"/{code}", headers={"User-Agent": ua})
	resp = client.get(f"/analytics/{code}")
	assert resp.status_code == 200
	data = resp.json()
	assert data["total_clicks"] == 3
