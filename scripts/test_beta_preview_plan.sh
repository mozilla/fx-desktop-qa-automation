#!/bin/bash

# Expected env vars:
#   DRY_RUN
#   WIN_SPLITS    JSON array of functional splits to run on Windows, e.g. ["functional1"]
#   MAC_SPLITS    JSON array of functional splits to run on macOS
#   PREVIEW_JSON

WIN_SPLITS="${WIN_SPLITS:-[]}"
MAC_SPLITS="${MAC_SPLITS:-[]}"

# Logs
echo "DRY_RUN=${DRY_RUN}"
echo "Windows splits to run=${WIN_SPLITS}"
echo "macOS splits to run=${MAC_SPLITS}"

# Job Summary
{
  echo "## Plan"
  echo ""
  echo "DRY_RUN: ${DRY_RUN}"
  echo ""
  echo "### Decision"
  if [ "${DRY_RUN}" = "true" ]; then
    echo "Preview Mode: no TestRail calls, no downstream triggers"
  else
    echo "Normal Mode:"
  fi
  echo ""
  if [ "${WIN_SPLITS}" != "[]" ] && [ -n "${WIN_SPLITS}" ]; then
    echo "Would trigger Test-Windows for splits: ${WIN_SPLITS}"
  else
    echo "Won't trigger Test-Windows (no uncovered splits)"
  fi

  if [ "${MAC_SPLITS}" != "[]" ] && [ -n "${MAC_SPLITS}" ]; then
    echo "Would trigger Test-MacOS for splits: ${MAC_SPLITS}"
  else
    echo "Won't trigger Test-MacOS (no uncovered splits)"
  fi

  if [ "${DRY_RUN}" = "true" ] && [ -n "${PREVIEW_JSON}" ]; then
    echo ""
    echo "### Preview details (JSON)"
    echo '```json'
    echo "${PREVIEW_JSON}"
    echo '```'
  fi
} >> "${GITHUB_STEP_SUMMARY}"