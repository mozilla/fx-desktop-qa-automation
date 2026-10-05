# Running STARfox against your Firefox build

STARfox is Mozilla QA's Firefox desktop smoke/functional suite. This page is for
**Firefox development and RelEng teams** who want to run it against a build of their
own and get machine-readable results back.

You do **not** need a TestRail account, Mozilla QA credentials, or any knowledge of
how the tests are written. You give us a build; you get back JUnit XML and a
versioned `summary.json`.

> Designing or changing the service? See [TESTING_AS_A_SERVICE.md](TESTING_AS_A_SERVICE.md).

---

## Pick a model

| | **A. Call it from your own CI** | **B. Ask our repo to run it** |
|---|---|---|
| How | `uses:` our workflow from your repo | Actions UI, or a REST API call |
| Runs on | **your** runners, your minutes | our runners |
| Results land in | your workflow run | our run; you fetch via API |
| Needs | a GitHub Actions workflow | nothing, or a token for the API |
| Best for | RelEng pipelines, teams with CI | ad-hoc checks, "just tell me if it's broken" |

**Model A is recommended** where you have CI. It costs us nothing, costs you only
runner minutes you already control, and no secrets cross the boundary.

---

## Model A — call it from your own repository

```yaml
jobs:
  fx-smoke:
    uses: mozilla/fx-desktop-qa-automation/.github/workflows/main.yml@main
    with:
      # REQUIRED for cross-repo use. Without these, the workflow would check out
      # *your* repository and fail to find the test suite.
      starfox_repository: mozilla/fx-desktop-qa-automation
      starfox_ref: main          # pin to a tag once v1 is cut; see Versioning

      win_installer_link: https://example/firefox-setup.exe
      mac_installer_link: https://example/Firefox.dmg
      linux_tarball_link: https://example/firefox.tar.xz
      test_set: smoke
      fail_on: non-flaky-failure
      request_id: my-team-build-42
```

Omit a `*_link` to skip that platform. Supply no secrets — every integration that
needs one (TestRail, BigQuery, Slack) detects their absence and skips.

Gate a later job on the result:

```yaml
  gate:
    needs: fx-smoke
    if: ${{ needs.fx-smoke.outputs.windows_verdict != 'pass' }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Smoke failed - blocking"; exit 1
```

Outputs available: `windows_verdict`, `macos_verdict`, `linux_verdict`.

> **Why `main.yml` and not the `fx-test-request.yml` façade?** Expressions are not
> permitted in a `uses:` value, so a nested reusable workflow cannot forward a
> dynamic ref. Calling `main.yml` directly keeps your pin honest. The trade-off is
> that you skip the façade's up-front request validation, so **supply explicit URLs
> and a `test_set` you know exists** — a typo surfaces as an empty or failed run
> rather than a fast, clear error.

---

## Model B — ask our repo to run it

### From the Actions UI

**Actions → Fx Test Request → Run workflow.** Fill in either `firefox_version` *or*
the direct URLs, then read the job summary when it finishes.

### From the API

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/mozilla/fx-desktop-qa-automation/dispatches \
  -d '{
        "event_type": "fx-test-request",
        "client_payload": {
          "firefox_version": "155.0.1",
          "test_set": "smoke",
          "platforms": "win,linux",
          "fail_on": "non-flaky-failure",
          "request_id": "releng-155.0.1"
        }
      }'
```

**Finding your run.** The API returns `204 No Content` with no run id — a GitHub
limitation, not ours. Your `request_id` is embedded in the run name, so poll for it:

```bash
gh run list --workflow fx-test-request.yml --json databaseId,name,status,conclusion \
  | jq '.[] | select(.name | contains("releng-155.0.1"))'
```

Then download results:

```bash
gh run download <run-id> --name fx-results-windows
```

---

## The request

| Field | Default | Notes |
|---|---|---|
| `firefox_version` | — | e.g. `155.0.1`, `153.0esr`, `156.0b2`. We resolve the highest `buildN` from archive.mozilla.org. **Mutually exclusive** with the `*_link` fields. |
| `win_installer_link` | `''` | Direct URL, `.exe` or `.zip` |
| `mac_installer_link` | `''` | Direct URL, `.dmg` |
| `linux_tarball_link` | `''` | Direct URL, `.tar.xz` |
| `channel` | `beta` | `beta`/`rc`/`esr`/`nightly`/`custom`. Metadata only — does not change test selection. Inferred from `firefox_version` when you don't set it. |
| `test_set` | `smoke` | `smoke` (~72 tests), `functional1`, `functional2`, `functional3`, `nightly`. Validated against `manifests/key.yaml`. |
| `platforms` | `win,mac,linux` | Comma-separated subset. Pay for only what you need. |
| `fail_on` | `non-flaky-failure` | See below. |
| `request_id` | auto | Opaque correlation id. Echoed into every `summary.json` and into the run name. |

Machine-readable: [`schemas/test-request-v1.json`](schemas/test-request-v1.json).

### `fail_on`

| Value | Request fails when |
|---|---|
| `non-flaky-failure` *(default)* | a test failed outright, or the run broke |
| `any-failure` | anything less than all-green, flakes included |
| `never` | never — you just want the data |

Start with the default. A gate that false-fails on a flake gets switched off and
never switched back on.

---

## What you get back

One artifact per platform, named `fx-results-windows` / `fx-results-macos` /
`fx-results-linux`, retained **30 days**:

```
summary.json   the contract - verdict, totals, failures, build metadata
junit.xml      headless + headed merged; feed it to any CI test reporter
```

A separate `artifacts-<os>` artifact holds the full debug bundle — HTML report,
per-test browser logs, screenshots. Reach for that when triaging, not when gating.

### Reading `summary.json`

```jsonc
{
  "schema_version": "1.0",
  "request_id": "releng-155.0.1",
  "verdict": "flaky",                  // pass | flaky | fail | infra_error
  "gate":  { "fail_on": "non-flaky-failure", "failed": false },
  "build": { "channel": "rc", "version": "155.0.1-build2", "platform": "windows",
             "machine_config": "Windows 11 x86_64", "source_url": "..." },
  "selection": { "test_set": "smoke", "test_count": 72, "suites": ["tabs", "..."] },
  "totals": { "passed": 71, "failed": 0, "error": 0, "skipped": 0,
              "xfailed": 0, "xpassed": 0, "flaky": 1 },
  "failures": [ { "nodeid": "...", "suite": "downloads", "outcome": "flaky",
                  "flaky": true, "message": "passed on retry", "duration_s": 42.1 } ],
  "infra_errors": []
}
```

**Gate on `gate.failed`.** It already applies your `fail_on` policy, so you don't
have to re-implement the rules.

The four verdicts are deliberately distinct:

| Verdict | Means | Your move |
|---|---|---|
| `pass` | all green | ship |
| `flaky` | everything passed, some only on retry | usually ship; worth a look if it recurs |
| `fail` | a test failed outright | investigate — likely a real regression |
| `infra_error` | **the run broke, so it says nothing about your build** | re-run; tell us if it persists |

That last distinction matters: a 404 on your installer URL or a geckodriver download
failure is not a signal about your code, and `summary.json` says so explicitly in
`infra_errors` rather than looking like a test failure.

Machine-readable: [`schemas/result-summary-v1.json`](schemas/result-summary-v1.json).

### A note on flakes

CI runs each test with up to 3 retries. A test that fails and then passes is counted
as **flaky**, not as a pass — it appears in `totals.flaky` and in `failures` with
`"flaky": true`.

Be aware that `junit.xml` *cannot* express this: it records a retried-then-passed
test as an ordinary pass. If you care about flake rate, read `summary.json`.

---

## Versioning

The façade's inputs and `summary.json`'s shape are the contract. `main.yml`'s
internals are not, and change without notice.

- **Pin to a tag** (`@v1`) once tags are cut, not to a branch.
- `v1` moves forward compatibly: fields may be **added**, never removed or retyped.
- A breaking change ships as `v2`, with `v1` kept working for at least one quarter.
- `report.json` inside the debug bundle is raw pytest-json-report output. Useful for
  debugging, explicitly **not** part of the contract — it changes when we bump the
  plugin.

> **Status:** no tags exist yet. Until `v1` is cut, pin `@main` and expect occasional
> churn.

---

## Limits and caveats

- **Triage is yours.** We return artifacts and a verdict; we don't currently
  investigate failures in your run. The `flaky` / `infra_error` classification exists
  precisely so most questions answer themselves. *(Proposed for v1 and not yet
  ratified — see TESTING_AS_A_SERVICE.md §9.1.)*
- **No synchronous API.** Dispatch is fire-and-forget; poll for your run.
- **macOS is the expensive platform.** Trim `platforms` when you don't need it.
- **No per-tenant quota yet.** Be considerate with `functional*` and `nightly`, which
  are several times the size of `smoke`.
- **Firefox desktop only.** No mobile, no Thunderbird.
- **Tenant runs never write to TestRail**, and never write to QA's BigQuery or Slack.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `Invalid test request: unknown test_set 'smoek'` | Typo. The error lists every valid split. |
| `Invalid test request: ... mutually exclusive` | You gave both `firefox_version` and a `*_link`. Pick one. |
| `candidate build X has no artifact for: mac` | That candidate didn't publish that platform. Narrow `platforms`. |
| `verdict: infra_error`, empty `failures` | The run broke before testing. Check `infra_errors`; re-run. |
| Workflow can't find `tests/` | Model A without `starfox_repository` / `starfox_ref`. |

Questions: file an issue on
[mozilla/fx-desktop-qa-automation](https://github.com/mozilla/fx-desktop-qa-automation/issues).
