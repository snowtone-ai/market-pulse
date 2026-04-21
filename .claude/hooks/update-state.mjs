#!/usr/bin/env node
// update-state.mjs — PostToolUse (Write|Edit|MultiEdit) async
// state.md の Activity Log に書き込み記録を追記する

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
    const filePath =
      data?.tool_input?.file_path ||
      data?.tool_input?.path ||
      data?.tool_response?.file_path;

    if (!filePath) { process.exit(0); }

    // .claude/ 内のファイルは無視（無限ループ防止）
    if (filePath.includes(".claude")) { process.exit(0); }

    const statePath = join(process.cwd(), ".claude", "state.md");
    if (!existsSync(statePath)) { process.exit(0); }

    const now = new Date().toISOString().slice(0, 16).replace("T", " ");
    const logLine = `| ${now} | ${filePath} | 書き込み |`;

    let content = readFileSync(statePath, "utf8");
    // Activity Log セクションの末尾に追記
    if (content.includes("## Activity Log")) {
      content = content.trimEnd() + "\n" + logLine + "\n";
    } else {
      content += "\n## Activity Log\n\n| 日時 | ファイル | アクション |\n|------|---------|----------|\n" + logLine + "\n";
    }

    writeFileSync(statePath, content, "utf8");
    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
