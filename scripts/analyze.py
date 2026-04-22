"""Gemini 2.5 Flash で市場分析: 1コールで選別・分析・構造化JSON出力"""
from __future__ import annotations

import json
import re
from typing import Any

import google.generativeai as genai

MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.3

SYSTEM_PROMPT = """あなたはゴールドマン・サックスのシニアマーケットストラテジストです。
グローバル市場の動向を幅広く分析し、日本人投資家に特に有益な情報を提供します。
分析は詳細・実用的・専門的に。日本語で出力してください。
米国テクノロジー株に偏らず、世界経済全体（中央銀行・マクロ経済・地政学・為替・日本市場）を均等にカバーしてください。"""

ANALYSIS_PROMPT = """以下の市場データとニュースプールを分析してください。

## 市場データ
{market_summary}

## ニュースプール（以下からGeminiが最重要5件を選別・分析）
{news_summary}

## ニュース選別基準（重要度順）
① 中央銀行・金融政策（FRB・日銀・ECBの決定・発言・利上げ/利下げ）
② マクロ経済指標（GDP・雇用統計・インフレ・貿易収支）
③ 地政学・政策リスク（関税・制裁・外交・地政学イベント）
④ 為替・コモディティ（円ドル・金・原油・日本市場への影響が大きいもの）
⑤ 株式市場動向（日本株・米国株・欧州株の主要な動き）

## 出力形式（必ずこのJSON構造で返してください）
```json
{{
  "date": "YYYY-MM-DD",
  "market_overview": "市場全体の2〜3文サマリー（主要指数・為替・コモディティの動きを含む）",
  "macro_context": {{
    "global_summary": "世界経済の現状と主要トレンド（3〜4文。中央銀行政策・インフレ・成長見通しを含む）",
    "japan_impact": "日本経済・株式・為替市場への具体的な影響（2〜3文）",
    "key_risks": ["リスク要因1（具体的に1文）", "リスク要因2（具体的に1文）", "リスク要因3（具体的に1文）"],
    "key_opportunities": ["注目の機会1（具体的に1文）", "注目の機会2（具体的に1文）"]
  }},
  "selected_news": [
    {{
      "rank": 1,
      "headline": "ニュース見出し",
      "source": "情報源",
      "url": "記事URL",
      "analysis": {{
        "what_happened": "何が起きたか（2〜3文。具体的な数値・背景を含む）",
        "why_it_matters": "なぜ重要か（2〜3文。市場・経済への構造的な意義を説明）",
        "market_reaction": "市場への影響（2〜3文。株・債券・為替・コモディティへの波及を含む）",
        "scenarios": {{
          "bull": "強気シナリオ（1〜2文。具体的な条件と結果）",
          "base": "基本シナリオ（1〜2文。最も可能性が高い展開）",
          "bear": "弱気シナリオ（1〜2文。具体的なリスクと影響）"
        }},
        "contrarian_view": "逆張り視点（1〜2文。コンセンサスに反する見方とその根拠）",
        "what_to_watch": "次に注目すべき指標/イベント（2〜3文。具体的な日程・閾値を含む）"
      }}
    }}
  ],
  "watchlist_highlights": [
    {{
      "symbol": "^N225",
      "name": "日経225",
      "price": 0.0,
      "change_pct": 0.0,
      "one_line": "価格変動の背景と今後の注目点（1文）"
    }}
  ],
  "editors_note": "編集後記（2〜3文。本日の全体テーマと日本人投資家へのメッセージ）"
}}
```

重要な制約:
- selected_news は必ず5件。ニュースプールが不足する場合は市場データを元に背景分析で補完すること
- watchlist_highlights は市場データにある銘柄から5〜7件（日経・為替・コモディティを優先）
- 上記JSON以外の文章を含めないでください。```json ... ``` ブロックのみで回答してください。"""


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

    return "\n".join(lines)


def _build_news_summary(news_list: list[dict[str, Any]]) -> str:
    lines = []
    for i, item in enumerate(news_list, 1):
        lines.append(f"{i}. {item['headline']}")
        if item.get("summary"):
            lines.append(f"   概要: {item['summary'][:300]}")
        lines.append(f"   出典: {item.get('source', 'N/A')} | {item.get('url', '')}")
    return "\n".join(lines)


def _extract_json(text: str) -> dict[str, Any]:
    """Gemini レスポンスから JSON ブロックを抽出・パース"""
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
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
