"""Check every tree path cited by the critical round against the tree inventory.

Same rules as validate_paths.py, but over the c_*.py ledger and against the refreshed
.fxtree snapshot. A cited token is OK if it is an existing file, an existing directory
prefix, or a bare basename matching exactly one file (the ledger abbreviates repeated
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

for f in sorted(glob.glob(os.path.join(HERE, "c_*.py"))):
    mod = os.path.basename(f)[:-3]
    if mod in ("crit_pop", "crit_sheet", "c_util"):
        continue
    importlib.import_module(mod)

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
        # The ledger also abbreviates *mid-path*, e.g. "toolkit/.../tests/" followed by
        # "unit_aus_update/foo.js", so accept a multi-segment token that is the suffix of a
        # real file. A few basenames exist under two roots (newtab keeps test/unit and
        # test/jest copies), so any match is enough to show the token is not a typo.
        cands = [
            f for f in BASENAMES.get(os.path.basename(tok), []) if f.endswith("/" + tok)
        ]
        if cands:
            continue
        bad.append((cl["suite"], tok))

head = open(os.path.join(ROOT, ".fxtree", "HEAD")).read().strip()
print("tree snapshot:", head)
print("distinct cited tokens:", len(seen))
print("UNVERIFIED:", len(bad))
for suite, tok in bad:
    base = os.path.basename(tok)
    hint = ""
    if base not in BASENAMES:
        stem = re.split(r"[._]", base)[0][:22]
        near = [b for b in BASENAMES if stem and stem in b][:3]
        hint = "  ~ " + ", ".join(near) if near else "  (no near match)"
    print("  suite %-7s %s%s" % (suite, tok, hint))
