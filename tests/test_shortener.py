
import pytest
from fastapi.testclient import TestClient
from random import randint
from app.app import app

client = TestClient(app)

def test_create_short_url_success():
	resp = client.post("/shorten", json={"original_url": "https://example.com"})
	assert resp.status_code == 200
	data = resp.json()
	assert "short_url" in data
	assert data["short_url"].startswith("http")

def test_create_short_url_with_alias():
	alias = "myalias" + str(randint(1000, 9999))
	resp = client.post("/shorten", json={"original_url": "https://example.com/2", "custom_alias": alias})
	assert resp.status_code == 200
	data = resp.json()
	assert data["short_url"].endswith(f"/{alias}")

def test_create_short_url_duplicate_alias():
	alias = "dupalias" + str(randint(1000, 9999))
	# First creation should succeed
	resp1 = client.post("/shorten", json={"original_url": "https://example.com/3", "custom_alias": alias})
	assert resp1.status_code == 200
	# Second creation with same alias should fail
	resp2 = client.post("/shorten", json={"original_url": "https://example.com/4", "custom_alias": alias})
	assert resp2.status_code in (400, 409)

def test_create_short_url_invalid_url():
	resp = client.post("/shorten", json={"original_url": "not-a-url"})
	assert resp.status_code == 422

def test_create_short_url_with_ttl():
	resp = client.post("/shorten", json={"original_url": "https://example.com/ttl", "ttl_seconds": 60})
	assert resp.status_code == 200
	data = resp.json()
	assert "short_url" in data
	# Optionally check for expires_at if returned
	if "expires_at" in data:
		assert isinstance(data["expires_at"], str)
