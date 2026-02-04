#!/bin/bash

# Expected env vars:
#   DRY_RUN
#   SPLIT
#   WIN_REPORTABLE
#   MAC_REPORTABLE
#   PREVIEW_JSON

# Logs
echo "DRY_RUN=${DRY_RUN}"
echo "Split=${SPLIT}"
echo "Windows reportable=${WIN_REPORTABLE}"
echo "macOS reportable=${MAC_REPORTABLE}"

# Job Summary
{
  echo "## Functional plan"
  echo ""
  echo "DRY_RUN: ${DRY_RUN}"
  echo "Split: ${SPLIT}"
  echo ""
  echo "### Decision"
  if [ "${DRY_RUN}" = "true" ]; then
    echo "Preview Mode: no TestRail calls, no downstream triggers"
  else
    echo "Normal Mode:"
  fi
  echo ""
  if [ "${WIN_REPORTABLE}" = "True" ]; then
    echo "Would trigger Test-Windows (test_set=${SPLIT})"
  else
    echo "Won't trigger Test-Windows"
  fi

  if [ "${MAC_REPORTABLE}" = "True" ]; then
    echo "Would trigger Test-MacOS (test_set=${SPLIT})"
  else
    echo "Won't trigger Test-MacOS (mac_reportable=${MAC})"
  fi

  if [ "${DRY_RUN}" = "true" ] && [ -n "${PREVIEW_JSON}" ]; then
    echo ""
    echo "### Preview details (JSON)"
    echo '```json'
    echo "${PREVIEW_JSON}"
    echo '```'
  fi
} >> "${GITHUB_STEP_SUMMARY}"
