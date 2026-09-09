"""Check every tree path cited by round 5 against the .fxtree inventory.

A cited token is OK if it is an existing file, an existing directory prefix, a bare basename
matching some file, or a multi-segment suffix of some file (the ledger abbreviates repeated
directories, e.g. "dir/browser_a.js; browser_b.js").

Also re-checks that every STARfox path in the ledger still exists in this repo -- ledger.T()
enforces that at import time, so a failure here means the repo moved underneath it.
"""

import glob
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import ledger  # noqa: E402
import pop  # noqa: E402

for f in sorted(glob.glob(os.path.join(HERE, "a_*.py"))):
    importlib.import_module(os.path.basename(f)[:-3])

inv = os.path.join(ROOT, ".fxtree", "allfiles.json")
if not os.path.exists(inv):
    raise SystemExit(
        ".fxtree/allfiles.json is missing. Run:\n"
        "  python manual_tests/analysis/fetch_tree.py"
    )
allf = json.load(open(inv))
FILES = set(allf)
BASENAMES = {}
for f in allf:
    BASENAMES.setdefault(os.path.basename(f), []).append(f)
DIRS = set()
for f in allf:
    p = f
    while "/" in p:
        p = p.rsplit("/", 1)[0]
        DIRS.add(p)
        DIRS.add(p + "/")

SKIP = re.compile(r"^(n/a|\(|and |the )", re.I)

bad = []
seen = set()
for cl in ledger.CLUSTERS:
    for tok in cl["tests"].split(";"):
        tok = tok.strip().rstrip(",")
        tok = re.sub(r"\s*\(\d+.*?\)$", "", tok).strip()
        if not tok or SKIP.match(tok) or tok in seen:
            continue
        seen.add(tok)
        if tok in FILES or tok in DIRS or tok.rstrip("/") in DIRS:
            continue
        if "/" not in tok and tok in BASENAMES:
            continue
        if [
            f for f in BASENAMES.get(os.path.basename(tok), []) if f.endswith("/" + tok)
        ]:
            continue
        bad.append((cl["area"], tok))

head_path = os.path.join(ROOT, ".fxtree", "HEAD")
head = open(head_path).read().strip() if os.path.exists(head_path) else "unknown"
print("tree snapshot:", head)
print("distinct cited tree paths:", len(seen))
print("UNVERIFIED:", len(bad))
for area, tok in bad:
    base = os.path.basename(tok)
    hint = ""
    if base not in BASENAMES:
        stem = re.split(r"[._]", base)[0][:22]
        near = [b for b in BASENAMES if stem and stem in b][:3]
        hint = "  ~ " + ", ".join(near) if near else "  (no near match)"
    print("  %-34s %s%s" % (area, tok, hint))

missing = sorted(
    {s for cl in ledger.CLUSTERS for s in cl["starfox"]} - pop.repo_tests()
)
if missing:
    print("\nSTARfox paths in the ledger that no longer exist (%d):" % len(missing))
    for m in missing:
        print("  " + m)
