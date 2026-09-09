"""Rebuild the .fxtree/ inventory from the GitHub git-trees API.

The full mozilla-firefox/firefox recursive tree exceeds the API's truncation limit, so we
fetch one recursive tree per top-level subtree of interest and concatenate.

Writes:
  .fxtree/<subtree>.json  - paths under that subtree
  .fxtree/allfiles.json   - flat list of every file path fetched
  .fxtree/bc.json         - just the browser-chrome tests
  .fxtree/HEAD            - the commit the snapshot was taken at
"""

import json
import os
import ssl
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, ".fxtree")
REPO = "mozilla-firefox/firefox"

SUBTREES = [
    "browser",
    "toolkit",
    "devtools",
    "services",
    "accessible",
    "dom",
    "netwerk",
    "security",
    "uriloader",
    "intl",
    "widget",
    "extensions",
    "docshell",
    "image",
    "modules",
    "testing",
    "gfx",
    "layout",
]

CTX = ssl.create_default_context()


def api(path):
    req = urllib.request.Request(
        "https://api.github.com/repos/%s/%s" % (REPO, path),
        headers={
            "User-Agent": "starfox-coverage-analysis",
            "Accept": "application/vnd.github+json",
        },
    )
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", "Bearer " + tok)
    with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
        return json.load(r)


def main():
    os.makedirs(OUT, exist_ok=True)
    head = api("commits/main")["sha"]
    print("HEAD", head)

    root = api("git/trees/%s" % head)
    top = {e["path"]: e["sha"] for e in root["tree"] if e["type"] == "tree"}
    rootfiles = [e["path"] for e in root["tree"] if e["type"] == "blob"]
    json.dump(rootfiles, open(os.path.join(OUT, "root.json"), "w"))

    allfiles = list(rootfiles)
    for name in SUBTREES:
        if name not in top:
            print("  !! no such subtree:", name)
            continue
        t = api("git/trees/%s?recursive=1" % top[name])
        if t.get("truncated"):
            print("  !! TRUNCATED:", name)
        paths = ["%s/%s" % (name, e["path"]) for e in t["tree"] if e["type"] == "blob"]
        json.dump(paths, open(os.path.join(OUT, "%s.json" % name), "w"))
        allfiles.extend(paths)
        print("  %-12s %6d" % (name, len(paths)))

    json.dump(allfiles, open(os.path.join(OUT, "allfiles.json"), "w"))
    bc = [
        f
        for f in allfiles
        if os.path.basename(f).startswith("browser_")
        and f.endswith(".js")
        and "/test" in f
    ]
    json.dump(bc, open(os.path.join(OUT, "bc.json"), "w"))
    open(os.path.join(OUT, "HEAD"), "w").write(head + "\n")
    print("allfiles", len(allfiles), "bc", len(bc))


main()
