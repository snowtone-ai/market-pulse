"""Gemini 2.5 Flash で市場分析: 1コールで選別・分析・構造化JSON出力"""
from __future__ import annotations

import json
import re
from typing import Any

import google.generativeai as genai

MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.3

SYSTEM_PROMPT = """あなたはゴールドマン・サックスのシニアマーケットストラテジストです。
提供された市場データとニュースを分析し、指定されたJSON形式で回答してください。
分析は簡潔・実用的・専門的に。日本語で出力してください。"""

ANALYSIS_PROMPT = """以下の市場データとニュース（最大5件）を分析してください。

## 市場データ
{market_summary}

## ニュース
{news_summary}

## 出力形式（必ずこのJSON構造で返してください）
```json
{{
  "date": "YYYY-MM-DD",
  "market_overview": "市場全体の1〜2文サマリー（日本語）",
  "selected_news": [
    {{
      "rank": 1,
      "headline": "ニュース見出し",
      "source": "情報源",
      "url": "記事URL",
      "analysis": {{
        "what_happened": "何が起きたか（1〜2文）",
        "why_it_matters": "なぜ重要か（1〜2文）",
        "market_reaction": "市場への影響（1〜2文）",
        "scenarios": {{
          "bull": "強気シナリオ（1文）",
          "base": "基本シナリオ（1文）",
          "bear": "弱気シナリオ（1文）"
        }},
        "contrarian_view": "逆張り視点（1文）",
        "what_to_watch": "注目すべき次の指標/イベント（1〜2文）"
      }}
    }}
  ],
  "watchlist_highlights": [
    {{
      "symbol": "NVDA",
      "name": "NVIDIA",
      "price": 0.0,
      "change_pct": 0.0,
      "one_line": "1行コメント"
    }}
  ],
  "economic_calendar_highlights": [
    {{
      "event": "イベント名",
      "date": "YYYY-MM-DD",
      "impact": "high",
      "note": "注目ポイント1文"
    }}
  ],
  "editors_note": "編集後記（全体を通じた1〜2文のまとめ）"
}}
```

重要: 上記JSON以外の文章を含めないでください。```json ... ``` ブロックのみで回答してください。"""


def _build_market_summary(market_data: dict[str, Any]) -> str:
    lines = []
    prices = market_data.get("prices", {})

    for category, items in prices.items():
        lines.append(f"### {category}")
        for item in items:
            if "error" in item:
                continue
            sign = "+" if item["change_pct"] >= 0 else ""
            lines.append(
                f"- {item['name']} ({item['symbol']}): {item['price']} "
                f"({sign}{item['change_pct']}%)"
            )

    calendar = market_data.get("economic_calendar", [])
    if calendar and not calendar[0].get("error"):
        lines.append("\n### 今週の経済イベント（高重要度）")
        for ev in calendar[:5]:
            lines.append(f"- {ev.get('event', '')} ({ev.get('time', '')})")

    return "\n".join(lines)


def _build_news_summary(news_list: list[dict[str, Any]]) -> str:
    lines = []
    for i, item in enumerate(news_list, 1):
        lines.append(f"{i}. {item['headline']}")
        if item.get("summary"):
            lines.append(f"   概要: {item['summary'][:200]}")
        lines.append(f"   出典: {item.get('source', 'N/A')} | {item.get('url', '')}")
    return "\n".join(lines)


def _extract_json(text: str) -> dict[str, Any]:
    """Gemini レスポンスから JSON ブロックを抽出・パース"""
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # フォールバック: テキスト全体をJSONとして試みる
    return json.loads(text.strip())


def analyze(
    market_data: dict[str, Any],
    news_list: list[dict[str, Any]],
    api_key: str,
    date_str: str,
) -> dict[str, Any]:
    """Gemini 2.5 Flash で分析し、構造化JSONを返す"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(
            temperature=TEMPERATURE,
            response_mime_type="text/plain",
        ),
    )

    market_summary = _build_market_summary(market_data)
    news_summary = _build_news_summary(news_list)

    prompt = ANALYSIS_PROMPT.format(
        market_summary=market_summary,
        news_summary=news_summary,
    )

    response = model.generate_content(prompt)
    raw_text = response.text

    try:
        result = _extract_json(raw_text)
        result["date"] = date_str
        # watchlist_highlights に chart データを補完
        prices_flat = {
            item["symbol"]: item
            for items in market_data.get("prices", {}).values()
            for item in items
            if "error" not in item
        }
        for wh in result.get("watchlist_highlights", []):
            sym = wh.get("symbol", "")
            if sym in prices_flat:
                src = prices_flat[sym]
                wh["price"] = src.get("price", wh.get("price", 0))
                wh["change_pct"] = src.get("change_pct", wh.get("change_pct", 0))
                wh["chart_dates"] = src.get("chart_dates", [])
                wh["chart_prices"] = src.get("chart_prices", [])
        return result
    except (json.JSONDecodeError, KeyError) as exc:
        return {
            "date": date_str,
            "error": f"JSON parse failed: {exc}",
            "raw": raw_text,
        }


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from scripts.fetch_market import fetch_market_data
    from scripts.fetch_news import fetch_news

    load_dotenv(".env.local")
    gemini_key = os.environ["GEMINI_API_KEY"]
    finnhub_key = os.environ["FINNHUB_API_KEY"]
    from datetime import datetime, timezone, timedelta
    date_str = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")

    market = fetch_market_data(finnhub_key)
    news = fetch_news(finnhub_key)
    result = analyze(market, news, gemini_key, date_str)
    print(json.dumps(result, ensure_ascii=False, indent=2))
