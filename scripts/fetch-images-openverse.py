#!/usr/bin/env python3
"""Fallback image fetcher: Unsplash napi now requires auth, so use Openverse
(CC-licensed image API, no key needed for basic search). Downloads the 7
section images for an issue.

Usage: fetch-images-openverse.py YYYY-WNN [dest_dir]
Retries up to 3 queries per image; failures skipped. Writes CREDITS.md.
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse

PROXY = "http://192.168.1.210:7892"
REPO = "/mnt/projects/whats-up"

IMAGES = [
    ("trending-news.jpg", "news trending social media"),
    ("finance-markets.jpg", "stock market trading floor"),
    ("geopolitics.jpg", "diplomacy summit"),
    ("ai-school.jpg", "AI education classroom"),
    ("tech-industry.jpg", "silicon valley tech campus"),
    ("environment-energy.jpg", "renewable energy wind turbine"),
    ("health-medical.jpg", "medical research laboratory"),
]

def curl(args, timeout=45):
    cmd = ["curl", "-sS", "-x", PROXY, "-m", str(timeout)] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def curl_bin(args, dest, timeout=60):
    cmd = ["curl", "-sS", "-x", PROXY, "-m", str(timeout), "-L", "-o", dest] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def pick_image_url(res):
    """Prefer an 800px-wide variant for flickr static URLs, else original."""
    url = res.get("url") or ""
    if "live.staticflickr.com" in url:
        base = re.sub(r"_[a-z]\.(jpg|jpeg|png)$", r"", url, flags=re.I)
        m = re.search(r"_([a-z])\.(jpg|jpeg)$", url, re.I)
        if m and m.group(1) not in ("c", "b", "k", "o") and m.group(2).lower() == "jpg":
            return base + "_c.jpg"
    return url

def search(query):
    url = ("https://api.openverse.org/v1/images/?"
           + urllib.parse.urlencode({"q": query, "page_size": 12,
                                     "license_type": "all-cc",
                                     "filetype": "jpg"}))
    r = curl(["-H", "Accept: application/json", url])
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
    return data.get("results") or []

def looks_jpeg(path):
    try:
        with open(path, "rb") as f:
            head = f.read(4)
        return head[:2] == b"\xff\xd8"
    except OSError:
        return False

def fetch_one(filename, query, dest_dir):
    dest = os.path.join(dest_dir, filename)
    for attempt in range(1, 4):
        try:
            results = search(query)
            if not results:
                print(f"  attempt {attempt}: no search results")
                continue
            picked = None
            for res in results:
                u = pick_image_url(res)
                if u and (res.get("width") or 0) >= 700:
                    picked = (res, u)
                    break
            if not picked:
                u = pick_image_url(results[0])
                if u:
                    picked = (results[0], u)
            if not picked:
                print(f"  attempt {attempt}: usable URL not found")
                continue
            res, img = picked
            dl = curl_bin([img], dest)
            if dl.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 5000 and looks_jpeg(dest):
                print(f"  OK {filename} ({os.path.getsize(dest)} bytes) <- {res.get('license')} {res.get('foreign_landing_url','')}")
                return res
            print(f"  attempt {attempt}: download failed rc={dl.returncode}")
            if os.path.exists(dest):
                os.remove(dest)
        except Exception as e:
            print(f"  attempt {attempt}: error {e}")
    return None

def main():
    if len(sys.argv) < 2:
        print("usage: fetch-images-openverse.py YYYY-WNN [dest_dir]")
        sys.exit(1)
    week = sys.argv[1]
    dest_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO, "assets/images", week)
    os.makedirs(dest_dir, exist_ok=True)
    credits = []
    missing = []
    for filename, query in IMAGES:
        print(f"[{filename}] query='{query}'")
        res = fetch_one(filename, query, dest_dir)
        if res:
            credits.append(f"- {filename}: \"{res.get('title')}\" by {res.get('creator')} "
                           f"(license: {str(res.get('license')).upper()} {res.get('license_version')}), "
                           f"via Openverse/{res.get('source')}: {res.get('foreign_landing_url')}")
        else:
            missing.append(filename)
    if credits:
        with open(os.path.join(dest_dir, "CREDITS.md"), "w", encoding="utf-8") as f:
            f.write(f"# {week} 配图来源(Openverse / CC 授权)\n\n" + "\n".join(credits) + "\n")
    if missing:
        print("MISSING: " + ", ".join(missing))
    else:
        print("ALL 7 OK")

if __name__ == "__main__":
    main()
