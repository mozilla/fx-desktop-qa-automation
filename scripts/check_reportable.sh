#!/bin/bash
# This script is intended to be run from the Check-Beta-Version job.
# Check-Beta-Version.outputs =>
#  win: "True" | "False" | "Preview",
#  mac: "True" | "False" | "Preview",
#  preview_json: "" | "{...json...}"

pip3 install 'pipenv==2023.11.15'
pipenv install

if [ "${DRY_RUN:-false}" = "true" ]; then
  echo "Dry run enabled: using preview_reportable() (no TestRail calls)"

  PREVIEW_JSON=$(pipenv run python - <<'PY'
  import json
  from modules import testrail_integration as tri
  preview = {
    "windows": tri.preview_reportable("Windows"),
    "macos": tri.preview_reportable("Darwin"),
  }
  print(json.dumps(preview))
  PY
  )

  # Create an output named preview_json with the value coming from preview_reportable()
  printf "preview_json<<EOF\n%s\nEOF\n" "$PREVIEW_JSON" >> "$GITHUB_OUTPUT"

  # mark the boolean outputs as Preview (so downstream gating won't treat them as "True")
  echo "win=Preview" >> "$GITHUB_OUTPUT"
  echo "mac=Preview" >> "$GITHUB_OUTPUT"
else
  echo "Normal run: using reportable() checking reportability against TestRail."
  echo win=$(pipenv run python -c 'from modules import testrail_integration as tri; print(tri.reportable("Windows"))') >> "$GITHUB_OUTPUT"
  echo mac=$(pipenv run python -c 'from modules import testrail_integration as tri; print(tri.reportable("Darwin"))') >> "$GITHUB_OUTPUT"
  # leave preview_json empty
  echo "preview_json=" >> "$GITHUB_OUTPUT"
fi
