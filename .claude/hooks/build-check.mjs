#!/usr/bin/env node
// build-check.mjs — PostToolUse (Write|Edit|MultiEdit)
// .py ファイルの構文チェック（python -m py_compile）

import { spawnSync, existsSync } from "node:child_process";

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

    if (!filePath || !filePath.endsWith(".py")) {
      process.exit(0);
    }

    const isWin = process.platform === "win32";
    const venvPython = isWin
      ? ".venv\\Scripts\\python.exe"
      : ".venv/bin/python";
    const python = require("node:fs").existsSync(venvPython) ? venvPython : "python";

    const result = spawnSync(python, ["-m", "py_compile", filePath], {
      shell: isWin,
      encoding: "utf8",
    });

    if (result.status !== 0) {
      // exit 2 でClaudeにブロックを通知（構文エラーを自動修正させる）
      process.stderr.write(
        `build-check: 構文エラー in ${filePath}\n${result.stderr}\n`
      );
      process.stdout.write(
        JSON.stringify({
          decision: "block",
          reason: `Python構文エラーが検出されました: ${filePath}\n${result.stderr}`,
        })
      );
      process.exit(2);
    }

    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
