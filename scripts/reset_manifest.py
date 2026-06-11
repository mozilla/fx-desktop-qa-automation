import sys

from manifests.testkey import TestKey

MANIFEST = "manifests/key.yaml"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Please indicate which split to add tests to.")
    tests = [line.strip() for line in open("selected_tests").readlines()]
    manifest = TestKey(MANIFEST)
    for test in tests:
        entry = manifest.get_entry_from_filename(test)
        while "splits" not in entry:
            for k in entry:
                entry = entry[k]
                break
            entry["splits"].append(sys.argv[1])
    manifest.write()
