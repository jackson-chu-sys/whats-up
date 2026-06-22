#!/bin/bash
# gen-linkedin.sh — 从周刊英文稿生成 LinkedIn 发布内容 (Jekyll URL)
# Usage: ./scripts/gen-linkedin.sh 2026-W24

set -e
cd "$(dirname "$0")/.."

WEEK="${1:-2026-W24}"
EN_FILE="issues/${WEEK}/index.en.md"

# Check _posts/en/ first, fallback to issues/
POST_FILE=$(ls _posts/en/*.md 2>/dev/null | head -1)
if [ -n "$POST_FILE" ]; then
  POST_SLUG=$(basename "$POST_FILE" .md)
  GITHUB_URL="https://jackson-chu-sys.github.io/whats-up/en/${POST_SLUG}.html"
  SRC_FILE="$POST_FILE"
elif [ -f "$EN_FILE" ]; then
  GITHUB_URL="https://jackson-chu-sys.github.io/whats-up"
  SRC_FILE="$EN_FILE"
else
  echo "❌ 找不到英文周刊文件 (请先生成英文版定稿)"
  exit 1
fi

echo "📝 正在生成 LinkedIn 内容..."

SUMMARY=$(python3 -c "
import re
with open('$SRC_FILE') as f:
    text = f.read()

# Skip Jekyll frontmatter
text = re.sub(r'^---.*?---\n', '', text, flags=re.DOTALL)

lines = text.split('\n')
sections = []
current_content = []
max_chars = 2500

for line in lines:
    if re.match(r'^# (🔥|🏦|🌐|🤖|💻|🌱|🏥|Headlines|Finance|International|Artificial|Tech|Environment|Healthcare)', line):
        if current_content:
            content = ' '.join(current_content[:2]).strip()[:200]
            sections.append(content + '\n')
        current_content = []
    elif line.strip() and not line.startswith('>') and not line.startswith('🔗') and not line.startswith('---') and not line.startswith('⚠️'):
        current_content.append(line.strip())

# Extract title
title = ''
for line in lines:
    if line.startswith('# ') and ('Vol' in line or 'Weekly' in line or 'what' in line.lower()):
        title = line.strip('# ').strip()
        break

if not title:
    title = \"what's Up! Global Weekly Digest\"

output = f'🟣 {title}\n'
output += 'Curated global digest covering this week in tech, AI, markets & world affairs.\n\n'

for s in sections[:6]:
    output += s[:300] + '\n'

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
  echo "⚠️ 未找到剪贴板工具，请手动复制上方内容"
fi

echo ""
echo "🔗 原文链接: $GITHUB_URL"
echo ""
echo "💼 发布到 LinkedIn:"
echo "   1. 打开 https://www.linkedin.com/feed/"
echo "   2. Cmd/Ctrl+V 粘贴内容"
echo "   3. 点击 Post"
