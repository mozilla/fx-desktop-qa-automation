#!/bin/bash
# This script is intended to be run from the Check-Beta-Version job.
# Check-Beta-Version.outputs =>
#  win: "True" | "False" | "Preview",
#  mac: "True" | "False" | "Preview",
#  preview_json: "" | "{...json...}"

if [ "${DRY_RUN}" = "true" ]; then
  echo "Dry run enabled: generating preview plan - using preview_reportable() (no TestRail calls)"

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

  echo "win=Preview"
  echo "mac=Preview"

  echo "win=Preview" >> "$GITHUB_OUTPUT"
  echo "mac=Preview" >> "$GITHUB_OUTPUT"
else
  echo "Normal run: using reportable() checking reportability against TestRail."

  WIN_STDOUT=$(pipenv run python -c 'from modules import testrail_integration as tri; print(tri.reportable("Windows"))' 2>/tmp/win_stderr)
  WIN_EXIT=$?

  echo "win=${WIN_STDOUT}"
  echo "win=${WIN_STDOUT}" >> "$GITHUB_OUTPUT"

  MAC_STDOUT=$(pipenv run python -c 'from modules import testrail_integration as tri; print(tri.reportable("Darwin"))' 2>/tmp/mac_stderr)
  MAC_EXIT=$?

  echo "mac=${MAC_STDOUT}"
  echo "mac=${MAC_STDOUT}" >> "$GITHUB_OUTPUT"

  {
    echo "### reportable() gate decisions"
    echo ""
    echo "| platform | exit | stdout | stderr (tail) |"
    echo "|---|---|---|---|"
    echo "| Windows | ${WIN_EXIT} | \`${WIN_STDOUT:-<empty>}\` | <details><summary>show</summary><pre>$(tail -c 4000 /tmp/win_stderr)</pre></details> |"
    echo "| Darwin | ${MAC_EXIT} | \`${MAC_STDOUT:-<empty>}\` | <details><summary>show</summary><pre>$(tail -c 4000 /tmp/mac_stderr)</pre></details> |"
  } >> "$GITHUB_STEP_SUMMARY"

  # leave preview_json empty
  echo "preview_json=" >> "$GITHUB_OUTPUT"
fi

