# decisions.md

## D-001: pm-zero v9.4 Lean Task Ledger alignment

- Date: 2026-05-16
- Decision: Keep Market Pulse project memory in AGENTS.md, tasks.md, docs/state.md, docs/repo-map.md, docs/decisions.md, and docs/issues.md.
- Rationale: The root docs/ directory is also the GitHub Pages output directory, but small pm-zero Markdown files are safe as repository metadata and do not alter existing generated HTML reports.
- Consequence: Project-local Claude hooks, agents, skills, state snapshots, and MCP config are removed unless a future task records a concrete project-specific need.
