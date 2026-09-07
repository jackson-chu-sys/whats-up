#!/usr/bin/env python3
"""Download the 7 section images for an issue from Unsplash.

Usage: fetch-images.py YYYY-WNN
Retries up to 3 attempts per image; failures skipped.
"""
import json
import os
import subprocess
import sys
import urllib.parse

PROXY = "http://192.168.1.210:7892"

IMAGES = [
    ("trending-news.jpg", "news trending social media"),
    ("finance-markets.jpg", "stock market trading floor"),
    ("geopolitics.jpg", "diplomacy summit"),
    ("ai-school.jpg", "AI education classroom"),
    ("tech-industry.jpg", "silicon valley tech"),
    ("environment-energy.jpg", "renewable energy wind"),
    ("health-medical.jpg", "medical research laboratory"),
]

def curl(args, timeout=45):
    cmd = ["curl", "-sS", "-x", PROXY, "-m", str(timeout)] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def fetch_one(filename, query, dest_dir):
    dest = os.path.join(dest_dir, filename)
    for attempt in range(1, 4):
        try:
            url = ("https://unsplash.com/napi/search/photos?per_page=5&query="
                   + urllib.parse.quote(query))
            r = curl([url])
            if r.returncode != 0 or not r.stdout.strip():
                print(f"  attempt {attempt}: napi search curl failed rc={r.returncode}")
                continue
            data = json.loads(r.stdout)
            results = data.get("results") or []
            picked = None
            for res in results:
                if res.get("urls", {}).get("raw"):
                    picked = res
                    break
            if not picked:
                print(f"  attempt {attempt}: no results in napi response")
                continue
            img = picked["urls"]["raw"] + "?q=85&w=800&auto=format&fit=crop"
            dl = curl(["-L", "-o", dest, img])
            if dl.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 5000:
                print(f"  OK {filename} ({os.path.getsize(dest)} bytes) <- photo {picked.get('id')}")
                return True
            print(f"  attempt {attempt}: download failed rc={dl.returncode}")
        except Exception as e:
            print(f"  attempt {attempt}: error {e}")
    return False

def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    week = sys.argv[1]
    dest_dir = f"/mnt/projects/whats-up/assets/images/{week}"
    os.makedirs(dest_dir, exist_ok=True)
    missing = []
    for filename, query in IMAGES:
        print(f"[{filename}] query={query!r}")
        if not fetch_one(filename, query, dest_dir):
            missing.append(filename)
    if missing:
        print("MISSING:", ", ".join(missing))
        sys.exit(1)
    print("ALL 7 OK")

if __name__ == "__main__":
    main()
