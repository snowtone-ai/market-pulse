# bootstrap.ps1 — market-pulse 環境初期化
# 実行: PowerShell（管理者不要）でプロジェクトフォルダから .\bootstrap.ps1
# 期待される完了メッセージ: "=== bootstrap 完了 ==="

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSNativeCommandUseErrorActionPreference = $true
}

function Write-Step($n, $total, $msg) { Write-Host "[$n/$total] $msg" -ForegroundColor Yellow }
function Write-OK($msg)   { Write-Host "  OK: $msg"   -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "  FAIL: $msg"  -ForegroundColor Red; exit 1 }

$total = 8

# ============================================================
# 1. ディレクトリ構造
# ============================================================
Write-Step 1 $total "ディレクトリ構造を作成"
$dirs = @(
    ".claude", ".claude\hooks", ".claude\agents", ".claude\skills",
    ".github", ".github\workflows",
    "scripts", "templates", "docs", "docs\reports"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}
Write-OK "全ディレクトリ作成完了"

# ============================================================
# 2. Python バージョン確認（3.12+ 推奨）
# ============================================================
Write-Step 2 $total "Python バージョン確認"
$pyVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) { Write-Fail "Python が見つかりません。https://www.python.org からインストールしてください。" }
Write-OK $pyVersion

# ============================================================
# 3. 仮想環境作成（.venv）
# ============================================================
Write-Step 3 $total "仮想環境を作成 (.venv)"
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { Write-Fail "venv 作成失敗" }
    Write-OK ".venv 作成完了"
} else {
    Write-OK ".venv は既に存在します（スキップ）"
}

# ============================================================
# 4. 依存パッケージインストール
# ============================================================
Write-Step 4 $total "依存パッケージをインストール"
$pip = ".venv\Scripts\pip.exe"
if (-not (Test-Path $pip)) { Write-Fail ".venv\Scripts\pip.exe が見つかりません" }

$requirements = @(
    "yfinance>=0.2",
    "httpx>=0.27",
    "finnhub-python>=2.4",
    "google-generativeai>=0.8",
    "Jinja2>=3.1",
    "python-dotenv>=1.0",
    "black>=24.0"
)

$reqFile = Join-Path (Get-Location).Path "requirements.txt"
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($reqFile, ($requirements -join "`n"), $utf8NoBom)

& $pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) { Write-Fail "pip install 失敗" }
Write-OK "全パッケージインストール完了"

# ============================================================
# 5. .env.local 作成（未存在の場合のみ）
# ============================================================
Write-Step 5 $total ".env.local を作成"
if (-not (Test-Path ".env.local")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env.local"
        Write-OK ".env.local を .env.example からコピーしました"
        Write-Host "  => .env.local を開いて GEMINI_API_KEY と FINNHUB_API_KEY を記入してください" -ForegroundColor Cyan
    } else {
        Write-Fail ".env.example が見つかりません。CLAUDE.md / vision.md と同じフォルダで実行しているか確認してください"
    }
} else {
    Write-OK ".env.local は既に存在します（スキップ）"
}

# ============================================================
# 6. .gitignore 作成
# ============================================================
Write-Step 6 $total ".gitignore を設定"
$gitignore = @"
.venv/
.env.local
.env
*.pyc
__pycache__/
.claude/settings.local.json
"@
$giPath = Join-Path (Get-Location).Path ".gitignore"
[System.IO.File]::WriteAllText($giPath, $gitignore, $utf8NoBom)
Write-OK ".gitignore 作成完了"

# ============================================================
# 7. Node.js 確認（hooks用）
# ============================================================
Write-Step 7 $total "Node.js バージョン確認（Hooks用）"
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARNING: Node.js が見つかりません。Claude Code Hooks には Node.js が必要です。" -ForegroundColor Magenta
    Write-Host "  インストール先: https://nodejs.org (22.x 以上推奨)" -ForegroundColor Magenta
} else {
    Write-OK "Node.js $nodeVersion"
}

# ============================================================
# 8. Git リポジトリ初期化
# ============================================================
Write-Step 8 $total "Git リポジトリを初期化"
if (-not (Test-Path ".git")) {
    git init
    if ($LASTEXITCODE -ne 0) { Write-Fail "git init 失敗" }

    $mainExists = git rev-parse --verify main 2>$null
    if ($LASTEXITCODE -ne 0) {
        git checkout -b main
    }
    Write-OK "Git リポジトリ初期化完了（ブランチ: main）"
} else {
    Write-OK "Git リポジトリは既に存在します（スキップ）"
}

# ============================================================
# 完了
# ============================================================
Write-Host ""
Write-Host "=== bootstrap 完了 ===" -ForegroundColor Green
Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Cyan
Write-Host "  1. .env.local を開いて GEMINI_API_KEY と FINNHUB_API_KEY を記入"
Write-Host "  2. GitHubでリポジトリを作成（パブリック）し git remote add origin <URL>"
Write-Host "  3. GitHub リポジトリの Settings > Pages > Source を 'docs/' フォルダに設定"
Write-Host "  4. GitHub Secrets に GEMINI_API_KEY と FINNHUB_API_KEY を登録"
Write-Host "  5. claude を実行して Claude Code を起動"
Write-Host ""
