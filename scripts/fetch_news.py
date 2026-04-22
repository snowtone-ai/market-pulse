"""Finnhub ニュース取得: グローバル経済重視（中央銀行・マクロ・地政学・為替・株式）"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

JST = timezone(timedelta(hours=9))

CATEGORIES = [
    "general",
    "forex",
    "merger",
]

# 幅広い業種をカバー（テクノロジー偏重を排除）
STOCK_SYMBOLS = ["AAPL", "AMZN", "GS", "JPM", "XOM"]

MAX_NEWS_POOL = 15   # Gemini が 5 件選別するためのプール
FINNHUB_BASE = "https://finnhub.io/api/v1"


async def _fetch_company_news(
    client: httpx.AsyncClient,
    symbol: str,
    from_date: str,
    to_date: str,
    api_key: str,
) -> list[dict[str, Any]]:
    try:
        resp = await client.get(
            f"{FINNHUB_BASE}/company-news",
            params={"symbol": symbol, "from": from_date, "to": to_date, "token": api_key},
        )
        resp.raise_for_status()
        return resp.json()[:3]
    except Exception as exc:
        return [{"headline": f"Error fetching {symbol}", "error": str(exc)}]


async def _fetch_general_news(
    client: httpx.AsyncClient,
    category: str,
    api_key: str,
) -> list[dict[str, Any]]:
    try:
        resp = await client.get(
            f"{FINNHUB_BASE}/news",
            params={"category": category, "minId": 0, "token": api_key},
        )
        resp.raise_for_status()
        return resp.json()[:8]
    except Exception as exc:
        return [{"headline": f"Error fetching {category}", "error": str(exc)}]


def _score_news(item: dict[str, Any]) -> int:
    """市場重要度スコア: 中央銀行/マクロ > 地政学 > 為替/コモディティ > 株式市場"""
    headline = (item.get("headline") or "").lower()
    summary = (item.get("summary") or "").lower()
    text = headline + " " + summary[:200]
    score = 0

    # 中央銀行・金融政策（最高優先）
    if any(w in text for w in [
        "fed", "federal reserve", "fomc", "boj", "bank of japan",
        "ecb", "rate hike", "rate cut", "interest rate", "monetary policy",
        "inflation target", "yield curve", "quantitative",
    ]):
        score += 100

    # マクロ経済指標
    if any(w in text for w in [
        "gdp", "inflation", "cpi", "ppi", "unemployment", "nonfarm",
        "payroll", "trade balance", "current account", "recession",
        "economic growth", "consumer price",
    ]):
        score += 80

    # 地政学・政策リスク
    if any(w in text for w in [
        "tariff", "sanction", "trade war", "geopolit", "trump",
        "china", "japan", "russia", "ukraine", "middle east", "opec",
    ]):
        score += 60

    # 為替・コモディティ
    if any(w in text for w in [
        "dollar", "yen", "euro", "gold", "oil", "crude", "commodity",
        "forex", "currency", "brent",
    ]):
        score += 40

    # 株式市場全般
    if any(w in text for w in [
        "stock", "market", "nasdaq", "s&p 500", "dow jones", "nikkei",
        "earnings", "revenue", "quarterly results",
    ]):
        score += 20

    return score


async def fetch_news_async(api_key: str) -> list[dict[str, Any]]:
    today = datetime.now(JST).date()
    from_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    async with httpx.AsyncClient(timeout=15, limits=httpx.Limits(max_connections=10)) as client:
        tasks = []
        for symbol in STOCK_SYMBOLS:
            tasks.append(_fetch_company_news(client, symbol, from_date, to_date, api_key))
        for category in CATEGORIES:
            tasks.append(_fetch_general_news(client, category, api_key))

        results = await asyncio.gather(*tasks)

    all_news: list[dict[str, Any]] = []
    seen_headlines: set[str] = set()

    for batch in results:
        for item in batch:
            if "error" in item:
                continue
            headline = item.get("headline", "")
            if headline and headline not in seen_headlines:
                seen_headlines.add(headline)
                item["_score"] = _score_news(item)
                all_news.append(item)

    all_news.sort(key=lambda x: (x["_score"], x.get("datetime", 0)), reverse=True)

    cleaned = []
    for item in all_news[:MAX_NEWS_POOL]:
        cleaned.append({
            "headline": item.get("headline", ""),
            "summary": item.get("summary", ""),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "datetime": item.get("datetime", 0),
            "related": item.get("related", ""),
            "category": item.get("category", ""),
        })

    return cleaned


def fetch_news(api_key: str) -> list[dict[str, Any]]:
    return asyncio.run(fetch_news_async(api_key))


if __name__ == "__main__":
    import json
    import os
    from dotenv import load_dotenv

    load_dotenv(".env.local")
    key = os.environ.get("FINNHUB_API_KEY", "")
    news = fetch_news(key)
    print(json.dumps(news, ensure_ascii=False, indent=2))
