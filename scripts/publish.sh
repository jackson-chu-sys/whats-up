#!/bin/bash
# publish.sh — 一键推送到 GitHub Pages (Jekyll)
# Usage: ./scripts/publish.sh "commit message"

set -e
cd "$(dirname "$0")/.."

MSG="${1:-publish: weekly update}"

echo "📦 Adding files..."
git add -A

echo "💬 Commit: $MSG"
git commit -m "$MSG" || { echo "⚠️ nothing to commit"; exit 0; }

echo "🚀 Pushing to GitHub..."
no_proxy=github.com git push origin main

echo ""
echo "✅ 已推送！GitHub Pages 正在自动构建..."
echo "🔗 1-2 分钟后访问: https://jackson-chu-sys.github.io/whats-up"
