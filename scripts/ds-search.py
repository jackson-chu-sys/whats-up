#!/usr/bin/env python3
"""DeepSeek 搜索/抓取备用链路(纯标准库,不依赖 Hermes provider registry)。

用途:web_search / web_extract 不可用或结果为空时的兜底。
密钥:环境变量 DEEPSEEK_API_KEY,或自动从 /opt/data/.env 读取。

用法:
  python3 scripts/ds-search.py search "查询词" [条数]     # 输出 JSON 结果列表
  python3 scripts/ds-search.py fetch <url>               # 输出 {title, content}
  python3 scripts/ds-search.py search "查询词" 5 --text  # 精简文本(每条 标题/URL/摘要)

退出码:0 成功;1 失败(错误信息写 stderr)。
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://api.deepseek.com/v1/tools"
TIMEOUT = 40


def _key() -> str:
    key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if key:
        return key
    try:
        with open("/opt/data/.env", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    sys.exit("DEEPSEEK_API_KEY not found (env or /opt/data/.env)")


def _post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{BASE}/{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:500]
        sys.exit(f"deepseek {path} HTTP {exc.code}: {body}")
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"deepseek {path} failed: {exc}")


def search(query: str, count: int = 10) -> dict:
    return _post("search", {"query": query, "count": max(1, min(count, 50))})


def fetch(url: str) -> dict:
    return _post("fetch", {"url": url})


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        sys.exit(__doc__)
    cmd = argv[1]
    if cmd == "search":
        query = argv[2]
        count = 10
        as_text = "--text" in argv
        rest = [a for a in argv[3:] if a != "--text"]
        if rest:
            try:
                count = int(rest[0])
            except ValueError:
                sys.exit(f"bad count: {rest[0]}")
        data = search(query, count)
        rows = data.get("results") or []
        if as_text:
            for i, r in enumerate(rows, 1):
                print(f"{i}. {r.get('title','')}")
                print(f"   {r.get('url','')}")
                print(f"   {(r.get('summary') or r.get('snippet') or '')[:300]}")
            return 0
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if cmd == "fetch":
        data = fetch(argv[2])
        print(json.dumps(
            {"title": data.get("title", ""), "content": data.get("content", "")},
            ensure_ascii=False,
        ))
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
