# /audit — ナレッジ陳腐化チェック Skill（月1回推奨）

## トリガー
月1回のメンテナンス / CLAUDE.mdの内容が古いと感じた時 / 新しいAPIバージョンが出た時

## 実行手順

1. `CLAUDE.md` と `.claude/decisions.md` を読む
2. web_search で以下を確認:
   - `gemini-2.5-flash latest version limits 2026`
   - `yfinance latest version 2026`
   - `finnhub api changes 2026`
   - `github actions breaking changes 2026`
3. 以下の形式で監査レポートを出力:

```
## /audit レポート — [日付]

### 陳腐化した情報
| 項目 | 現在の記載 | 最新情報 | 対応要否 |
|------|-----------|---------|--------|

### decisions.md の確認
- D-XX: [変更が必要か確認した決定]

### 推奨アクション
1. [具体的な修正項目]

### 次回 /audit 推奨時期
[日付]
```

4. 変更が必要な場合は `CLAUDE.md` と `decisions.md` を更新する（ユーザー確認後）
