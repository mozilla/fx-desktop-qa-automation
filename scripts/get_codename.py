from manifests.testkey import DEFAULT_KEY_PATH, TestKey


def main(testpath: str) -> str:
    manifest = TestKey(DEFAULT_KEY_PATH)
    return manifest.get_entry_field_from_filename(testpath, "codename")
