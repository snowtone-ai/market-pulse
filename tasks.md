# tasks.md -- pm-zero v9.4 Execution Ledger

## Goal Binding
- Vision source: docs/vision.md
- Active goal: Refactor Market Pulse internals without changing product behavior, generated reports, or external interfaces.
- Planning owner: Codex CLI
- Implementation owner: Codex CLI
- Review owner: Codex CLI self-audit

## Status Vocabulary
- proposed: idea exists, not ready
- ready: owner, dependencies, write scope, acceptance, verification, and expected evidence are clear
- doing: one owner is actively working
- blocked: needs decision, dependency, credential, environment, or human action
- review: implementation complete, review pending
- done: accepted by reviewer
- verified: evidence recorded

## Parallelization Rules
- Coordinator owns tasks.md.
- Worker agents own only their assigned Write Scope.
- Parallel implementation requires disjoint Write Scopes or isolated worktrees.
- If two tasks need the same file, serialize them.
- Subagents return reports; coordinator updates tasks.md.

## Tasks
| ID | Status | Owner | Depends On | Write Scope | Acceptance | Verification | Evidence |
|---|---|---|---|---|---|---|---|
| T001 | verified | Codex CLI | none | AGENTS.md, CLAUDE.md, HANDOFF-JA.md, tasks.md, docs/vision.md, docs/state.md, docs/decisions.md, docs/issues.md, docs/repo-map.md, scripts/setup.mjs, scripts/verify.mjs, .claude/settings.json, .gitignore | pm-zero v9.4 source-of-truth files exist, old project-local hook/MCP scaffolds are removed, and product report generation code is untouched | git diff --check; node scripts/verify.mjs | 2026-05-17: node scripts/verify.mjs passed; git diff --check passed before commit. |
| T002 | verified | Codex CLI | T001 | scripts/fetch_news.py, tasks.md | News scoring keeps the same weights and matching behavior while keyword groups are named and easier to maintain | node scripts/verify.mjs | 2026-05-17: verify passed; compileall recompiled scripts/fetch_news.py. |
| T003 | verified | Codex CLI | none | .github/workflows/generate.yml, tasks.md, docs/state.md | 自動配信ジョブが実行されず、docs/ への自動コミット配信が停止している | node scripts/verify.mjs | 2026-05-19: generate workflow に `if: false` を設定し配信停止。verify passed. |

## Blockers
| ID | Task | Blocker | Needed decision | Owner |
|---|---|---|---|---|

## Review Notes
| Task | Reviewer | Result | Follow-up |
|---|---|---|---|
