# 📊 Market Pulse

**毎朝7時（JST）に市場レポートを自動生成し、PWAで配信するシステム**

[![Generate Market Report](https://github.com/snowtone-ai/market-pulse/actions/workflows/generate.yml/badge.svg)](https://github.com/snowtone-ai/market-pulse/actions/workflows/generate.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-blue?logo=github)](https://snowtone-ai.github.io/market-pulse/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)

---

## 🌐 デモ

**[https://snowtone-ai.github.io/market-pulse/](https://snowtone-ai.github.io/market-pulse/)**

Androidのホーム画面に追加するとアプリとして利用できます（PWA対応）。

---

## 概要

GitHub Actions が毎朝 UTC 22:00（JST 07:00）に自動起動し、  
**Gemini 2.5 Flash** がニュースを分析・HTML レポートを生成、**GitHub Pages** で即時配信します。  
Claudeは初期構築のみ担当し、**日常運用でClaudeトークンを消費しません**。

```
yfinance / Finnhub          Gemini 2.5 Flash          GitHub Pages PWA
   市場データ取得      →      6ステップ分析       →     https://...github.io
   ニュース取得（5件）         構造化 JSON 出力          毎朝7時 自動更新
```

---

## 機能

| 機能 | 詳細 |
|------|------|
| **市場データ** | NVDA / AAPL / GOOGL / MSFT / TSM + 主要指数 + USD/JPY + 金/原油 |
| **ニュース分析** | 1日5件（AI/テック重点）を Gemini が6ステップで深掘り |
| **6ステップ分析** | What Happened → Why It Matters → Market Reaction → 3 Scenarios → Contrarian View → What to Watch |
| **ミニチャート** | 30日 sparkline（Chart.js 4.x） |
| **PWA** | オフライン対応・Androidホーム画面追加 |
| **完全自動** | GitHub Actions cron + GitHub Pages 自動デプロイ |

---

## セットアップ（フォーク → 5ステップで稼働）

### 1. リポジトリをフォーク

```
Fork: https://github.com/snowtone-ai/market-pulse
```

### 2. GitHub Pages を有効化

**Settings → Pages → Source**: `Deploy from a branch` → Branch: `main` / Folder: `/docs`

### 3. API キーを取得

| サービス | 取得先 | 無料枠 |
|---------|--------|--------|
| **Gemini API** | [Google AI Studio](https://aistudio.google.com/) | 250 RPD / 10 RPM |
| **Finnhub** | [finnhub.io](https://finnhub.io/) | 60 calls/min |

### 4. GitHub Secrets に登録

**Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | Google AI Studio で取得したキー |
| `FINNHUB_API_KEY` | Finnhub で取得したキー |

### 5. 手動で初回実行

**Actions → Generate Market Report → Run workflow**

✅ `docs/reports/YYYY-MM-DD.html` が生成されれば完了。翌朝から自動で動きます。

---

## アーキテクチャ

```
.
├── scripts/
│   ├── fetch_market.py      # yfinance（価格）+ Finnhub（経済カレンダー）
│   ├── fetch_news.py        # Finnhub ニュース取得・スコアリング（上位5件）
│   ├── analyze.py           # Gemini 2.5 Flash 呼び出し・JSON 検証
│   └── generate_report.py   # オーケストレーター・Jinja2 レンダリング
├── templates/
│   └── report.html.j2       # ダークテーマ・Chart.js sparkline
├── docs/                    # GitHub Pages 公開ディレクトリ
│   ├── reports/             # 日付別レポート（例: 2026-04-21.html）
│   ├── index.html           # アーカイブ一覧（自動更新）
│   ├── manifest.json        # PWA マニフェスト
│   └── sw.js                # Service Worker
└── .github/workflows/
    └── generate.yml         # cron: '0 22 * * *'（UTC 22:00 = JST 07:00）
```

---

## カスタマイズ

**ウォッチリスト変更** → `scripts/fetch_market.py` の `WATCHLIST` を編集

**レポート時刻変更** → `.github/workflows/generate.yml` の `cron` を変更  
（例: JST 06:00 にしたい場合 → `'0 21 * * *'`）

**デザイン変更** → `templates/report.html.j2` を編集

---

## ローカル実行

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

# .env.local に API キーを記入
cp .env.example .env.local

python -m scripts.generate_report
# → docs/reports/YYYY-MM-DD.html が生成される
```

---

## 技術スタック

| 役割 | 技術 |
|------|------|
| 分析エンジン | Gemini 2.5 Flash（temperature 0.3） |
| 市場データ | yfinance 0.2+（APIキー不要） |
| ニュース / カレンダー | Finnhub API |
| HTTP クライアント | httpx + asyncio |
| HTML テンプレート | Jinja2 3.1+ |
| チャート | Chart.js 4.x（CDN） |
| CI/CD | GitHub Actions（パブリックリポジトリ：無料・無制限） |
| ホスティング | GitHub Pages（CDN付き・無料） |
| PWA | Web App Manifest + Service Worker |

---

## ライセンス

MIT
