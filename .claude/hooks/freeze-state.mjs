#!/usr/bin/env node
// freeze-state.mjs — PreCompact (auto|manual) コンパクション前に state を固定化

import { readFileSync, writeFileSync, existsSync } from "node:fs";
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
    const snapshotPath = join(process.cwd(), ".claude", "state.snapshot.md");

    if (existsSync(statePath)) {
      const content = readFileSync(statePath, "utf8");
      writeFileSync(snapshotPath, content, "utf8");
    }

    process.stdout.write(
      JSON.stringify({
        additionalContext:
          "state.md をスナップショットに保存しました。コンパクション後は resume-state.mjs が再注入します。",
      })
    );
    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
