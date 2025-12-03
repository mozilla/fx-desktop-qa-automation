import os

from manifests import testkey

NUM_FUNCTIONAL_SPLITS = 1
TEST_ROOT = "tests"
TEST_KEY = os.path.join("manifests", "key.yaml")


if __name__ == "__main__":
    manifest = testkey.TestKey(TEST_KEY)
    manifest.addtests()
