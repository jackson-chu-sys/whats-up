#!/bin/bash
# gen-linkedin.sh — 从英文周刊生成 LinkedIn 发布内容
# Usage: ./scripts/gen-linkedin.sh 2026-W24

set -e
cd "$(dirname "$0")/.."

WEEK="${1:-2026-W24}"
EN_FILE="issues/${WEEK}/index.en.md"
GITHUB_URL="https://jackson-chu-sys.github.io/whats-up/issues/${WEEK}/"

if [ ! -f "$EN_FILE" ]; then
  echo "❌ 找不到 $EN_FILE (请先生成英文版)"
  exit 1
fi

echo "📝 正在从 $EN_FILE 生成 LinkedIn 内容..."

SUMMARY=$(python3 -c "
import re, sys
with open('$EN_FILE') as f:
    text = f.read()

lines = text.split('\n')
sections = []
current_section = ''
current_content = []
max_chars = 2500

for line in lines:
    if re.match(r'^# (🔥|🏦|🌐|🤖|💻|🌱|🏥)', line) or line.startswith('# Headlines') or line.startswith('# Finance') or line.startswith('# International') or line.startswith('# Artificial') or line.startswith('# Tech') or line.startswith('# Environment') or line.startswith('# Healthcare'):
        if current_section and current_content:
            content = ' '.join(current_content[:2]).strip()[:200]
            sections.append(f'{current_section}\n{content}\n')
        current_section = line
        current_content = []
    elif line.startswith('## ▶') or line.startswith('## 1️⃣') or line.startswith('## 2️⃣') or line.startswith('## 3️⃣'):
        if current_content:
            content = ' '.join(current_content[:2]).strip()[:200]
            sections.append(f'{current_section}\n{content}\n')
        current_section = line
        current_content = []
    elif line.strip() and not line.startswith('>') and not line.startswith('🔗') and not line.startswith('---'):
        current_content.append(line.strip())

# Build output
title_line = ''
for line in lines:
    if line.startswith('# ') and ('Vol' in line or 'Weekly' in line or 'what' in line.lower()):
        title_line = line.strip('# ')
        break

if not title_line:
    title_line = 'what\\'s Up! Global Weekly Digest'

output = f'🟣 {title_line}\n'
output += 'Curated global digest covering this week in tech, AI, markets & world affairs.\n\n'

for s in sections[:6]:
    short = s[:300]
    output += short + '\n'

output += '\n—\n'
output += f'📖 Full issue: $GITHUB_URL\n'
output += '#WeeklyDigest #Tech #AI #Markets #GlobalNews #WhatsUp'

print(output.strip())
")

echo "──────────────────────────────────────"
echo "$SUMMARY"
echo "──────────────────────────────────────"
echo ""

# Copy to clipboard
if command -v xclip &>/dev/null; then
  echo "$SUMMARY" | xclip -selection clipboard
  echo "✅ 内容已复制到剪贴板！"
elif command -v pbcopy &>/dev/null; then
  echo "$SUMMARY" | pbcopy
  echo "✅ 内容已复制到剪贴板！"
else
  echo "⚠️ 未找到剪贴板工具 (xclip/pbcopy)，请手动复制上方内容"
fi

echo ""
echo "🔗 原文链接: $GITHUB_URL"
echo ""
echo "🌐 发布到 LinkedIn:"
echo "   手动操作: 1. 打开 https://www.linkedin.com/feed/"
echo "             2. 粘贴内容"
echo "             3. 点击 Post"
