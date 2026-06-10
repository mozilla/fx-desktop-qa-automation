import os
import sys

TESTNAME_LEN = 14
THRESHOLDS = {2: 4, 6: 3, 10: 2}

VOWELS = "aeiouy"

MID_TOKENS = [
    "and",
    "as",
    "a",
    "an",
    "the",
    "via",
    "from",
    "to",
    "in",
    "on",
    "ui",
    "ux",
    "action",
    "viewer",
    "through",
]

SUFFIXES = [
    "ing",
    "ed",
    "es",
]


def collapse(s: str, length=4) -> str:
    if not s:
        return ""
    c = s[0]
    tail = s[1:]
    for suf in SUFFIXES:
        if tail.endswith(suf):
            tail = tail[: -(len(suf))]
    for v in VOWELS:
        tail = tail.replace(v, "")
    while len(tail) >= length:
        tail = tail[:-2] + tail[-1]
    return c + tail


def suite_collapse(s: str, length=4) -> str:
    for token in MID_TOKENS:
        s = s.replace(f"_{token}_", "_")
    if s.endswith(f"_{token}"):
        s = s[: -(len(token) + 1)]
    if "_" in s:
        words = s.split("_")
        print(f"w{words}")
        return "".join(w[0].upper() for w in words)
    if s.endswith("s"):
        s = s[:-1]
    if len(s) > length:
        for v in VOWELS:
            s = s.replace(v, "")
    while len(s) > length:
        s = s[:-2] + s[-1]
    return s.upper()


def test_collapse(test: str) -> dict:
    print(f"1 {test}")
    test = test.replace(".py", "")
    if test.endswith("_"):
        test = test[:-1]
    print(f"2 {test}")
    if test.startswith("test_"):
        test = test.replace("test_", "")
    print(f"3 {test}")
    for token in MID_TOKENS:
        test = test.replace(f"_{token}_", "_")
    print(f"4 {test}")
    pieces = test.split("_")
    if len(test) > TESTNAME_LEN * 1.5:
        pieces = pieces[:-1]
        test = "_".join(pieces)
    if len(test) > TESTNAME_LEN:
        for v in VOWELS:
            test = test[0] + test[1:].replace(v, "")
    print(f"5 {test}")
    while len(test) > TESTNAME_LEN:
        # print(f"--t{test}")
        pieces = test.split("_")
        if len(test) > TESTNAME_LEN * 1.5:
            pieces = pieces[:-1]
        for i in range(len(pieces)):
            if len(pieces[i]) < 3:
                continue
            pieces[i] = pieces[i][:-2] + pieces[i][-1]
        test = "_".join(pieces)
    print(f"6 {test}")
    return test


def get_collapsers(tests: list) -> dict:
    collapsers = {}
    last_tokens = [p[-1] for p in [test.split(os.sep) for test in tests]]
    longest_token_num = max([t.count("_") for t in last_tokens])
    for i in range(longest_token_num):
        counts = {}
        for token in last_tokens:
            token = token.replace(".py", "")
            words = token.split("_")
            if i > len(words) - 1:
                continue
            if words[i] in MID_TOKENS:
                continue
            if words[i] in counts.keys():
                counts[words[i]] += 1
                thr = 0
                for threshold in THRESHOLDS:
                    if counts[words[i]] >= threshold:
                        thr = THRESHOLDS[threshold]
                collapsers[words[i]] = collapse(words[i], thr)
                continue
            counts[words[i]] = 1
    return collapsers


if __name__ == "__main__":
    codenames = {}
    if len(sys.argv) < 2:
        testroots = ["tests"]
    else:
        testroots = sys.argv[1:]
    tests = []
    for testroot in testroots:
        tests.extend(
            [
                os.path.join(dirpath, f)
                for (dirpath, dirnames, filenames) in os.walk(testroot)
                for f in filenames
            ]
        )

    collapsers = get_collapsers(tests)
    bases = {}
    if len(testroots) > 1:
        for testroot in testroots:
            i = 0
            while (cap := testroot[i].upper()) in bases.values():
                i += 1
            bases[testroot] = cap

    for test in tests:
        print(test)
        if test.startswith(".") or test.startswith("_"):
            continue
        nameout = ""
        root, suite = (pieces := test.split(os.sep))[:2]
        testname = pieces[-1]
        testname = testname.replace("test_", "")
        testname = testname.replace(f"_{suite}", "")
        if testname.startswith(".") or testname.startswith("_"):
            continue
        if root in bases:
            nameout = nameout + bases[root] + "|"
        nameout = nameout + suite_collapse(suite)
        for collapser in collapsers:
            testname = testname.replace(collapser, collapsers[collapser])
        testname = test_collapse(testname)
        nameout = nameout + "/" + testname
        codenames[test] = nameout

    for test, codename in codenames.items():
        print(codename, test)
