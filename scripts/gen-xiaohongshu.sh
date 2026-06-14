#!/bin/bash
# gen-xiaohongshu.sh — 从小红书周刊生成小红书发布内容
# Usage: ./scripts/gen-xiaohongshu.sh 2026-W24

set -e
cd "$(dirname "$0")/.."

WEEK="${1:-2026-W24}"
CN_FILE="issues/${WEEK}/index.cn.md"
GITHUB_URL="https://jackson-chu-sys.github.io/whats-up/issues/${WEEK}/"

if [ ! -f "$CN_FILE" ]; then
  echo "❌ 找不到 $CN_FILE"
  exit 1
fi

echo "📝 正在从 $CN_FILE 生成小红书内容..."

# Extract title and first few sections
TITLE=$(head -5 "$CN_FILE" | grep -E '^# [^#]' | head -1 | sed 's/^# //')
if [ -z "$TITLE" ]; then
  TITLE="what's Up! 全球热点周刊"
fi

# Generate condensed version (first 3 sections summaries)
SUMMARY=$(python3 -c "
import re, sys
with open('$CN_FILE') as f:
    text = f.read()

# Extract section headers and first paragraph of each
lines = text.split('\n')
sections = []
current_section = ''
current_content = []
in_content = False
char_count = 0
max_chars = 900

for line in lines:
    if line.startswith('# 🔥') or line.startswith('# 🏦') or line.startswith('# 🌐') or line.startswith('# 🤖') or line.startswith('# 💻') or line.startswith('# 🌱') or line.startswith('# 🏥'):
        if current_section and current_content:
            content = ' '.join(current_content[:3]).strip()
            sections.append(f'{current_section}\n{content}')
        current_section = line
        current_content = []
        in_content = True
    elif in_content and line.startswith('## ▶'):
        # subsection - grab its text
        pass
    elif in_content and line.strip() and not line.startswith('>') and not line.startswith('🔗'):
        current_content.append(line.strip())

if current_section and current_content:
    content = ' '.join(current_content[:3]).strip()
    sections.append(f'{current_section}\n{content}')

# Build output
output = f'🟣 {TITLE}\n\n'
for s in sections[:5]:  # top 5 sections for 小红书
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
  echo "⚠️ 未找到剪贴板工具 (xclip/pbcopy)，请手动复制上方内容"
fi

echo ""
echo "🔗 原文链接: $GITHUB_URL"
echo "📸 封面图: assets/covers/${WEEK}.png (请手动准备)"
echo ""
echo "🌐 打开小红书发布页..."
echo "   手动操作: 1. 打开 https://creator.xiaohongshu.com/publish/publish"
echo "             2. Cmd/Ctrl+V 粘贴内容"
echo "             3. 上传封面图"
echo "             4. 点击发布"
