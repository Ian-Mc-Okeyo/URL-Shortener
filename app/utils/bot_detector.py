BOT_SIGNATURES = [
    "bot", "crawler", "spider", "slurp", "headless", "curl", "wget", "python-requests",
    "httpclient", "scrapy", "selenium", "automation"
]

def is_bot(user_agent: str | None) -> bool:
    if not user_agent:
        return False
    ua = user_agent.lower()
    return any(sig in ua for sig in BOT_SIGNATURES)
