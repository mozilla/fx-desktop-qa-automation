import os
import sys

NUM_FUNCTIONAL_SPLITS = 1
TEST_ROOT = "tests"
TEST_KEY = os.path.join("manifests", "key.yaml")


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    from manifests import testkey

    manifest = testkey.TestKey(TEST_KEY)
    if len(sys.argv) > 1 and sys.argv[1] == "-q":
        manifest.addtests(interactive=False)
    else:
        manifest.addtests()
