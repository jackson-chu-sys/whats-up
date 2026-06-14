# 🟣 what's Up!

> 全球热点信息周刊 · Global Weekly Digest

每周一期，覆盖时事、金融、AI、科技等领域的高信息密度 curated digest。

**🌐 阅读**: [jackson-chu-sys.github.io/whats-up](https://jackson-chu-sys.github.io/whats-up)

## 板块

| # | 板块 | 内容 |
|---|------|------|
| 🔥 | 时事热点 | 社交平台热议话题 |
| 🏦 | 金融宏观 | 全球市场与央行动态 |
| 🌐 | 国际政治 | 地缘与外交 |
| 🤖 | 人工智能 | AI 产业与研究前沿 |
| 💻 | 科技产业 | 大厂动态与工程趋势 |
| 🌱 | 环境能源 | 气候与能源转型 |
| 🏥 | 医疗健康 | 公共卫生与心理健康 |

## 工作流

```
1. 写中文稿 → issues/YYYY-WNN/index.cn.md
2. 审阅定稿 → 复制到 _posts/zh/ + 添加 Jekyll frontmatter
3. 翻译英文 → issues/YYYY-WNN/index.en.md
4. 定稿 → 复制到 _posts/en/ + 添加 Jekyll frontmatter
5. ./scripts/publish.sh → 推送到 GitHub → 自动部署 GitHub Pages
6. ./scripts/gen-xiaohongshu.sh → 生成小红书内容
7. ./scripts/gen-linkedin.sh → 生成 LinkedIn 内容
```

## 目录

```
whats-up/
├── _posts/            ← Jekyll 发布目录（GitHub Pages 自动构建）
│   ├── zh/            ← 中文周刊
│   └── en/            ← English edition
├── issues/            ← 源文件（Markdown 编辑在这里）
├── templates/         ← 周刊模板
├── scripts/           ← 自动化脚本
└── assets/            ← 封面图、归档文件
```

## 脚本

| 脚本 | 用途 |
|------|------|
| `./scripts/publish.sh` | 推送到 GitHub，触发 Pages 部署 |
| `./scripts/gen-xiaohongshu.sh 2026-W24` | 从中文稿生成小红书内容 |
| `./scripts/gen-linkedin.sh 2026-W24` | 从英文稿生成 LinkedIn 内容 |
