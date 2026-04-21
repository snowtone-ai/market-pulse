# market-pulse — CLAUDE.md
# 更新: 2026-04-21 | Python 3.12 + GitHub Actions + Gemini 2.5 Flash + GitHub Pages PWA

## ロール
毎朝7時（JST）に市場レポートHTMLを自動生成し、GitHub Pages PWAで配信するシステムを構築する。
分析エンジンはGemini 2.5 Flash。Claudeの役割は初期構築のみ（日常運用でClaudeトークンを消費しない）。

## ファイル構造（変更禁止）
```
market-pulse/
├── scripts/           # Pythonスクリプト（データ取得・分析・生成）
├── templates/         # Jinja2 HTMLテンプレート
├── docs/              # GitHub Pages公開ディレクトリ
│   ├── reports/       # 日付別レポート HTML（例: 2026-04-21.html）
│   ├── index.html     # アーカイブ一覧
│   ├── manifest.json  # PWAマニフェスト
│   └── sw.js          # Service Worker
├── .github/workflows/ # GitHub Actions
└── .claude/           # pm-zero フレームワーク管理ファイル
```

## タスク開始前の確認（必須）
1. `.claude/state.md` を読む → 完了済みタスクを再実装しない
2. `.claude/decisions.md` を読む → 確定済み技術選定を覆さない
3. `.env.example` の全KEYが環境に存在するか確認

## コーディング規則
- Python 3.12+、型ヒント必須、black フォーマット適用
- 非同期処理: `asyncio` + `httpx`（`requests` より優先）
- API呼び出しは全て `try/except` でラップ → 失敗時 `.claude/issues.md` に追記
- HTML生成: `Jinja2` テンプレートを使用（f-string で HTMLを組み立てない）
- Chart.js 4.x でチャート描画（CDN経由、外部ライブラリ追加禁止）

## API規則
- **Gemini**: モデル `gemini-2.5-flash`（`gemini-2.0-flash` は廃止済み、使用禁止）
  - 1回のAPIコールで選別・分析・構造化JSON出力を完結させる
  - temperature: 0.3（分析の一貫性を優先）
  - 無料枠: 10 RPM / 250 RPD → 日次1回のみ使用
- **yfinance**: APIキー不要。レート制限に引っかかったら60秒待機して1回リトライ
- **Finnhub**: 60コール/分。ニュース取得 + 経済指標カレンダーに使用

## GitHub Actions規則
- スケジュール: `cron: '0 22 * * *'`（UTC 22:00 = JST 翌7:00）
- シークレット: `GEMINI_API_KEY`、`FINNHUB_API_KEY` はGitHub Secretsに保存（コードへのハードコード禁止）
- 生成物は `docs/` ディレクトリに出力 → Actions が自動 push → Pages が自動デプロイ
- ワークフロー失敗時: GitHub Actions の標準メール通知に委任（追加設定不要）

## レポート生成規則
- 対象ニュース: 1日5件まで（AI/テック重点 → 米国株 → 日本株 → 為替/コモディティの優先順）
- 分析フレームワーク（6ステップ）:
  ① What happened → ② Why it matters → ③ Market reaction
  → ④ Three scenarios (Bull/Base/Bear) → ⑤ Contrarian View → ⑥ What to watch
- 週末・祝日: 市場休場でもレポート生成（地政学ニュース + 翌週プレビュー）
- アーカイブ: 全履歴を `docs/reports/YYYY-MM-DD.html` で保持

## 禁止事項
- APIキーをコード・テンプレートにハードコードすること
- `gemini-2.0-flash` を使うこと（廃止済み）
- `requests` を新規コードで使うこと（`httpx` を使う）
- Claudeトークンをレポート日常生成に消費すること
- `docs/` 以外のディレクトリをGitHub Pagesのルートにすること
- f-string でHTMLを直接組み立てること（Jinja2テンプレートを使う）
