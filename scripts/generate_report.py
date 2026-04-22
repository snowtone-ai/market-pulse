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


def _regenerate_archive_index(docs_dir: Path, env: Environment) -> None:
    """docs/reports/ 内の全 YYYY-MM-DD.html をスキャンし、index.html を完全再生成。
    regex パッチ方式を廃止: ファイルスキャンで常に正確なリストを保証する。"""
    reports_dir = docs_dir / "reports"
    report_files = sorted(reports_dir.glob("????-??-??.html"), reverse=True)
    dates = [f.stem for f in report_files]

    template = env.get_template("index.html.j2")
    html = template.render(dates=dates)

    index_path = docs_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")


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

    _regenerate_archive_index(docs_dir, env)
    print("[generate] アーカイブインデックス再生成完了")

    return out_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Market Pulse レポート生成")
    parser.add_argument("--date", help="生成日付 YYYY-MM-DD（省略時: 今日 JST）")
    args = parser.parse_args()
    generate(args.date)
