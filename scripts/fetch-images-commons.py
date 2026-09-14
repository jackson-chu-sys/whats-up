#!/usr/bin/env python3
"""Wikimedia Commons fallback for whats-up section images (proxy-safe, no auth).
Usage: fetch-images-commons.py YYYY-WNN
Only downloads MISSING files; appends to CREDITS.md.
"""
import json
import os
import subprocess
import sys
import urllib.parse

PROXY = "http://192.168.1.210:7892"
DEST = os.path.join("/mnt/projects/whats-up", "assets/images", sys.argv[1] if len(sys.argv) > 1 else "????")

WANT = [
    ("geopolitics.jpg", ["G20 summit leaders", "diplomats meeting flags", "UN Security Council meeting"]),
    ("environment-energy.jpg", ["wind turbines field", "offshore wind farm", "solar panels wind turbines"]),
    ("health-medical.jpg", ["medical laboratory research", "scientists laboratory pipette", "hospital research lab"]),
]

def curl_json(url):
    r = subprocess.run(["curl", "-sS", "-x", PROXY, "-m", "40", url],
                       capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None

def api(query):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": "6",
        "gsrlimit": "8", "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "800",
    }
    return curl_json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params))

def try_dl(res, dest):
    ii = (res.get("imageinfo") or [{}])[0]
    url = ii.get("thumburl") or ii.get("url")
    if not url:
        return False
    r = subprocess.run(["curl", "-sS", "-x", PROXY, "-m", "60", "-L", "-o", dest, url],
                       capture_output=True, text=True)
    ok = (r.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 5000
          and open(dest, "rb").read(2) == b"\xff\xd8")
    if not ok and os.path.exists(dest):
        os.remove(dest)
    return ok

def main():
    credits_path = os.path.join(DEST, "CREDITS.md")
    credits = []
    missing = []
    for filename, queries in WANT:
        dest = os.path.join(DEST, filename)
        if os.path.exists(dest):
            continue
        print(f"[{filename}]")
        got = False
        for q in queries:
            data = api(q)
            pages = (data or {}).get("query", {}).get("pages", {}) if data else {}
            ranked = sorted(pages.values(), key=lambda p: p.get("index", 99))
            for p in ranked:
                ii = (p.get("imageinfo") or [{}])[0]
                title = p.get("title", "")
                if any(bad in title.lower() for bad in ("dall", "midjourney", "chatgpt", "generated")):
                    continue
                if ii.get("mime") != "image/jpeg" or (ii.get("width") or 0) < 700:
                    continue
                if try_dl(p, dest):
                    md = ii.get("extmetadata") or {}
                    artist = (md.get("Artist", {}).get("value") or "").strip()
                    lic = (md.get("LicenseShortName", {}).get("value") or "").strip()
                    print(f"  OK {filename} ({os.path.getsize(dest)}B) <- {title} [{lic}]")
                    credits.append(f"- {filename}: \"{title}\" ({lic}), via Wikimedia Commons: "
                                   f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}")
                    got = True
                    break
            if got:
                break
        if not got:
            missing.append(filename)
    if credits:
        with open(credits_path, "a", encoding="utf-8") as f:
            f.write("\n".join(credits) + "\n")
    print("STILL MISSING: " + ", ".join(missing) if missing else "ALL RESOLVED")

if __name__ == "__main__":
    main()
