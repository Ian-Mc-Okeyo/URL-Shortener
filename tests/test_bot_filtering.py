from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def create_short(alias: str):
    resp = client.post("/shorten", json={"original_url": "https://example.com/bot", "custom_alias": alias})
    assert resp.status_code == 200
    return alias

def test_bot_filtering_counts():
    code = create_short("botfiltertest")
    # Simulate human clicks
    for _ in range(3):
        client.get(f"/{code}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    # Simulate bot clicks
    bot_agents = [
        "Googlebot/2.1 (+http://www.google.com/bot.html)",
        "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
        "curl/8.1.2"
    ]
    for ua in bot_agents:
        client.get(f"/{code}", headers={"User-Agent": ua})

    analytics = client.get(f"/analytics/{code}")
    assert analytics.status_code == 200
    data = analytics.json()
    assert data["total_clicks"] == 6
    assert data["bot_clicks"] == 3
    assert data["human_clicks"] == 3
    assert isinstance(data["user_agents"], dict)
    assert sum(data["user_agents"].values()) == 6
