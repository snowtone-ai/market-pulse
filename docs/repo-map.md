# repo-map.md -- pm-zero v9.4 Repository Map

## Read Policy
- Session start: read Summary only.
- Before editing: read the section for the target area when target files are unclear.
- When navigation is unclear: read Entry Points and Directory Map.
- After structural changes: update only the affected section.

## Summary
- App type: Python market-report generator with GitHub Pages PWA output.
- Main runtime: Python 3.12 scripts, Jinja2, yfinance/Finnhub/Gemini.
- Package manager: pip via requirements.txt.
- Primary source directory: scripts/.
- Public output directory: docs/.
- Main entry point: scripts/generate_report.py.
- Verification command: node scripts/verify.mjs.

## Directory Map
| Path | Purpose | Edit Frequency | Notes |
|---|---|---|---|
| scripts/ | Data fetch, analysis, report generation | high | Product automation. |
| templates/ | Jinja report template | medium | Product output shape. |
| docs/ | GitHub Pages output plus pm-zero metadata | medium | Do not overwrite generated reports casually. |
| docs/reports/ | Generated daily reports | generated | Commit only intentional published reports. |
| .github/workflows/ | Scheduled generation workflow | medium | Secrets live in GitHub Actions, not files. |

## Entry Points
| Area | File | Purpose |
|---|---|---|
| Generate report | scripts/generate_report.py | Orchestrates data, analysis, and HTML output. |
| Market data | scripts/fetch_market.py | Price and macro data fetch. |
| News | scripts/fetch_news.py | News fetch and scoring. |
| Analysis | scripts/analyze.py | Gemini-backed analysis. |
| Verification | scripts/verify.mjs | Metadata and Python syntax checks. |

## Common Workflows
| Workflow | Read First | Edit Usually | Verify |
|---|---|---|---|
| Data source change | docs/vision.md | scripts/fetch_*.py | python -m compileall scripts |
| Report layout | templates/report.html.j2 | templates/, docs/index.html | node scripts/verify.mjs |
| pm-zero docs | AGENTS.md | tasks.md, docs/*.md, scripts/verify.mjs | git diff --check |

## Generated / External Files
| Path | Rule |
|---|---|
| .venv/, __pycache__/ | Ignore. |
| docs/reports/*.html | Generated reports; commit only when intentionally published. |
| .env, .env.local, .env.*.local | Ignore secrets. |
| *.log, logs/ | Ignore. |

## Update Rules
- Keep Summary under 20 lines.
- Keep each directory note concrete.
- Move rationale to docs/decisions.md.
