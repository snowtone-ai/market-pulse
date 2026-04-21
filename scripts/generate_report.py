"""メインオーケストレーター: データ取得 → Gemini分析 → Jinja2レンダリング → docs/出力"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scripts.fetch_market import fetch_market_data
from scripts.fetch_news import fetch_news
from scripts.analyze import analyze

JST = timezone(timedelta(hours=9))


def _format_price(value: float) -> str:
    if value >= 1000:
        return f"{value:,.2f}"
    elif value >= 10:
        return f"{value:.2f}"
    else:
        return f"{value:.4f}"


def _build_chart_data(watchlist_highlights: list[dict]) -> list[dict]:
    result = []
    for item in watchlist_highlights:
        sym = item.get("symbol", "")
        prices = item.get("chart_prices", [])
        dates = item.get("chart_dates", [])
        if not prices:
            continue
        up = (prices[-1] >= prices[0]) if len(prices) >= 2 else True
        result.append({
            "id": sym.replace("/", "-"),
            "dates": dates,
            "prices": prices,
            "up": up,
        })
    return result


def _update_archive_index(docs_dir: Path, date_str: str) -> None:
    """docs/index.html の __REPORTS__ 配列に新しい日付を追加"""
    index_path = docs_dir / "index.html"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    marker = "const reports = window.__REPORTS__ || [];"
    if marker not in content:
        return

    # 既存の日付リストを抽出
    import re
    match = re.search(r"window\.__REPORTS__\s*=\s*(\[.*?\]);", content, re.DOTALL)
    if match:
        try:
            existing = json.loads(match.group(1))
        except json.JSONDecodeError:
            existing = []
    else:
        existing = []

    if date_str not in existing:
        existing.insert(0, date_str)
        # 最大90件
        existing = existing[:90]

    new_reports_js = f"window.__REPORTS__ = {json.dumps(existing)};"
    if match:
        content = content[:match.start()] + new_reports_js + content[match.end():]
    else:
        content = content.replace(marker, f"{new_reports_js}\n    {marker}")

    index_path.write_text(content, encoding="utf-8")


def generate(date_str: str | None = None) -> Path:
    load_dotenv(ROOT / ".env.local", override=False)

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    finnhub_key = os.environ.get("FINNHUB_API_KEY", "")

    if not gemini_key:
        raise EnvironmentError("GEMINI_API_KEY is not set")
    if not finnhub_key:
        raise EnvironmentError("FINNHUB_API_KEY is not set")

    if date_str is None:
        date_str = datetime.now(JST).strftime("%Y-%m-%d")

    print(f"[generate] {date_str} — データ取得開始")
    market_data = fetch_market_data(finnhub_key)
    print("[generate] ニュース取得中...")
    news_list = fetch_news(finnhub_key)
    print(f"[generate] ニュース {len(news_list)} 件取得完了。Gemini 分析中...")

    analysis = analyze(market_data, news_list, gemini_key, date_str)

    if "error" in analysis:
        print(f"[generate] WARNING: Gemini error: {analysis['error']}", file=sys.stderr)

    prices = market_data.get("prices", {})
    chart_data = _build_chart_data(analysis.get("watchlist_highlights", []))

    env = Environment(
        loader=FileSystemLoader(str(ROOT / "templates")),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["format_price"] = _format_price

    template = env.get_template("report.html.j2")
    html = template.render(
        data=analysis,
        prices=prices,
        chart_data_json=json.dumps(chart_data),
    )

    docs_dir = ROOT / "docs"
    reports_dir = docs_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    out_path = reports_dir / f"{date_str}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"[generate] レポート生成完了: {out_path}")

    _update_archive_index(docs_dir, date_str)
    print("[generate] アーカイブインデックス更新完了")

    return out_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Market Pulse レポート生成")
    parser.add_argument("--date", help="生成日付 YYYY-MM-DD（省略時: 今日 JST）")
    args = parser.parse_args()
    generate(args.date)
