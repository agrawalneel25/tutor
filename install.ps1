# tutor installer  -  one-liner bootstrap for Windows (PowerShell).
#
# Usage (PowerShell):
#   iwr -useb https://raw.githubusercontent.com/advitrocks9/tutor/main/install.ps1 | iex
#
# What it does:
#   1. Installs prerequisites if missing: uv, Node (for claude), git.
#   2. Clones advitrocks9/tutor into $HOME\tutor.
#   3. Launches Claude Code with `--dangerously-skip-permissions "/setup"`.
#
# You'll only need to interact once: when a browser window opens for Imperial SSO.

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/advitrocks9/tutor.git"
$Dest    = Join-Path $HOME "tutor"

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Warn($msg) { Write-Host "!!  $msg" -ForegroundColor Yellow }
function Die($msg)  { Write-Host "xx  $msg" -ForegroundColor Red; exit 1 }
function Has($cmd)  { $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue) }

Step "tutor installer  -  Windows"

# --- git ---
if (-not (Has "git")) {
    Step "Installing git via winget..."
    if (-not (Has "winget")) { Die "winget not found. Install git from https://git-scm.com/download/win, then rerun." }
    winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
}

# --- uv ---
if (-not (Has "uv")) {
    Step "Installing uv (Python package manager)..."
    iwr -useb https://astral.sh/uv/install.ps1 | iex
    $env:Path = "$HOME\.local\bin;$HOME\.cargo\bin;$env:Path"
}
if (-not (Has "uv")) { Die "uv install finished but 'uv' is not on PATH. Open a new PowerShell and rerun." }

# --- Node ---
if (-not (Has "node")) {
    Step "Installing Node.js via winget..."
    if (-not (Has "winget")) { Die "winget not found. Install Node 20+ from https://nodejs.org, then rerun." }
    winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements
    $env:Path = "$env:ProgramFiles\nodejs;$env:Path"
}

# --- Claude Code ---
if (-not (Has "claude")) {
    Step "Installing Claude Code (npm -g @anthropic-ai/claude-code)..."
    npm install -g "@anthropic-ai/claude-code"
}
if (-not (Has "claude")) { Die "Claude Code install finished but 'claude' is not on PATH. Open a new PowerShell and rerun." }

# --- clone ---
if (Test-Path (Join-Path $Dest ".git")) {
    Step "Repo already at $Dest, pulling latest..."
    git -C $Dest pull --ff-only
} elseif (Test-Path $Dest) {
    Die "$Dest exists but is not a git repo. Move or delete it, then rerun."
} else {
    Step "Cloning tutor into $Dest..."
    git clone $RepoUrl $Dest
}

Set-Location $Dest

# --- launch Claude Code into /setup ---
Step "Launching Claude Code. The agent will drive setup from here."
Write-Host ""
Write-Host "   If a browser window opens, log in with your Imperial account."
Write-Host "   One login covers both Panopto and Blackboard."
Write-Host ""
claude --dangerously-skip-permissions "/setup"
