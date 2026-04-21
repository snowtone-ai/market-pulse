#!/usr/bin/env node
// stopfailure-notify.mjs — StopFailure (rate_limit|server_error)
// API エラー発生時にコンソールへ通知し issues.md に記録する

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const TIMEOUT_MS = 3000;
const t = setTimeout(() => process.exit(0), TIMEOUT_MS);

let buf = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (buf += c));
process.stdin.on("end", () => {
  clearTimeout(t);

  const reason = (() => {
    if (!buf.trim()) return "unknown";
    try { return JSON.parse(buf)?.stop_reason || "unknown"; }
    catch { return "unknown"; }
  })();

  const messages = {
    rate_limit:   "レート制限に達しました。数分待ってから再試行してください。",
    server_error: "Anthropic サーバーエラーが発生しました。ステータス: https://status.anthropic.com",
  };

  const msg = messages[reason] || `APIエラー: ${reason}`;
  process.stderr.write(`\n[StopFailure] ${msg}\n`);

  try {
    const now = new Date().toISOString().slice(0, 16).replace("T", " ");
    const issuesPath = join(process.cwd(), ".claude", "issues.md");
    let content = existsSync(issuesPath)
      ? readFileSync(issuesPath, "utf8")
      : "# issues.md\n\n| 日時 | タスク | エラー内容 | 試みた対策 | 状態 |\n|------|--------|-----------|----------|------|\n";
    content = content.trimEnd() + `\n| ${now} | StopFailure | ${msg} | - | open |\n`;
    writeFileSync(issuesPath, content, "utf8");
  } catch {}

  process.exit(0);
});
