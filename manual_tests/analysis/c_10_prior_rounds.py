"""Critical round -- carry over the verdicts rounds 1-3 already reached.

Rounds 1-3 (the d_*.py ledger) reviewed 29 suites across all priorities. 482 of the 1551
cases in this round's population already have a verdict there: 357 STRONG and 125 MEDIUM.
Re-deriving them would be wasted effort and would risk disagreeing with the published
LOW_PRIORITY_CANDIDATES.csv for no reason, so this module replays them instead.

Only cases that are (a) in this round's population and (b) not already claimed by an earlier
c_*.py cluster are carried over -- so where this round has looked at a suite in more detail,
that verdict wins.

The prior rounds were taken against main @ 7d438b9 (2026-07-30); this round is against
537539a. Tree coverage only grows between those points, so a carried-over STRONG cannot have
become wrong for lack of a test.
"""

import glob
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import _ledger  # noqa: E402
import crit_pop  # noqa: E402

POP = crit_pop.population()

_before = len(_ledger.CLUSTERS)
_claimed = {cid for cl in _ledger.CLUSTERS for cid in cl["ids"]}

for _f in sorted(glob.glob(os.path.join(HERE, "d_*.py"))):
    importlib.import_module(os.path.basename(_f)[:-3])

# Take what the d_* modules appended, then put the ledger back the way we found it so the
# report only ever sees this round's clusters.
_prior = _ledger.CLUSTERS[_before:]
del _ledger.CLUSTERS[_before:]

_carried = 0
for _cl in _prior:
    _ids = [i for i in _cl["ids"] if i in POP and i not in _claimed]
    if not _ids:
        continue
    _claimed.update(_ids)
    _carried += len(_ids)
    _ledger.C(
        _cl["suite"],
        _cl["tier"],
        _cl["tests"],
        _cl["why"] + "  [carried over from round 1-3 analysis]",
        _ids,
    )
