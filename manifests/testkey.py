import os
import platform
import re
import sys
from copy import deepcopy

import yaml

NUM_FUNCTIONAL_SPLITS = 2
MAX_DEPTH = 5
SUITE_TUPLE_RE = re.compile(r'\s+return \("S?(\d+)", ?".*"\)')


def sysname():
    sys_platform = platform.system().lower()
    if sys_platform.startswith("darwin"):
        return "mac"
    elif sys_platform.startswith("win"):
        return "win"
    elif sys_platform.startswith("linux"):
        return "linux"
    raise OSError("Unsupported system.")


def test_expected_to_pass(entry: dict) -> bool:
    """
    Return True if the test is marked 'pass' in the manifest.
    Else return False.
    """
    ptr = entry
    for _ in range(MAX_DEPTH):
        if "result" not in ptr:
            ptr = ptr[list(ptr.keys())[0]]
    if ptr["result"] == "pass":
        return True
    elif isinstance(ptr["result"], str):
        return False
    else:
        if ptr["result"][sysname()] == "pass":
            return True
    return False


def has_subtests(entry: dict) -> bool:
    """Given an entry, does it have subtests?"""
    suite = entry[list(entry.keys())[0]]
    test = suite[list(suite.keys())[0]]
    return test.keys() and "result" not in test.keys()


def get_subtests(entry: dict) -> list:
    """Return a list of entries where each entry represents a subtest of a given test entry"""
    if not has_subtests(entry):
        return []
    suite = list(entry.keys())[0]
    testfile = list(entry[suite].keys())[0]
    subtests = []
    for subtest_name in entry[suite][testfile].keys():
        subtests.append(
            {suite: {testfile: {subtest_name: entry[suite][testfile][subtest_name]}}}
        )
    print(subtests)
    return subtests


def clean_prompt(prompt: str) -> str:
    """Clean up prompts"""
    if prompt[0].islower():
        prompt[0] = prompt[0].upper()
    if "?" not in prompt:
        prompt = prompt.strip() + "? "
    if not prompt.endswith(" "):
        prompt = prompt + " "
    return prompt


def ask_question(prompt: str) -> bool:
    """Ask a question, return True for yeslike strs, False for nolike."""
    prompt = clean_prompt(prompt)
    while True:
        resp = input(prompt)
        first_char = resp.strip().lower()[0]
        if first_char == "y":
            return True
        elif first_char == "n":
            return False


def ask_open_question(prompt: str) -> str:
    """Asks an open question, only accepts non-empty string answers."""
    prompt = clean_prompt(prompt)
    while True:
        resp = input(prompt)
        clean_resp = resp.strip()
        if clean_resp:
            return clean_resp


class TestKey:
    def __init__(self, manifest_file, test_root="tests"):
        self.manifest_file = manifest_file
        with open(manifest_file) as fh:
            self.manifest = yaml.safe_load(fh)
        self.test_root = test_root

    def write(self):
        """
        Dump the manifest to the filename passed at initialization.
        """
        with open(self.manifest_file, "w") as fh:
            yaml.safe_dump(self.manifest, fh)

    def normalize_test_filename(self, suite, testfile, subtest=None):
        filename = os.path.join(self.test_root, suite, f"{testfile}.py")
        if subtest is not None:
            filename = filename + "::" + subtest
        return filename

    def filter_filenames_by_pass(self, filenames: list) -> list:
        """
        Given a list of filenames, return only the ones marked 'pass'
        """
        passes = []
        for filename in filenames:
            full_entry = self.get_entry_from_filename(filename)
            if has_subtests(full_entry):
                subtests = get_subtests(full_entry)
                print(subtests)
                subresults = [test_expected_to_pass(subtest) for subtest in subtests]
                if all(subresults):
                    passes.append(filename)
                elif any(subresults):
                    for i, subtest in enumerate(subtests):
                        if subresults[i]:
                            suite = list(subtest.keys())[0]
                            testfile = list(subtest[suite].keys())[0]
                            subtest_name = list(subtest[suite][testfile].keys())[0]
                            print(f"normalizing {suite} {testfile}, {subtest_name}")
                            passes.append(
                                self.normalize_test_filename(
                                    suite, testfile, subtest_name
                                )
                            )
                continue
            if test_expected_to_pass(full_entry):
                passes.append(filename)

        return passes

    def get_entry_from_filename(self, filename) -> dict:
        """
        Given a filename, get a partial dict that represents
        the test's location in the manifest
        """
        segments = filename.split(os.path.sep)
        i = 0
        if segments[i] == ".":
            i += 1
        if segments[i] != self.test_root:
            print(f"Test file not in root dir {self.test_root}")
            return None
        entry = {}
        manifest_ptr = self.manifest
        entry_ptr = entry
        segments[-1] = segments[-1].replace(".py", "")
        if "::" in segments[-1]:
            testfile, subtest = segments[-1].split("::")
            segments[-1] = testfile
            segments.append(subtest)
        i += 1
        for segment in segments[i:-1]:
            if segment not in manifest_ptr:
                print(f"Test file not in manifest: {filename}")
            entry_ptr[segment] = {}
            entry_ptr = entry_ptr[segment]
            manifest_ptr = manifest_ptr[segment]
        entry_ptr[segments[-1]] = manifest_ptr[segments[-1]]
        return entry

    def rebalance_functionals(self):
        """
        Reassign tests to a functional split, based on what number is set in
        NUM_FUNCTIONAL_SPLITS. Currently, the function may split suites.
        """
        all_functs = []
        for splitnum in range(NUM_FUNCTIONAL_SPLITS + 1):
            all_functs.extend(
                self.gather_split(f"functional{splitnum:02}", pass_only=False)
            )
        total_functs = len(all_functs)
        functs_per_split = total_functs // NUM_FUNCTIONAL_SPLITS
        remainder = total_functs % NUM_FUNCTIONAL_SPLITS
        split_cutoffs = []
        for i in range(NUM_FUNCTIONAL_SPLITS):
            prev_cutoff = 0 if i == 0 else split_cutoffs[i - 1]
            extra = 1 if remainder > 0 else 0
            remainder -= 1
            split_cutoffs.append(prev_cutoff + functs_per_split + extra)
        for i, test_filename in enumerate(all_functs):
            splitnum = 0
            for j in range(NUM_FUNCTIONAL_SPLITS):
                if i > split_cutoffs[j]:
                    splitnum = j + 1
            entry = self.get_entry_from_filename(test_filename)
            suite = list(entry.keys())[0]
            ptr = entry[suite]
            for _ in range(MAX_DEPTH):
                if "splits" not in ptr:
                    ptr = ptr[list(ptr.keys())[0]]
                else:
                    break
            actual_test = list(entry[suite].keys())[0]
            if f"functional{(splitnum + 1):02}" in ptr["splits"]:
                print(f"Keeping {actual_test} in functional split {(splitnum + 1):02}")
                continue
            for split_ in ptr["splits"]:
                if split_.startswith("functional"):
                    ptr["splits"].remove(split_)
            print(f"Moving {actual_test} to functional split {(splitnum + 1):02}")
            ptr["splits"].append(f"functional{(splitnum + 1):02}")
            self.manifest[suite] |= entry[suite]

    def gather_split(self, split_name, pass_only=True):
        """
        Given a split name, return the pytest locations of the tests in that split.
        Default to only returning tests expected to pass
        """
        test_filenames = []
        for suite in self.manifest:
            for testfile in self.manifest[suite]:
                if "splits" in self.manifest[suite][testfile]:
                    if split_name not in self.manifest[suite][testfile]["splits"]:
                        continue
                    if pass_only and not test_expected_to_pass(
                        self.manifest[suite][testfile]
                    ):
                        continue
                    test_filenames.append(self.normalize_test_filename(suite, testfile))
                else:
                    if not any(
                        [k.startswith("test_") for k in self.manifest[suite][testfile]]
                    ):
                        print(
                            f"Manifest entry for {suite} {testfile} is malformed: no splits"
                        )
                        continue
                    for subtest in self.manifest[suite][testfile]:
                        if not subtest.startswith("test_"):
                            print(
                                f"Manifest entry for {suite} {testfile} has illegal key: {subtest}"
                            )
                            continue
                        if "splits" not in self.manifest[suite][testfile][subtest]:
                            print(
                                f"Manifest entry for {suite} {testfile} :: {subtest} "
                                "is malformed: no splits"
                            )
                            continue
                        if split_name not in self.manifest[suite][testfile][subtest]:
                            continue
                        if pass_only and not test_expected_to_pass(
                            self.manifest[suite][testfile][subtest]
                        ):
                            continue
                        test_filenames.append(
                            self.normalize_test_filename(suite, testfile, subtest)
                        )

        return test_filenames

    def get_valid_suites_in_split(self, split, suite_numbers=False) -> list:
        """
        Given a split name, return the subdirectory names corresponding to
        valid suites with member tests in the split. If suite_numbers is True,
        return the TestRail suite id instead.
        """
        filenames = self.gather_split(split)
        suite_dirs = []
        for filename in filenames:
            suite_dir = filename.split(os.path.sep)[1]
            if suite_dir not in suite_dirs:
                suite_dirs.append(suite_dir)

        if not suite_numbers:
            return suite_dirs
        else:
            suite_nums = []
            for suite_dir in suite_dirs:
                with open(os.path.join("tests", suite_dir, "conftest.py")) as fh:
                    lines = fh.readlines()
                suite_flag = False
                for line in lines:
                    if suite_flag:
                        m = SUITE_TUPLE_RE.search(line)
                        if m and len(m.groups()) > 0:
                            suite_num = m.group(1)
                        if suite_num not in suite_nums:
                            suite_nums.append(suite_num)
                        suite_flag = False
                        break
                    else:
                        if "def suite_id" in line:
                            suite_flag = True

            return suite_nums

    def find_all_splits(self):
        """
        Iterate through the manifest file and return a set
         including unique splits.
        """
        splits = set()
        data = self.manifest
        for folder, files in data.items():
            if not isinstance(files, dict):
                continue

            for file_name, file_data in files.items():
                if not isinstance(file_data, dict):
                    continue

                file_splits = file_data.get("splits", [])
                if isinstance(file_splits, list):
                    splits.update(file_splits)

        return sorted(splits)

    def addtests(self, interactive=True):
        """
        If a test in the directory is not in the manifest, ask questions
        to determine where the tests should go in the manifest, then add it
        and write the manifest. If interactive is False, exit with an error
        code if a test is not in the manifest.
        """
        newkey = deepcopy(self.manifest)
        for root, _, files in os.walk(self.test_root):
            for f in files:
                suite = root.split(os.path.sep)[1]
                if not (f.startswith("test_") and f.endswith(".py")):
                    continue
                testfile = f.replace(".py", "")
                if suite not in newkey:
                    if not interactive:
                        sys.exit(
                            "Please run `python addtests.py` from your command prompt."
                        )
                    if ask_question(f"Found suite {suite}. Add it to key? "):
                        newkey[suite] = {}

                resplit = False
                if testfile not in newkey[suite]:
                    if not interactive:
                        sys.exit(
                            "Please run `python addtests.py` from your command prompt."
                        )
                    if ask_question(f"Found test {suite}/{testfile}. Add it to key? "):
                        newkey[suite][testfile] = {"result": "pass"}

                    resplit = True

                old_style = (
                    isinstance(newkey[suite][testfile], str)
                    or not any(
                        [k.startswith("test_") for k in newkey[suite][testfile].keys()]
                    )
                ) and "result" not in newkey[suite][testfile]
                if old_style:
                    print(
                        f"The test at {suite}/{testfile} is mis-keyed, fixing automatically..."
                    )
                    newkey[suite][testfile] = {"result": newkey[suite][testfile]}
                    resplit = True

                if resplit:
                    if ask_question(
                        "Should this test run in a Scheduled Functional split? "
                        "(Say no if unsure.) "
                    ):
                        newkey[suite][testfile]["splits"] = ["functional1"]
                        self.rebalance_functionals()
                    else:
                        all_splits = self.find_all_splits()
                        output = "\n".join(f"{item}" for item in all_splits)

                        split = ask_open_question(
                            f"What split is this test assigned to? Please choose one "
                            f"from available splits:\n {output}. "
                        )
                        newkey[suite][testfile]["splits"] = [split]

                    print(
                        f"Test will be added to {split} in {self.manifest_file}. "
                        "Consider modifying that file if the test is unstable in any OS, "
                        "or if subtests need to be tracked separately."
                    )

        self.manifest = newkey
        self.write()
