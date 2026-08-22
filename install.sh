#!/usr/bin/env bash
# Deep Market Research Skill — 跨平台一键安装脚本
# 检测本机已安装的 Agent 平台，将 skill 复制到对应 skills/ 目录。
set -euo pipefail

SKILL_DIR="deep-market-research"
SRC="$(cd "$(dirname "$0")" && pwd)"

# 要复制的文件（排除 .git 与安装脚本自身；scripts/ 承载机检脚本，benchmarks/ 为基准包）
FILES=(SKILL.md README.md README_EN.md references assets benchmarks scripts LICENSE CONTRIBUTING.md .gitignore)

# 各平台 skills 根目录（存在的才安装）
TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.trae/skills"
  "$HOME/.trae-cn/skills"
  "$HOME/.qoder/skills"
  "$HOME/.workbuddy/skills"
)

SKILL_VERSION="$(grep -m1 -E '^version:[[:space:]]*"?[0-9.]+' "$SRC/SKILL.md" 2>/dev/null | sed -E 's/.*version:[[:space:]]*"?([0-9.]+).*/\1/')"
echo "Installing deep-market-research v${SKILL_VERSION:-unknown}"

installed=0
for base in "${TARGETS[@]}"; do
  if [ -d "$base" ]; then
    dest="$base/$SKILL_DIR"
    mkdir -p "$dest"
    for f in "${FILES[@]}"; do
      [ -e "$SRC/$f" ] && cp -R "$SRC/$f" "$dest/"
    done
    # Never ship Python bytecode caches to skill directories.
    find "$dest" -type d -name "__pycache__" -exec rm -rf {} +
    echo "Installed to $dest"
    installed=$((installed + 1))
  fi
done

if [ "$installed" -eq 0 ]; then
  echo "No supported agent skills directory found on this machine."
  echo "  Manually copy this folder to your agent's skills directory, e.g.:"
  echo "    cp -r $SRC \"\$HOME/.claude/skills/$SKILL_DIR\""
  echo "  Supported: ~/.claude ~/.codex ~/.trae ~/.trae-cn ~/.qoder ~/.workbuddy"
  exit 1
fi

echo ""
echo "Done. Restart your agent (or run /skill refresh) to load 'deep-market-research'."