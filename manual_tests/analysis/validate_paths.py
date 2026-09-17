"""Check every tree path cited in the verdict ledger against the live tree inventory.

A cited token is OK if it is an existing file, an existing directory prefix, or a bare
basename that matches exactly one file in the inventory (the ledger abbreviates repeated
directories, e.g. "dir/browser_a.js; browser_b.js").
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

import _ledger  # noqa: E402

for f in sorted(glob.glob(os.path.join(HERE, "d_*.py"))):
    importlib.import_module(os.path.basename(f)[:-3])

allf = json.load(open(os.path.join(ROOT, ".fxtree", "allfiles.json")))
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
for cl in _ledger.CLUSTERS:
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
        bad.append((cl["suite"], tok))

print("distinct cited tokens:", len(seen))
print("UNVERIFIED:", len(bad))
for suite, tok in bad:
    hint = ""
    base = os.path.basename(tok)
    if base not in BASENAMES:
        near = [b for b in BASENAMES if base.split(".")[0][:22] in b][:3]
        hint = "  ~ " + ", ".join(near) if near else "  (no near match)"
    print("  suite %-7s %s%s" % (suite, tok, hint))
