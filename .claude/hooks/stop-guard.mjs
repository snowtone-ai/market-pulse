#!/usr/bin/env node
// stop-guard.mjs — Stop hook（Windows stdin バグ対策必須）
// Claude 応答完了時に自己検証を促す additionalContext を注入する

const TIMEOUT_MS = 3000;
const t = setTimeout(() => {
  // Windows stdin バグ: stdin が来ない場合は素通し
  process.exit(0);
}, TIMEOUT_MS);

let buf = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (buf += c));
process.stdin.on("end", () => {
  clearTimeout(t);

  // stdin が空の場合も素通し（Windows バグ対策）
  if (!buf.trim()) { process.exit(0); }

  try {
    // 完了確認チェックリスト注入
    const checklist = [
      "=== 完了前 自己検証チェック ===",
      "- state.md のタスクステータスを更新したか？",
      "- .env.local のキーをコードにハードコードしていないか？",
      "- gemini-2.0-flash（廃止）ではなく gemini-2.5-flash を使っているか？",
      "- 新しい .py ファイルに型ヒントと try/except を書いたか？",
      "- decisions.md と矛盾する実装をしていないか？",
    ].join("\n");

    process.stdout.write(JSON.stringify({ additionalContext: checklist }));
    process.exit(0);
  } catch (e) {
    process.exit(0);
  }
});
