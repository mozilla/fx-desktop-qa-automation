import os
import platform
from copy import deepcopy

import yaml

NUM_FUNCTIONAL_SPLITS = 1


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
    if entry["result"] == "pass":
        return True
    elif isinstance(entry["result"], str):
        return False
    else:
        if entry[sysname()]["result"] == "pass":
            return True
    return False


def clean_prompt(prompt: str) -> str:
    # Clean up prompts
    if prompt[0].islower():
        prompt[0] = prompt[0].upper()
    if "?" not in prompt:
        prompt = prompt.strip() + "? "
    if not prompt.endswith(" "):
        prompt = prompt + " "
    return prompt


def ask_question(prompt: str) -> bool:
    # Ask a question, return True for yeslike strs, False for nolike.
    prompt = clean_prompt(prompt)
    while True:
        resp = input(prompt)
        first_char = resp.strip().lower()[0]
        if first_char == "y":
            return True
        elif first_char == "n":
            return False


def ask_open_question(prompt: str) -> str:
    # Asks an open question, only accepts non-empty string answers.
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
        with open(self.manifest_file, "w") as fh:
            yaml.safe_dump(self.manifest, fh)

    def normalize_test_filename(self, suite, testfile, subtest=None):
        filename = os.path.join(self.test_root, suite, f"{testfile}.py")
        if subtest is not None:
            filename = filename + "::" + subtest
        return filename

    def get_entry_from_filename(self, filename) -> dict:
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
        for segment in segments[i + 1 : -1]:
            if segment not in manifest_ptr:
                print(f"Test file not in manifest: {filename}")
            entry_ptr[segment] = {}
            entry_ptr = entry_ptr[segment]
            manifest_ptr = manifest_ptr[segment]
        entry_ptr[segments[-1]] = manifest_ptr[segments[-1]]
        return entry

    def rebalance_functionals(self):
        all_functs = []
        for splitnum in range(NUM_FUNCTIONAL_SPLITS):
            all_functs.extend(self.gather_split(f"functional{splitnum}"))
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
                    splitnum = j
            entry = self.get_entry_from_filename(test_filename)
            ptr = entry
            while "splits" not in ptr:
                ptr = entry[list(entry.keys())[0]]
            if f"functional{splitnum + 1}" in ptr["splits"]:
                continue
            for split_ in ptr["splits"]:
                if split_.startswith("functional"):
                    ptr["splits"].remove(split_)
            ptr["splits"].append(f"functional{splitnum + 1}")
            self.manifest |= entry

    def gather_split(self, split_name, pass_only=True):
        # Given a split name, return the pytest locations of the tests in that split
        # Default to only returning tests expected to pass
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

    def addtests(self):
        newkey = deepcopy(self.manifest)
        for root, _, files in os.walk(self.test_root):
            for f in files:
                suite = root.split(os.path.sep)[1]
                testfile = f.replace(".py", "")
                if suite not in newkey:
                    if ask_question(f"Found suite {suite}. Add it to key? "):
                        newkey[suite] = {}

                if testfile not in newkey[suite]:
                    if not testfile.startswith("test_"):
                        continue
                    if ask_question(f"Found test {suite}/{testfile}. Add it to key? "):
                        newkey[suite][testfile] = {"result": "pass"}

                        split = ask_open_question(
                            "What split is this test assigned to? (One only) "
                        )
                        newkey[suite][testfile]["splits"] = [split]

                        if ask_question(
                            "Should this test run in a Scheduled Functional split? "
                            "(Say no if unsure.) "
                        ):
                            self.rebalance_functionals()

                        print(
                            f"Test will be added to {split} in {self.manifest_file}. "
                            "Consider modifying that file if the test is unstable in any OS, "
                            "or if subtests need to be tracked separately."
                        )

        self.manifest = newkey
        self.write()
