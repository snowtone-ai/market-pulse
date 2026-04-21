#!/usr/bin/env node
// format-file.mjs — PostToolUse (Write|Edit|MultiEdit) async
// .py ファイルに black フォーマットを適用する

import { spawnSync } from "node:child_process";

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
    const venvBlack = isWin
      ? ".venv\\Scripts\\black.exe"
      : ".venv/bin/black";

    // venv の black を優先、なければグローバル
    const cmd = require("node:fs").existsSync(venvBlack) ? venvBlack : "black";
    const result = spawnSync(cmd, [filePath], {
      shell: isWin,
      encoding: "utf8",
    });

    if (result.error) {
      process.stderr.write("format-file: black not found, skip\n");
    }
    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
