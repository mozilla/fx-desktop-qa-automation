import os


def return_slack_blocks(report_file: str):
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
                "text": f"*Task*: {os.getenv("GITHUB_REF_NAME")}",
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Owner*: {os.getenv("GITHUB_ACTOR")}"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Commit*: https://github.com/mozilla/fx-desktop-qa-automation/commit/{os.getenv("GITHUB_SHA")}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Test Summary*: {report_file} :debug:",
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
