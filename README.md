# Market Pulse

> 毎朝7時に株式・為替・商品市場のAI分析レポートを自動配信。サーバー費用ゼロで運用できる

GitHub Actions（クラウド上の自動実行基盤）が定刻に起動し、Gemini AIがニュースを6つの視点で深掘り分析したHTMLレポートをGitHub Pages（無料のウェブ公開サービス）で配信します。スマートフォンのホーム画面にアプリとして追加できるPWA（ウェブアプリをスマホアプリのように動かす技術）にも対応しています。

---

## 主な機能

- NVDA・AAPL・GOOGL・MSFT・TSMなどの主要株式、ドル円、金・原油の価格データを毎朝自動取得できる
- Gemini AIがニュース5件を「何が起きたか・なぜ重要か・市場の反応・3つのシナリオ・反対意見・今後の注目点」の6ステップで分析できる
- 30日間の株価推移をミニチャートで視覚的に確認できる
- 過去レポートをアーカイブ一覧から参照できる
- スマートフォンのホーム画面に追加してアプリとして利用できる（オフライン対応）

---

## 技術スタック

バックエンド：Python 3.12、yfinance（株価データ取得ライブラリ）、Jinja2（HTMLテンプレートエンジン）、httpx・asyncio（非同期HTTP通信ライブラリ）
インフラ・環境：GitHub Actions（自動実行基盤・無料）、GitHub Pages（ウェブ公開サービス・無料）
AI・外部API：Gemini 2.5 Flash（Google製AI）、Finnhub API（金融ニュース・経済カレンダー）

---

## 設計の工夫

- 日常運用でAPIトークンを消費しない設計（AIはシステム構築時のみ担当）
- GitHub ActionsのCron（定時実行）とGitHub Pagesを組み合わせた完全ゼロコスト運用

---

## セットアップ

必要なツール：Python 3.12、Gemini APIキー（Google AI Studio）、Finnhub APIキー

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows

pip install -r requirements.txt

# APIキーを .env.local に記入
cp .env.example .env.local

# レポート生成
python -m scripts.generate_report
# → docs/reports/YYYY-MM-DD.html が生成される
```

GitHub上での自動運用は、リポジトリをフォーク後にSettings → Secrets and variables → Actionsで `GEMINI_API_KEY` と `FINNHUB_API_KEY` を登録し、GitHub Pagesを有効化するだけで稼働します。

---

## ライセンス

MIT
