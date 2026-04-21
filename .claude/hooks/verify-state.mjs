#!/usr/bin/env node
// verify-state.mjs — SessionStart (startup|resume|clear)
// state.md を読み additionalContext として注入する

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const TIMEOUT_MS = 3000;
const t = setTimeout(() => process.exit(0), TIMEOUT_MS);

let buf = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (buf += c));
process.stdin.on("end", () => {
  clearTimeout(t);

  try {
    const statePath = join(process.cwd(), ".claude", "state.md");
    const decisionsPath = join(process.cwd(), ".claude", "decisions.md");

    const state = existsSync(statePath)
      ? readFileSync(statePath, "utf8")
      : "state.md が存在しません。T-001 から開始してください。";

    const decisions = existsSync(decisionsPath)
      ? readFileSync(decisionsPath, "utf8").split("\n").slice(0, 20).join("\n")
      : "";

    const context = [
      "=== セッション再開: state.md ===",
      state,
      decisions ? "\n=== decisions.md（要約）===\n" + decisions : "",
      "\n鉄則: state.mdとコードが矛盾した場合、実コードが正。完了済みタスクを再実装しない。",
    ]
      .filter(Boolean)
      .join("\n");

    const output = JSON.stringify({ additionalContext: context });
    process.stdout.write(output);
    process.exit(0);
  } catch (e) {
    process.stderr.write("verify-state: " + e.message + "\n");
    process.exit(0); // エラーでもブロックしない
  }
});
