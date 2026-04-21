"""Finnhub ニュース取得: AI/テック重点 → 米国株 → 日本株 → 為替/コモディティ"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

JST = timezone(timedelta(hours=9))

# 優先順位付きカテゴリ
CATEGORIES = [
    ("general", "general"),     # AI/テック含む全般ニュース
    ("forex", "forex"),
    ("merger", "merger"),
]

# ウォッチリスト銘柄（個別ニュース取得用）
STOCK_SYMBOLS = ["NVDA", "AAPL", "GOOGL", "MSFT", "TSM"]

MAX_NEWS = 5
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
        return resp.json()[:5]
    except Exception as exc:
        return [{"headline": f"Error fetching {category}", "error": str(exc)}]


def _score_news(item: dict[str, Any]) -> int:
    """優先スコア: AI/テック > 米国株 > 為替 > その他"""
    headline = (item.get("headline") or item.get("summary") or "").lower()
    related = (item.get("related") or "").upper()
    score = 0
    if any(w in headline for w in ["ai", "artificial intelligence", "nvidia", "semiconductor", "tech"]):
        score += 100
    if any(s in related for s in STOCK_SYMBOLS):
        score += 50
    if any(w in headline for w in ["fed", "rate", "inflation", "gdp", "earnings"]):
        score += 30
    return score


async def fetch_news_async(api_key: str) -> list[dict[str, Any]]:
    today = datetime.now(JST).date()
    from_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    async with httpx.AsyncClient(timeout=15, limits=httpx.Limits(max_connections=10)) as client:
        tasks = []
        for symbol in STOCK_SYMBOLS:
            tasks.append(_fetch_company_news(client, symbol, from_date, to_date, api_key))
        for category, _ in CATEGORIES:
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

    # 必要フィールドだけ返す
    cleaned = []
    for item in all_news[:MAX_NEWS]:
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
