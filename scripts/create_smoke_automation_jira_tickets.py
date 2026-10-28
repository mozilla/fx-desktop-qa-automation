"""Create the Smart Window smoke-automation tickets under epic DTE-5295.

One child issue per functional group from the smoke suite, each listing the
TestRail cases it covers. Groups and case lists are the same ones the TestRail
script tags as "Smoke & Sanity", so the two stay in step.

Idempotent: an issue whose summary already exists under the epic is left alone,
so re-running after a partial failure only creates what is missing.

Credentials come from jira_credentials.env (gitignored). Dry run by default;
pass --apply to create.

    python scripts/create_smoke_automation_jira_tickets.py
    python scripts/create_smoke_automation_jira_tickets.py --apply
"""

import argparse
import base64
import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

EPIC_KEY = "DTE-5295"
# The board picks up every Smart Window ticket by this label.
BOARD_LABEL = "dte-automation"
TESTRAIL_CASE_URL = "https://mozilla.testrail.io/index.php?/cases/view/{}"

# (group, why it is in smoke, [(case_id, title)]) — only the cases still to automate.
GROUPS = [
    (
        "Window lifecycle and switching",
        "The feature's front door: getting into a Smart Window, back out, and keeping "
        "state across the switch.",
        [
            (3309852, "Open a Smart Window from the Hamburger menu"),
            (4062295, "A Smart Window opens first even if the last window was Classic"),
        ],
    ),
    (
        "Smart Bar input and search",
        "The Smart Bar is the Smart Window's address bar; if it stops routing queries "
        "the feature is unusable.",
        [
            (3321894, "Smart Bar suggestions recognise the user's intent to chat"),
            (
                3977124,
                "Search with different search engines directly from the Smart Bar",
            ),
        ],
    ),
    (
        "AI chat",
        "The core value proposition: ask something, get an answer, keep the thread.",
        [
            (3322038, "Summarize the page for the active tab"),
            (3374374, "Continue a conversation on the Home page"),
        ],
    ),
    (
        "AI tab actions",
        "Tool calls that change browser state. No case in this group is automated yet, "
        "so it is the biggest hole in the smoke path.",
        [
            (4120777, "The AI model can close tabs"),
            (4220532, "The AI model can create a tab group"),
        ],
    ),
    (
        "History and chat history",
        "Both entry points to past activity, browser and chat.",
        [(3313455, "Reach the History page from the Smart Window Home page")],
    ),
    (
        "Settings and AI controls",
        "Where a user turns the feature off. The kill switch must always work.",
        [
            (3310316, "The AI model type is displayed in the AI settings page"),
            (3310318, "Change the AI model from the Settings page"),
        ],
    ),
    (
        "Onboarding and sign-in",
        "First run and FxA. Gates every other surface for a real user.",
        [
            (3371299, "Start the Onboarding process from the Hamburger menu"),
            (3392591, "Sign-in flow is working"),
        ],
    ),
    (
        "Session restore",
        "A Smart Window must survive a restart.",
        [
            (
                3309861,
                'Smart Window restored automatically with "Open previous windows and tabs"',
            )
        ],
    ),
]


# Research spikes. These are not smoke automation, so they carry the board
# label but are deliberately NOT parented to the smoke epic.
SPIKES = [
    (
        "[SPIKE] - fx-desktop-qa-automation - Smart Window Monkey Testing",
        "Can randomised/fuzz interaction find Smart Window defects that scripted "
        "scenarios miss?",
        [
            "Pick an approach: a Selenium-driven random walker over the Smart Window "
            "surfaces, or an existing fuzz harness.",
            "Decide what counts as a failure signal without a test oracle -- crashes, "
            "unhandled rejections in the browser console, chrome errors, a hung chat turn.",
            "Decide how a finding is made reproducible: seed the random stream and "
            "record the action sequence.",
            "Note that the mock server makes model replies deterministic, so a monkey run "
            "varies only in user actions. That is what makes replay feasible.",
            "Output: a recommendation, a rough cost, and one worked example of a "
            "reproducible finding.",
        ],
    ),
    (
        "[SPIKE] - fx-desktop-qa-automation - Smart Window Visual Testing (Nova redesign)",
        "About 100 of the 289 Smart Window scenarios are visual-design checks "
        "(gradients, glow, rounded corners, spacing, animation). They are the single "
        "largest not-automatable block. Is a visual-baseline approach worth it for a "
        "subset?",
        [
            "Scope: the Nova redesign sections in S70279 -- see "
            "s70279_automatability_report.md, the sections listed under 'Nova redesign'.",
            "Evaluate screenshot-diff baselines against the cost nobody wants: flaky "
            "diffs from font rendering, animation timing and platform differences.",
            "Consider the cheaper middle ground first -- assert computed styles or "
            "element geometry for a handful of high-value cases rather than pixels.",
            "Separate the genuinely subjective cases ('a subtle glowing border') from the "
            "measurable ones ('the active tab has a gradient border'); only the latter "
            "are candidates.",
            "Output: recommend in or out, and if in, name the specific cases worth it.",
        ],
    ),
    (
        "[SPIKE] - fx-desktop-qa-automation - Functionality Coverage Reporting",
        "Weekly reporting currently counts test cases added, which does not say how much "
        "of the feature is actually covered. Work out how to report coverage by "
        "functionality instead.",
        [
            "The raw material already exists: TestRail sections are functional areas, and "
            "every S70279 case now carries an automation status (Completed / Suitable / "
            "Untriaged) plus a coverage value (Full / Partial / None).",
            "A per-section 'N of M scenarios automated, X Full / Y Partial' rolls straight "
            "out of the TestRail API -- see "
            "modules/testrail_scripts/set_smart_window_smoke_and_automation.py for the "
            "field handling.",
            "Decide the denominator: all scenarios, or only the automatable ones? Counting "
            "unautomatable visual cases against us makes the number permanently bad.",
            "Decide whether Partial coverage counts as covered, half, or not at all.",
            "Watch the duplicate trap: S70279 has 362 cases but 289 unique scenarios, so "
            "any count off the raw suite is inflated by a quarter.",
            "Output: an agreed metric definition and a script that emits the weekly table.",
        ],
    ),
]


DONE_BY_GROUP = {
    "Window lifecycle and switching": [
        (3248785, "Switch to a Smart Window from the Switch Windows button"),
        (3248786, "Switch to Classic Window from the Switch Windows button"),
        (3309849, "Switch windows while visiting a website"),
        (3309851, "Smart Window option missing in Private Browsing"),
        (3309853, "Open a New Private Window from the Smart Window"),
        (3309854, "Open a New Classic Window from the Smart Window"),
    ],
    "Smart Bar input and search": [
        (3248361, "Perform a Classic Search"),
        (3248362, "Perform a search with different engines"),
        (3321908, "Smart bar autocompletes domains"),
    ],
    "AI chat": [
        (3311329, "Open/Close the AI chat from the ASK button"),
        (3374375, "Continue the conversation in the Chat Sidebar"),
        (3978359, "Close the Sidebar from the X Close button"),
    ],
    "AI tab actions": [],
    "History and chat history": [
        (3313457, "Open the History page from the Hamburger menu")
    ],
    "Settings and AI controls": [
        (3310319, "Enable/Block the Smart Window from the AI controls settings page")
    ],
    "Onboarding and sign-in": [
        (3240165, "Go through the entire Onboarding Flow"),
        (3371305, "Onboarding without an existing account"),
        (3392590, "Signing up via smart window flow"),
    ],
    "Session restore": [(3309859, "Smart Window restored after restart")],
}


def load_credentials():
    """Read jira_credentials.env into the environment, if present."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(root, "jira_credentials.env")
    if not os.path.exists(path):
        return
    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


class Jira:
    """Minimal Jira Cloud REST v3 client: the three calls this script needs."""

    def __init__(self, base_url, email, token):
        self.base = base_url.rstrip("/") + "/rest/api/3/"
        auth = base64.b64encode(f"{email}:{token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method, path, payload=None):
        request = urllib.request.Request(
            self.base + path,
            method=method,
            headers=self.headers,
            data=json.dumps(payload).encode() if payload is not None else None,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as error:
            detail = error.read().decode()[:400]
            if error.code == 401:
                raise SystemExit(
                    "Jira rejected the credentials. Check JIRA_EMAIL and "
                    "JIRA_API_TOKEN in jira_credentials.env; the token is an API "
                    "token, not your password."
                ) from error
            if error.code == 403:
                raise SystemExit(
                    f"Jira refused the request (403). The account may lack Create "
                    f"Issue on this project.\n{detail}"
                ) from error
            raise SystemExit(
                f"Jira {method} {path} -> {error.code}: {detail}"
            ) from error

    def issue(self, key):
        return self._request("GET", f"issue/{key}")

    def _search(self, jql):
        """Run a JQL search, following pagination so nothing is truncated."""
        found, start = {}, 0
        while True:
            page = self._request(
                "GET",
                f"search/jql?jql={urllib.parse.quote(jql)}"
                f"&fields=summary&maxResults=100&startAt={start}",
            )
            issues = page.get("issues", [])
            found.update({i["fields"]["summary"]: i["key"] for i in issues})
            start += len(issues)
            if len(issues) < 100 or start >= page.get("total", start):
                return found

    def children_of(self, key):
        return self._search(f'parent = "{key}" ORDER BY created ASC')

    def summaries_in_project(self, project, label):
        return self._search(f'project = "{project}" AND labels = "{label}"')

    def issue_types(self, project):
        # The projectKeys+expand form of createmeta is deprecated.
        meta = self._request("GET", f"issue/createmeta/{project}/issuetypes")
        return [t["name"] for t in meta.get("issueTypes", [])]

    def create(self, fields):
        return self._request("POST", "issue", {"fields": fields})


def adf_spike(question, points):
    """Body for a research spike: the question, then what to settle."""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": question}]},
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "To settle:",
                        "marks": [{"type": "strong"}],
                    }
                ],
            },
            {
                "type": "bulletList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": point}],
                            }
                        ],
                    }
                    for point in points
                ],
            },
        ],
    }


def adf(group, why, cases, done):
    """Build the Atlassian Document Format body REST v3 requires."""
    bullets = [
        {
            "type": "listItem",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"C{case_id} — {title}",
                            "marks": [
                                {
                                    "type": "link",
                                    "attrs": {
                                        "href": TESTRAIL_CASE_URL.format(case_id)
                                    },
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        for case_id, title in cases
    ]
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": why}]},
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": f"TestRail cases to automate ({len(cases)}):",
                        "marks": [{"type": "strong"}],
                    }
                ],
            },
            {"type": "bulletList", "content": bullets},
            *(
                [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    f"Already automated in this group ({len(done)}), "
                                    "for context -- no work needed:"
                                ),
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": f"C{cid} -- {title}",
                                                "marks": [
                                                    {
                                                        "type": "link",
                                                        "attrs": {
                                                            "href": TESTRAIL_CASE_URL.format(
                                                                cid
                                                            )
                                                        },
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                            for cid, title in done
                        ],
                    },
                ]
                if done
                else []
            ),
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "All cases are tagged 'Smoke & Sanity' in TestRail suite "
                            "S70279 and marked automation status Suitable. Each is "
                            "automatable with the current harness — no new "
                            "infrastructure is needed. See "
                            "s70279_automatability_report.md for the per-case reasoning."
                        ),
                    }
                ],
            },
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Create. Omit for a dry run."
    )
    parser.add_argument(
        "--issue-type", default="Task", help="Child issue type (default: Task)"
    )
    parser.add_argument(
        "--spike-type",
        default=None,
        help="Spike issue type (default: Spike if the project has one, else --issue-type)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    load_credentials()

    missing = [
        name
        for name in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")
        if not os.environ.get(name) or os.environ[name] == "REPLACE_ME"
    ]
    if missing:
        raise SystemExit(
            f"Missing Jira credentials: {', '.join(missing)}. Fill in "
            "jira_credentials.env (token at "
            "https://id.atlassian.com/manage-profile/security/api-tokens)."
        )

    jira = Jira(
        os.environ["JIRA_BASE_URL"],
        os.environ["JIRA_EMAIL"],
        os.environ["JIRA_API_TOKEN"],
    )

    epic = jira.issue(EPIC_KEY)
    project = epic["fields"]["project"]["key"]
    logging.info(
        "Epic %s (%s) in project %s: %s",
        EPIC_KEY,
        epic["fields"]["issuetype"]["name"],
        project,
        epic["fields"]["summary"],
    )

    types = jira.issue_types(project)
    if types:
        logging.info("Issue types in %s: %s", project, ", ".join(types))
    if args.spike_type is None:
        args.spike_type = "Story" if "Story" in types else args.issue_type
    for name, label in (
        (args.issue_type, "--issue-type"),
        (args.spike_type, "--spike-type"),
    ):
        if types and name not in types:
            raise SystemExit(
                f"{label}={name!r} is not a type in {project}. Available: {', '.join(types)}"
            )
    logging.info(
        "Children: %s   Spikes: %s   Label: %s",
        args.issue_type,
        args.spike_type,
        BOARD_LABEL,
    )

    existing = jira.children_of(EPIC_KEY)
    if existing:
        logging.info("Epic already has %s child issue(s).", len(existing))

    planned = 0
    for group, why, cases in GROUPS:
        done_n = len(DONE_BY_GROUP.get(group, []))
        summary = f"Automate Smart Window smoke: {group}"
        if summary in existing:
            logging.info("SKIP  %-52s already exists as %s", group, existing[summary])
            continue
        planned += 1
        if not args.apply:
            logging.info(
                "WOULD CREATE  %-44s %s to do, %s already automated",
                group,
                len(cases),
                done_n,
            )
            continue
        created = jira.create(
            {
                "project": {"key": project},
                "parent": {"key": EPIC_KEY},
                "issuetype": {"name": args.issue_type},
                "labels": [BOARD_LABEL],
                "summary": summary,
                "description": adf(group, why, cases, DONE_BY_GROUP.get(group, [])),
            }
        )
        logging.info("CREATED %s  %s", created["key"], group)

    # Spikes are not smoke automation, so they get the board label but no epic
    # parent. Matched by summary across the project, since they have no parent.
    existing_spikes = jira.summaries_in_project(project, BOARD_LABEL)
    for summary, question, points in SPIKES:
        if summary in existing_spikes:
            logging.info(
                "SKIP  %-52s already exists as %s",
                summary[:52],
                existing_spikes[summary],
            )
            continue
        planned += 1
        if not args.apply:
            logging.info("WOULD CREATE  spike: %s", summary)
            continue
        created = jira.create(
            {
                "project": {"key": project},
                "issuetype": {"name": args.spike_type},
                "labels": [BOARD_LABEL],
                "summary": summary,
                "description": adf_spike(question, points),
            }
        )
        logging.info("CREATED %s  %s", created["key"], summary)

    total = sum(len(cases) for _, _, cases in GROUPS)
    if not args.apply:
        logging.info(
            "Dry run: would create %s issue(s) covering %s TestRail cases. "
            "Re-run with --apply.",
            planned,
            total,
        )
    else:
        logging.info("Done: %s issue(s) created under %s.", planned, EPIC_KEY)


if __name__ == "__main__":
    sys.exit(main())
