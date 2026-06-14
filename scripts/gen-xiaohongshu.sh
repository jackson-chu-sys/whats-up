#!/bin/bash
# gen-xiaohongshu.sh — 从周刊中文稿生成小红书发布内容 (Jekyll URL)
# Usage: ./scripts/gen-xiaohongshu.sh 2026-W24

set -e
cd "$(dirname "$0")/.."

WEEK="${1:-2026-W24}"
CN_FILE="issues/${WEEK}/index.cn.md"

# Derive Jekyll URL from issue year/week
YEAR=$(echo "$WEEK" | cut -d'-' -f1)
WNUM=$(echo "$WEEK" | cut -d'W' -f2)
# Find the actual post file
POST_FILE=$(ls _posts/zh/*.md 2>/dev/null | head -1)
if [ -z "$POST_FILE" ] && [ ! -f "$CN_FILE" ]; then
  echo "❌ 找不到中文周刊文件"
  exit 1
fi

# Determine GitHub Pages URL
if [ -n "$POST_FILE" ]; then
  POST_SLUG=$(basename "$POST_FILE" .md)
  GITHUB_URL="https://jackson-chu-sys.github.io/whats-up/zh/${POST_SLUG}.html"
else
  GITHUB_URL="https://jackson-chu-sys.github.io/whats-up"
fi

SRC_FILE="${POST_FILE:-$CN_FILE}"

echo "📝 正在生成小红书内容..."

SUMMARY=$(python3 -c "
import re
with open('$SRC_FILE') as f:
    text = f.read()

# Skip Jekyll frontmatter
text = re.sub(r'^---.*?---\n', '', text, flags=re.DOTALL)

lines = text.split('\n')
sections = []
current_section = ''
current_content = []
max_chars = 900

for line in lines:
    if re.match(r'^# (🔥|🏦|🌐|🤖|💻|🌱|🏥)', line):
        if current_section and current_content:
            content = ' '.join(current_content[:3]).strip()[:200]
            sections.append(f'{current_section}\n{content}\n')
        current_section = line
        current_content = []
    elif line.startswith('## ') and ('▶' in line or '1️⃣' in line or '2️⃣' in line or '3️⃣' in line):
        pass  # subsection header, skip
    elif line.strip() and not line.startswith('>') and not line.startswith('🔗') and not line.startswith('---') and not line.startswith('⚠️'):
        current_content.append(line.strip())

if current_section and current_content:
    content = ' '.join(current_content[:3]).strip()[:200]
    sections.append(f'{current_section}\n{content}\n')

# Extract title
title = ''
for line in lines:
    if line.startswith('# ') and 'Vol' in line:
        title = line.strip('# ').strip()
        break

output = f'🟣 {title}\n\n' if title else '🟣 what\\'s Up! 全球热点周刊\n\n'
for s in sections[:5]:
    short = s[:180]
    output += short + '\n\n'
    if len(output) > 850:
        break

output += '—\n'
output += f'🔗 全文阅读: $GITHUB_URL\n'
output += '#全球热点 #每周简报 #时事 #AI #科技'

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
  echo "⚠️ 未找到剪贴板工具，请手动复制上方内容"
fi

echo ""
echo "🔗 原文链接: $GITHUB_URL"
echo ""
echo "📱 发布到小红书:"
echo "   1. 打开 https://creator.xiaohongshu.com/publish/publish"
echo "   2. Cmd/Ctrl+V 粘贴内容"
echo "   3. 上传封面图 (assets/covers/${WEEK}.png)"
echo "   4. 点击发布"
