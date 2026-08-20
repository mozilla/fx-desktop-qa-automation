import csv
import json
import sys

GITHUB_PREFIX = "https://github.com/mozilla/fx-desktop-qa-automation/tree/main"
SEARCHFOX_TEMPLATE = "https://searchfox.org/firefox-main/search?q=%SEARCH_TERM%&path=&case=false&regexp=false"


def respond(row: dict):
    resp = "xyz"
    resp_options = [
        "Agree with verdict",
        "Disagree with verdict",
        "Skip test",
    ]
    match = None
    while match is None:
        pad = "\n\t"
        links = ["STARfox: " + "/".join([GITHUB_PREFIX, row["starfox_test"]])]
        for treetest in row["in_tree_tests"].split(";"):
            links.append(
                "   Tree: "
                + SEARCHFOX_TEMPLATE.replace("%SEARCH_TERM%", treetest.strip())
            )
        print("\n".join(links))
        print(f"Options:{pad}{pad.join(resp_options)}")
        resp = input("Please select: ").strip().lower()
        for r in resp_options:
            if r.lower().startswith(resp):
                match = r
                break
            else:
                match = None
        if match == resp_options[0]:
            return "Agree"
        elif match == resp_options[1]:
            final = False
            while not final:
                reason = input("Please explain your reasoning: ")
                final_resp = input("Is this correct? ")
                final = final_resp.lower().startswith(
                    "y"
                ) or final_resp.lower().startswith("c")
            return reason
        elif match == resp_options[2]:
            return "Skip"


with open(sys.argv[1]) as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        with open("responses.json") as rfh:
            current_responses = json.load(rfh)
        if row["verdict"] == "STRONG":
            starfox_test = row["starfox_test"]
            if starfox_test in current_responses:
                continue
            resp = respond(row)
            if resp == "Skip":
                continue
            else:
                current_responses[row["starfox_test"]] = resp
            with open("responses.json", "w") as ofh:
                json.dump(current_responses, ofh)
