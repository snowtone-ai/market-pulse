#!/usr/bin/env node
// block-dangerous.mjs — PreToolUse (Bash)
// 危険なコマンドを exit 2 でブロックする

const TIMEOUT_MS = 3000;
const t = setTimeout(() => process.exit(0), TIMEOUT_MS);

const BLOCKED_PATTERNS = [
  /rm\s+-rf\s+[\/\*]/,
  /Remove-Item\s+-Recurse\s+-Force\s+[\/\*]/i,
  /git\s+push\s+--force/,
  /git\s+push\s+-f\b/,
  /git\s+reset\s+--hard/,
  /git\s+clean\s+-fd/,
  /sudo\s+/,
  />\s*\/dev\/sda/,
  /mkfs\./,
  /curl\s+.*\|\s*sh/,   // curl pipe to shell
  /wget\s+.*\|\s*sh/,
];

let buf = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (buf += c));
process.stdin.on("end", () => {
  clearTimeout(t);
  if (!buf.trim()) { process.exit(0); }

  try {
    const data = JSON.parse(buf);
    const command = data?.tool_input?.command || "";

    for (const pattern of BLOCKED_PATTERNS) {
      if (pattern.test(command)) {
        process.stderr.write(`block-dangerous: ブロック: ${command.slice(0, 80)}\n`);
        process.stdout.write(
          JSON.stringify({
            decision: "block",
            reason: `危険なコマンドを検出しました: ${command.slice(0, 80)}\n別のアプローチを使ってください。`,
          })
        );
        process.exit(2);
      }
    }

    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
