import math
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_ab_testing_distribution():
    alias = "abtest"
    resp = client.post(
        "/shorten",
        json={
            "original_url": "https://example.com/primary",
            "variant_url": "https://example.com/secondary",
            "split_percent": 70,
            "custom_alias": alias,
        },
    )
    assert resp.status_code == 200
    # Perform multiple redirects
    total_requests = 50
    for _ in range(total_requests):
        client.get(f"/{alias}")

    analytics = client.get(f"/analytics/{alias}")
    assert analytics.status_code == 200
    data = analytics.json()
    assert data["variant_distribution"] is not None
    primary_count = data["variant_distribution"].get("https://example.com/primary", 0)
    secondary_count = data["variant_distribution"].get("https://example.com/secondary", 0)
    assert primary_count + secondary_count == data["total_clicks"]

    # Check distribution is roughly within tolerance (allow wide tolerance due to randomness)
    expected_primary = total_requests * 0.7
    tolerance = total_requests * 0.25  # 25% tolerance
    assert abs(primary_count - expected_primary) <= tolerance, (
        f"Primary distribution out of tolerance: got {primary_count} expected around {expected_primary}"
    )
