#!/bin/bash
# Functional pipeline only. Run from the Check-Beta-Version job.
# Unlike check_reportable.sh (which emits a single win/mac boolean for the
# smoke/rc/devedition/l10n flows), this enumerates the functional splits that
# still lack coverage for each platform on the latest build, so the run jobs can
# fan out over them via a matrix instead of guessing a split by the hour.
#
# Check-Beta-Version.outputs =>
#  win_splits:   list of functional splits needing Windows coverage, e.g. ["functional1"]
#  mac_splits:   list of functional splits needing macOS coverage
#  preview_json: "" | "{...json...}"

pip3 install 'pipenv==2023.11.15'
pipenv install

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

  printf "preview_json<<EOF\n%s\nEOF\n" "$PREVIEW_JSON" >> "$GITHUB_OUTPUT"

  # No downstream triggers in preview mode.
  echo 'win_splits=[]' >> "$GITHUB_OUTPUT"
  echo 'mac_splits=[]' >> "$GITHUB_OUTPUT"
else
  echo "Normal run: computing uncovered functional splits per platform against TestRail."

  WIN_SPLITS=$(pipenv run python -m scripts.reportable_splits --platform Windows --format json 2>/tmp/win_stderr)
  echo "win_splits=${WIN_SPLITS:-[]}" >> "$GITHUB_OUTPUT"

  MAC_SPLITS=$(pipenv run python -m scripts.reportable_splits --platform Darwin --format json 2>/tmp/mac_stderr)
  echo "mac_splits=${MAC_SPLITS:-[]}" >> "$GITHUB_OUTPUT"

  {
    echo "### functional split coverage gate"
    echo ""
    echo "| platform | splits to run | stderr (tail) |"
    echo "|---|---|---|"
    echo "| Windows | \`${WIN_SPLITS:-[]}\` | <details><summary>show</summary><pre>$(tail -c 4000 /tmp/win_stderr)</pre></details> |"
    echo "| Darwin | \`${MAC_SPLITS:-[]}\` | <details><summary>show</summary><pre>$(tail -c 4000 /tmp/mac_stderr)</pre></details> |"
  } >> "$GITHUB_STEP_SUMMARY"

  echo "preview_json=" >> "$GITHUB_OUTPUT"
fi
