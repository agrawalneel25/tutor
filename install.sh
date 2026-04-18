#!/usr/bin/env bash
# tutor installer  -  one-liner bootstrap for macOS / Linux.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/advitrocks9/tutor/main/install.sh | bash
#
# What it does:
#   1. Installs prerequisites if missing: uv, Node (for claude), git.
#   2. Clones advitrocks9/tutor into ~/tutor (or $1 if given).
#   3. Launches Claude Code with `--dangerously-skip-permissions "/setup"`
#      so the agent runs the whole setup autonomously.
#
# After this runs, the only thing you do by hand is log into Imperial SSO
# when a browser window opens.

set -euo pipefail

REPO_URL="https://github.com/advitrocks9/tutor.git"
DEST="${1:-$HOME/tutor}"

# --- helpers ---
has() { command -v "$1" >/dev/null 2>&1; }
step() { printf "\033[1;36m==>\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m!!\033[0m  %s\n" "$*" >&2; }
die()  { printf "\033[1;31mxx\033[0m  %s\n" "$*" >&2; exit 1; }

# --- platform ---
OS="$(uname -s)"
case "$OS" in
  Darwin) PLATFORM="macos" ;;
  Linux)  PLATFORM="linux" ;;
  *) die "Unsupported OS: $OS. Use install.ps1 on Windows." ;;
esac

step "tutor installer  -  $PLATFORM"

# --- git ---
if ! has git; then
  if [ "$PLATFORM" = "macos" ]; then
    step "Installing Xcode Command Line Tools (provides git)..."
    xcode-select --install || true
    warn "An install prompt may have opened. Finish it, then re-run this script."
    exit 1
  else
    die "Please install git (e.g. sudo apt install git) and rerun."
  fi
fi

# --- uv ---
if ! has uv; then
  step "Installing uv (Python package manager)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
has uv || die "uv install finished but 'uv' is not on PATH. Open a new shell and rerun."

# --- Node + Claude Code ---
if ! has node; then
  step "Installing Node (needed for Claude Code)..."
  if [ "$PLATFORM" = "macos" ]; then
    if has brew; then
      brew install node
    else
      warn "Homebrew not found. Install Node from https://nodejs.org, then rerun."
      exit 1
    fi
  else
    if has apt-get; then
      curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
      sudo apt-get install -y nodejs
    else
      warn "Please install Node 20+ from https://nodejs.org, then rerun."
      exit 1
    fi
  fi
fi

if ! has claude; then
  step "Installing Claude Code (npm -g @anthropic-ai/claude-code)..."
  npm install -g @anthropic-ai/claude-code
fi
has claude || die "Claude Code install finished but 'claude' is not on PATH. Open a new shell and rerun."

# --- clone ---
if [ -d "$DEST/.git" ]; then
  step "Repo already at $DEST, pulling latest..."
  git -C "$DEST" pull --ff-only || warn "pull failed; continuing with current state"
elif [ -d "$DEST" ]; then
  die "$DEST exists but is not a git repo. Move or delete it, then rerun."
else
  step "Cloning tutor into $DEST..."
  git clone "$REPO_URL" "$DEST"
fi

cd "$DEST"

# --- launch Claude Code into /setup ---
step "Launching Claude Code. The agent will drive setup from here."
echo
echo "   If a browser window opens, log in with your Imperial account."
echo "   One login covers both Panopto and Blackboard."
echo
exec claude --dangerously-skip-permissions "/setup"
