import json
import logging
import sys
from collections import defaultdict

from choose_l10n_ci_set import valid_l10n_mappings


def distribute_mappings_evenly(mappings):
    """
    Distribute the selected mappings into 3 splits and return the container.

    Args:
        mappings (dict): A dictionary of mappings, where the keys are sites and the values are sets of regions.
    """
    if not mappings:
        return {}
    # sort the mappings by the length of the regions per site
    mappings = dict(sorted(mappings.items(), key=lambda val: len(val[1]), reverse=True))
    # place the mappings into 3 containers evenly according to the load
    loads = [0, 0, 0]
    balanced_splits = [defaultdict(list) for _ in range(3)]
    for site, regions in mappings.items():
        min_idx = loads.index(min(loads))
        balanced_splits[min_idx][site] = list(regions)
        loads[min_idx] += len(regions)
    return balanced_splits


if __name__ == "__main__":
    l10n_mappings = valid_l10n_mappings()
    all_splits = distribute_mappings_evenly(l10n_mappings)
    if not all_splits:
        logging.warning("No valid l10n mappings")
        sys.exit(1)
    for idx, split in enumerate(all_splits, start=1):
        with open(f"l10n_CM/beta_run_splits/l10n_split_{idx}.json", "w") as f:
            json.dump(split, f)
