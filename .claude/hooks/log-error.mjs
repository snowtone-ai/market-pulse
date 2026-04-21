#!/usr/bin/env node
// log-error.mjs — PostToolUseFailure async
// エラーを .claude/issues.md に自動追記する

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const TIMEOUT_MS = 3000;
const t = setTimeout(() => process.exit(0), TIMEOUT_MS);

let buf = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (buf += c));
process.stdin.on("end", () => {
  clearTimeout(t);
  if (!buf.trim()) { process.exit(0); }

  try {
    const data = JSON.parse(buf);
    const tool = data?.tool || "unknown";
    const error = data?.tool_output || data?.error || "（エラー詳細なし）";
    const filePath = data?.tool_input?.file_path || data?.tool_input?.command || "";

    const now = new Date().toISOString().slice(0, 16).replace("T", " ");
    const logLine = `| ${now} | ${filePath || tool} | ${String(error).slice(0, 120).replace(/\n/g, " ")} | - | open |`;

    const issuesPath = join(process.cwd(), ".claude", "issues.md");
    let content = existsSync(issuesPath)
      ? readFileSync(issuesPath, "utf8")
      : "# issues.md\n\n| 日時 | タスク | エラー内容 | 試みた対策 | 状態 |\n|------|--------|-----------|----------|------|\n";

    content = content.trimEnd() + "\n" + logLine + "\n";
    writeFileSync(issuesPath, content, "utf8");
    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
