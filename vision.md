# market-pulse — vision.md
# 2026-04-21 | v1.0

---

## 1. プロジェクト概要

**市場情勢エージェント**。世界の株式・為替・コモディティ市場の重要な動きを、
Goldman Sachs / JPMorganのトップアナリスト視点で分析し、毎朝7時（JST）に
AndroidスマホのPWAアプリとして届ける自動レポートシステム。

目的は投資ではなく**世界情勢の理解**。市場を通して地政学・経済・テクノロジーの
連鎖を読む力を養う。

---

## 2. ゴール

| # | ゴール | 計測基準 |
|---|--------|---------|
| G1 | 毎朝7時、自動でレポートが届く | GitHub Actionsのcronが安定稼働（月次稼働率95%以上） |
| G2 | Claudeトークンを日常運用で消費しない | 日次Gemini APIのみで完結 |
| G3 | 3分以内で読める量（5件/日） | ニュース件数上限5件 |
| G4 | GS/JPMレポート品質の分析 | 6ステップフレームワーク全項目が毎回出力される |
| G5 | Androidでネイティブアプリ同等のUX | PWA（ホーム画面追加 + オフライン対応） |
| G6 | 全レポートがアーカイブとして永続 | `docs/reports/YYYY-MM-DD.html` 形式で全日付保持 |

---

## 3. アーキテクチャ

```
GitHub Actions（毎日UTC 22:00）
  │
  ├── [scripts/fetch_market.py]
  │     yfinance → 株価・指数・為替・コモディティデータ取得
  │
  ├── [scripts/fetch_news.py]
  │     Finnhub → ニュース取得（AI/テック重点）
  │     Finnhub → 経済指標カレンダー取得
  │
  ├── [scripts/analyze.py]
  │     Gemini 2.5 Flash API → ニュース選別（5件）+ 6ステップ分析 + 構造化JSON
  │
  ├── [scripts/generate_report.py]
  │     Jinja2 → 構造化JSONをHTMLに変換
  │     Chart.js 4.x → 週次推移 + セクターヒートマップ
  │
  └── [docs/reports/YYYY-MM-DD.html] + [docs/index.html] をgit commit → push
        │
        └── GitHub Pages（CDN） → PWA
              Android ホーム画面からアクセス
```

**データソース確定（Phase 0リサーチ済み）**

| ソース | 対象 | 制限 | APIキー |
|--------|------|------|--------|
| yfinance | 株価/指数/為替/コモディティ | 非公式（安定性リスクあり） | 不要 |
| Finnhub | ニュース / 経済カレンダー | 60コール/分（無料） | 必要 |
| Gemini 2.5 Flash | 分析・選別 | 10 RPM / 250 RPD（無料） | 必要 |

---

## 4. 機能仕様

### F-01: 市場データ取得

**対象データ（固定）**
- 主要指数: S&P 500、Nasdaq 100、Dow Jones、Nikkei 225、TOPIX
- AI/テック個別: NVDA、AAPL、GOOGL、MSFT、TSM（ADR）
- 為替: USD/JPY、EUR/USD、EUR/JPY
- コモディティ: 金（GC=F）、原油WTI（CL=F）
- セクターETF（S&P 500）: XLK、XLF、XLE、XLV、XLI、XLY、XLP、XLU、XLRE、XLB、XLC
- 日本セクター指数: TOPIX-17シリーズ（yfinanceで取得可能な範囲）

```gherkin
Given GitHub Actionsがトリガーされた
When scripts/fetch_market.py が実行される
Then 上記全銘柄の前日終値・前日比・週次データが取得される
And 取得失敗した銘柄はスキップしてissues.mdに記録（全体は止まらない）
```

### F-02: ニュース取得と選別

```gherkin
Given 市場データ取得が完了した
When scripts/fetch_news.py がFinnhubからニュースを取得する
Then 過去24時間のニュースが取得される
And 優先度: AI/テック > 米国株マクロ > 日本株 > 為替/コモディティ の順で取得

Given ニュースリストがGemini 2.5 Flashに渡された
When 重要度評価プロンプトが実行される
Then 上位5件が選別されて返される
And 選別理由が構造化JSONに含まれる
```

### F-03: 6ステップ分析（Gemini 2.5 Flash）

各ニュース（最大5件）に対して以下を生成:

```gherkin
Given 選別された5件のニュースと市場データが揃った
When Gemini 2.5 Flash の分析プロンプトが実行される（1回のAPIコール）
Then 各ニュースについて以下が構造化JSONで返される:
  ① What happened    : 2-3文、日本語、英語専門用語+括弧内日本語訳
  ② Why it matters   : 因果連鎖、GS/JPMアナリスト視点
  ③ Market reaction  : 数値（前日比%）+ 解釈
  ④ Three scenarios  : Bull/Base/Bear の3シナリオ（各2-3文）
  ⑤ Contrarian View  : 市場コンセンサスが見落としている視点（1-2文）
  ⑥ What to watch    : 次のカタリスト（日付付き具体的イベント）
And 超重要用語（1ニュースにつき最大1個）には「※アナリストメモ」注釈が付く
And 経済指標カレンダー（当日・翌日）がレポート冒頭に付与される
```

**[ASSUMPTION] Gemini 2.5 Flash の出力品質が6ステップ全項目を安定生成できる（検証タスクT-006で確認）**

### F-04: HTMLレポート生成

```gherkin
Given 分析JSONが生成された
When scripts/generate_report.py が Jinja2 で HTML を生成する
Then docs/reports/YYYY-MM-DD.html が出力される
And デザインはGS/JPMリサーチレポート風（白背景・セリフ+サンセリフ混用・プロフェッショナル）
And Chart.js 4.x で以下のチャートが埋め込まれる:
    - 主要指数の週次推移ライン（5銘柄）
    - S&P 500 11セクター + 日経主要セクターのヒートマップ（前日比カラーコード）
And レポートはモバイルファースト（375px基準）でレスポンシブ
And 英語専門用語は日本語訳を括弧またはtitleタグで付与
```

### F-05: PWAとアーカイブ

```gherkin
Given GitHub Pagesにデプロイ済み
When AndroidユーザーがChrome/Edgeで docs/ URLを開く
Then manifest.json の設定により「ホーム画面に追加」ができる
And ホーム画面からアプリとして起動できる

Given Service Worker が登録済み
When ユーザーがオフライン時に最新レポートを開く
Then キャッシュから直近のレポートが表示される

Given 過去のレポートが docs/reports/ に蓄積されている
When ユーザーが docs/index.html を開く
Then 全日付のレポートリンクが新しい順に表示される
And 日付の横に「平日 / 週末」ラベルが表示される
```

### F-06: 週末・祝日レポート

```gherkin
Given 当日が土曜または日曜（または主要市場の祝日）
When GitHub Actionsがトリガーされる
Then 市場データは週次サマリーのみ取得（前週終値との比較）
And ニュースソースは地政学・経済政策・テクノロジー分野に絞る
And 「翌週のカタリスト」セクションを追加（FOMC・経済指標・決算予定）
```

---

## 5. タスクブレークダウン

| ID | タスク | 依存 | Verified |
|----|--------|------|---------|
| T-001 | GitHubパブリックリポジトリ作成 + GitHub Pages有効化（docs/フォルダ指定） | - | [ ] |
| T-002 | Python環境構築（requirements.txt: yfinance, httpx, finnhub-python, google-generativeai, Jinja2） | T-001 | [ ] |
| T-003 | scripts/fetch_market.py 実装（yfinance + Finnhub カレンダー） | T-002 | [ ] |
| T-004 | scripts/fetch_news.py 実装（Finnhub ニュース取得・フィルタリング） | T-002 | [ ] |
| T-005 | scripts/analyze.py 実装（Gemini 2.5 Flash 呼び出し + JSON検証） | T-003, T-004 | [ ] |
| T-006 | Geminiプロンプト設計・品質検証（6ステップ全項目の安定出力を確認） | T-005 | [ ] |
| T-007 | templates/report.html.j2 設計（GS/JPM風デザイン、Chart.js統合） | T-006 | [ ] |
| T-008 | scripts/generate_report.py 実装（Jinja2レンダリング + docs/出力） | T-007 | [ ] |
| T-009 | docs/manifest.json + docs/sw.js 実装（PWA化） | T-008 | [ ] |
| T-010 | docs/index.html 実装（アーカイブ一覧、自動生成） | T-008 | [ ] |
| T-011 | .github/workflows/generate.yml 実装（cron UTC 22:00、Secrets連携） | T-008 | [ ] |
| T-012 | GitHub Secrets 設定 + Actions エンドツーエンド実行テスト | T-011 | [ ] |
| T-013 | Androidホーム画面追加 + オフライン動作確認 | T-012 | [ ] |

---

## 6. 前提条件（ASSUMPTION）

| ID | 前提 | リスク | 対策 |
|----|------|--------|------|
| A-01 | yfinance が東証銘柄（個別）のデータを安定取得できる | HIGH（非公式API） | 失敗時はスキップ + issues.md記録。指数で代替 |
| A-02 | Gemini 2.5 Flash が6ステップ全項目を安定したJSON形式で返す | MEDIUM | T-006でプロンプト検証。失敗時は構造化プロンプトを強化 |
| A-03 | Finnhub無料枠（60コール/分）が全データ取得に十分 | LOW | 1回のレポート生成で消費するのは10コール以下 |
| A-04 | GitHub Actionsが毎日UTC 22:00に安定して起動する | LOW | cron遅延は最大数分。許容範囲内 |
| A-05 | Google AI StudioのGemini APIキーが引き続き無料枠で利用可能 | MEDIUM | 2026年4月時点で安定。制限変更時はGemini 2.5 Flash-Liteに移行 |

---

## 7. 受入基準

以下が全て確認できたときプロジェクト完了とする：

- [ ] GitHub Actionsのcronが手動トリガーで正常実行される（T-012）
- [ ] `docs/reports/YYYY-MM-DD.html` が生成されている（T-012）
- [ ] レポートHTMLに6ステップ分析が全件含まれている（T-012）
- [ ] セクターヒートマップと週次推移チャートが表示される（T-012）
- [ ] AndroidのChromeで「ホーム画面に追加」が選択できる（T-013）
- [ ] ホーム画面アイコンからレポートが開ける（T-013）
- [ ] docs/index.html でアーカイブ一覧が確認できる（T-013）
- [ ] Vercel/Cloudflare等の有料サービスを一切使っていない（T-013）
- [ ] 最終的なGitHub ActionsのワークフローでGemini以外のAPIコストが発生していない（T-013）
