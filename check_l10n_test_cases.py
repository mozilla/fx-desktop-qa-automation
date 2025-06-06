import json
import os
import sys
from collections import defaultdict

OUTPUT_FILE = "selected_l10n_mappings"


def valid_l10n_mappings():
    mapping = defaultdict(set)
    region_paths = [d for d in os.listdir("./l10n_CM/region/")]
    for region_path in region_paths:
        if region_path != "Unified.json":
            region = region_path.split(".")[0]
            with open(f"./l10n_CM/region/{region_path}", "r+") as f:
                region_file = json.load(f)
                if region_file.get("sites"):
                    for site in region_file.get("sites"):
                        mapping[site].add(region)
    return mapping


if __name__ == "__main__":
    l10n_mappings = valid_l10n_mappings()
    with open(OUTPUT_FILE, "w") as file:
        pass  # File is created or cleared
    for site, regions in l10n_mappings.items():
        with open(OUTPUT_FILE, "a+") as fh:
            fh.write(f"{site} {' '.join(regions)}\n")
    sys.exit(0)
