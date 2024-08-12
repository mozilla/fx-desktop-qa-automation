import os

def return_slack_blocks(report_file: str):
    task_text = f"*Task*: {os.getenv("GITHUB_REF_NAME")}"
    owner_text = f"*Owner*: {os.getenv("GITHUB_ACTOR")}"
    commit_text = f"*Commit*: https://github.com/mozilla/fx-desktop-qa-automation/commit/{os.getenv("GITHUB_SHA")}"
    test_summary_text = f"*Test Summary*: {report_file} :debug:"

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "firefox-desktop :firefox: Smoke Tests Mac & Windows\n",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": task_text,
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": owner_text},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": commit_text,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": test_summary_text,
            },
        },
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":testops-notify: created by Desktop QA Test Engineering",
                }
            ],
        },
    ]
