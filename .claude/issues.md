# issues.md — エラー自動記録
# 書き込み: PostToolUseFailure Hook が自動追記
# 読み取り: /ev 実行時の入力

| 日時 | タスク | エラー内容 | 試みた対策 | 状態 |
|------|--------|-----------|----------|------|
| 2026-04-21 07:52 | C:\Users\chidj\dev\market-pulse\.github\workflows\daily-report.yml | File does not exist. Note: your current working directory is C:\Users\chidj\dev\market-pulse. | - | open |
| 2026-04-21 13:06 | gh pr list | Exit code 1 HTTP 401: Bad credentials (https://api.github.com/graphql) Try authenticating with:  gh auth login | - | open |
| 2026-04-21 13:06 | gh pr list | Exit code 1 HTTP 401: Bad credentials (https://api.github.com/graphql) Try authenticating with:  gh auth login | - | open |
| 2026-04-22 11:13 | git push origin main | Exit code 1 To https://github.com/snowtone-ai/market-pulse.git  ! [rejected]        main -> main (fetch first) error: fa | - | open |
| 2026-04-22 11:13 | git pull --rebase origin main | Exit code 128 error: cannot pull with rebase: You have unstaged changes. error: Please commit or stash them. | - | open |
| 2026-04-22 11:14 | git merge origin/main -m "merge: integrate Actions-pushed 2026-04-22 report" | Exit code 1 Auto-merging docs/index.html CONFLICT (content): Merge conflict in docs/index.html Automatic merge failed; f | - | open |
| 2026-04-22 11:27 | python scripts/generate_report.py --date 2026-04-22 2>&1 | Exit code 1 C:\Users\chidj\dev\market-pulse\scripts\analyze.py:8: FutureWarning:   All support for the `google.generat | - | open |
| 2026-04-22 11:30 | StopFailure | APIエラー: unknown | - | open |
| 2026-04-23 01:21 | C:\Users\chidj\.claude\issues.md | File does not exist. Note: your current working directory is C:\Users\chidj\dev\market-pulse. | - | open |
| 2026-04-23 01:23 | cd /d C:\Users\chidj\dev\market-pulse && git add -A && git commit -m "refactor: migrate to new Gemini SDK (google-genai v0.x), remove watchlist_highlights feature" | Exit code 1 /usr/bin/bash: line 1: cd: too many arguments | - | open |
