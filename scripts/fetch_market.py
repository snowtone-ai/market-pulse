"""市場データ取得: yfinance（価格/チャート）+ Finnhub（経済カレンダー）"""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
import yfinance as yf

JST = timezone(timedelta(hours=9))

WATCHLIST: dict[str, list[str]] = {
    "stocks": ["NVDA", "AAPL", "GOOGL", "MSFT", "TSM"],
    "indices": ["^GSPC", "^NDX", "^DJI", "^N225"],
    "fx": ["JPY=X", "EURUSD=X", "EURJPY=X"],
    "commodities": ["GC=F", "CL=F"],
}

DISPLAY_NAMES: dict[str, str] = {
    "^GSPC": "S&P 500", "^NDX": "NASDAQ 100", "^DJI": "Dow Jones", "^N225": "Nikkei 225",
    "JPY=X": "USD/JPY", "EURUSD=X": "EUR/USD", "EURJPY=X": "EUR/JPY",
    "GC=F": "Gold", "CL=F": "WTI Oil",
}


def _fetch_ticker(symbol: str) -> dict[str, Any]:
    """1銘柄の価格・変化率・過去30日チャートを取得（同期）"""
    for attempt in range(2):
        try:
            tk = yf.Ticker(symbol)
            hist = tk.history(period="30d", interval="1d")
            if hist.empty:
                return {"symbol": symbol, "error": "no data"}

            close = hist["Close"]
            latest = float(close.iloc[-1])
            prev = float(close.iloc[-2]) if len(close) >= 2 else latest
            change_pct = (latest - prev) / prev * 100 if prev else 0.0

            chart_dates = [d.strftime("%m/%d") for d in close.index]
            chart_prices = [round(float(p), 4) for p in close.values]

            return {
                "symbol": symbol,
                "name": DISPLAY_NAMES.get(symbol, symbol),
                "price": round(latest, 4),
                "change_pct": round(change_pct, 2),
                "chart_dates": chart_dates,
                "chart_prices": chart_prices,
            }
        except Exception as exc:
            if attempt == 0:
                time.sleep(60)
            else:
                return {"symbol": symbol, "error": str(exc)}
    return {"symbol": symbol, "error": "retry exhausted"}


def fetch_all_prices() -> dict[str, list[dict[str, Any]]]:
    """全ウォッチリストの価格データを返す"""
    result: dict[str, list[dict[str, Any]]] = {}
    for category, symbols in WATCHLIST.items():
        result[category] = [_fetch_ticker(s) for s in symbols]
    return result


async def fetch_economic_calendar(api_key: str) -> list[dict[str, Any]]:
    """Finnhub 経済カレンダーから今週の主要イベントを取得"""
    today = datetime.now(JST).date()
    from_date = today.strftime("%Y-%m-%d")
    to_date = (today + timedelta(days=6)).strftime("%Y-%m-%d")

    url = "https://finnhub.io/api/v1/calendar/economic"
    params = {"from": from_date, "to": to_date, "token": api_key}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            events = data.get("economicCalendar", [])
            # impact が "high" のみ抽出、最大10件
            high_impact = [e for e in events if e.get("impact") == "high"]
            return high_impact[:10]
    except Exception as exc:
        return [{"error": str(exc)}]


def fetch_market_data(finnhub_api_key: str) -> dict[str, Any]:
    """全市場データを収集して返す（fetch_market.py のメインエントリ）"""
    prices = fetch_all_prices()
    calendar = asyncio.run(fetch_economic_calendar(finnhub_api_key))

    return {
        "fetched_at": datetime.now(JST).isoformat(),
        "prices": prices,
        "economic_calendar": calendar,
    }


if __name__ == "__main__":
    import json
    import os
    from dotenv import load_dotenv

    load_dotenv(".env.local")
    key = os.environ.get("FINNHUB_API_KEY", "")
    data = fetch_market_data(key)
    print(json.dumps(data, ensure_ascii=False, indent=2))
