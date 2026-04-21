#!/usr/bin/env node
// resume-state.mjs — SessionStart (compact) コンパクション後に state 再注入

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
    const state = existsSync(statePath)
      ? readFileSync(statePath, "utf8")
      : "state.md なし";

    process.stdout.write(
      JSON.stringify({
        additionalContext:
          "=== コンパクション後 state.md 再注入 ===\n" + state,
      })
    );
    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
