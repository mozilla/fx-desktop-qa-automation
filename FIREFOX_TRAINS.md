# Automated Firefox test branch management

## Active states

| Firefox state | Automation branch |
|---|---|
| Current Beta | `main` |
| Current Nightly | `nightly` |
| Released major `N` | `firefoxN` |

Firefox artifact parsing remains version-aware: Nightly (`aN`), Beta (`bN`),
Release, dot-release, and ESR versions are recognized. Beta and DevEdition test
execution resolves to `main`; Nightly resolves to `nightly`; released builds
resolve to their numbered `firefoxN` branch. RC uses `firefoxN` after that
release branch exists and falls back to `main` before the first transition.

## Automatic train transition

`.github/workflows/sync-firefox-branches.yml` supports three triggers:

- a production `repository_dispatch` API event named
  `firefox-beta-promoted`, with the promoted Beta version and optional outgoing
  release major in `client_payload`;
- a manual `workflow_dispatch` request, which defaults to dry-run mode;
- an hourly fallback that detects the first Beta (`N.0b1`) in the Mozilla
  candidate archive.

The production API event performs the transition without inheriting the manual
dry-run default. It requires `client_payload.promoted_beta_version`; optional
fields are `released_major` and `retention`.

On the first run, if `nightly` does not exist, it is bootstrapped from `main`
without performing a promotion. An explicit promotion API request is blocked
until this bootstrap has completed, so an event cannot be silently consumed
without performing its requested transition.

For a Nightly-to-Beta promotion, the workflow:

1. captures the current `main` commit as `firefoxN`;
2. merges the current Beta fixes from `main` into `nightly`;
3. atomically updates `nightly` and `main` to the promoted commit while
   creating `firefoxN` from the outgoing `main`;
4. validates all three remote refs;
5. deletes expired numbered branches, retaining the newest two by default.

The atomic push makes the transition all-or-nothing. No force-push is used.
If the Beta and Nightly histories cannot be merged automatically, or branch
protection rejects the update, the workflow fails without partially changing
the three train branches. Repeated promotion requests are safe because the
expected `firefoxN` branch acts as the completed-transition marker.

Manual executions default to dry-run mode. Production API events and scheduled
fallbacks perform real transitions. Branch retention is configurable, and
deletion is restricted to names matching `firefoxNNN`.

## Nightly tests

`.github/workflows/nightly-tests.yml` provides a manual entry point for testing
the `nightly` automation branch. Buildhub metadata resolves each platform to an
immutable, dated Mozilla archive URL before execution. The workflow uses those
pinned artifacts for both the `smoke` and `nightly` manifest splits on Windows
and macOS. Test scheduling and sprint cadence are intentionally managed outside
this branch-management implementation.

## Main implementation files

- `scripts/firefox_train.py` parses Firefox versions and resolves their active
  automation branch.
- `scripts/firefox_branches.py` creates deterministic lookup, bootstrap,
  promotion, idempotency, and retention plans.
- `scripts/collect_executables.py` discovers Nightly builds and pins exact
  candidate artifacts across platforms. Nightly resolution reads one archive
  listing and returns dated Buildhub download URLs as a single build set.
- `.github/workflows/resolve-firefox-branch.yml` selects the automation ref and
  Firefox artifacts before a test workflow starts. It pins the selected branch
  to an immutable commit SHA so a concurrent promotion cannot change the
  automation code after artifact resolution.
- `.github/workflows/sync-firefox-branches.yml` performs train promotion and
  retention.
- `scripts/tests_firefox_train.py` covers version parsing, routing, promotion,
  and retention behavior.
- `.github/workflows/firefox-branch-management-ci.yml` runs the focused unit,
  lint, and formatting checks for pull requests and active-train updates.
