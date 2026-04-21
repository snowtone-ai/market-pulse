# state.md — market-pulse タスク状態 SSOT
# 更新ルール: PostToolUse Hookが自動追記 / ユーザー明示指示時に手動更新
# 鉄則: state.md と実コードが矛盾した時、**実コードが正**

## タスク状態

| ID | タスク | Status | 担当ファイル | Verified |
|----|--------|--------|------------|---------|
| T-001 | GitHubリポジトリ作成 + Pages有効化（docs/指定） | pending | - | [ ] |
| T-002 | Python環境（requirements.txt + .venv） | pending | requirements.txt | [ ] |
| T-003 | scripts/fetch_market.py（yfinance + Finnhubカレンダー） | pending | scripts/fetch_market.py | [ ] |
| T-004 | scripts/fetch_news.py（Finnhubニュース取得） | pending | scripts/fetch_news.py | [ ] |
| T-005 | scripts/analyze.py（Gemini 2.5 Flash 呼び出し + JSON検証） | pending | scripts/analyze.py | [ ] |
| T-006 | Geminiプロンプト設計・品質検証（6ステップ安定出力確認） | pending | scripts/analyze.py | [ ] |
| T-007 | templates/report.html.j2（GS/JPM風デザイン + Chart.js統合） | pending | templates/report.html.j2 | [ ] |
| T-008 | scripts/generate_report.py（Jinja2レンダリング + docs/出力） | pending | scripts/generate_report.py | [ ] |
| T-009 | docs/manifest.json + docs/sw.js（PWA化） | pending | docs/manifest.json, docs/sw.js | [ ] |
| T-010 | docs/index.html（アーカイブ一覧、自動生成） | pending | docs/index.html | [ ] |
| T-011 | .github/workflows/generate.yml（cron UTC 22:00 + Secrets連携） | pending | .github/workflows/generate.yml | [ ] |
| T-012 | GitHub Secrets設定 + Actionsエンドツーエンドテスト | pending | - | [ ] |
| T-013 | Android PWA動作確認（ホーム画面追加 + オフライン） | pending | - | [ ] |

## Activity Log

| 日時 | ファイル | アクション |
|------|---------|----------|
| 2026-04-21 | bootstrap.ps1 実行 | 環境初期化 |
