# RFC: STARfox as a Service

**Status:** Draft — for discussion
**Author:** Arash Eghtesadi
**Date:** 2026-10-05
**Branch:** `arash/fx-dte-as-a-service`

> This is the engineering design. For the stakeholder-facing proposal — what we
> are doing, current status, and the decisions still open — see
> [STARfox-as-a-service.md](STARfox-as-a-service.md). For consumer instructions,
> see [SERVICE.md](SERVICE.md).

---

## 1. Summary

STARfox today is a closed loop: Mozilla QA schedules runs against Beta/DevEdition/RC, and results land in TestRail. This RFC proposes opening a **narrow, well-specified front door** so that Firefox development teams and RelEng can say:

> "Here is a Firefox build. Run your smoke suite on it. Give me machine-readable results."

and get an answer without talking to a human, without a TestRail account, and without learning the POM/BOM framework.

**Scope is deliberately one mode: bring-your-own-build (BYOB).** Consumers run *our existing suites* against *their build*. They do not contribute tests, and they do not vendor the framework. Those are separate conversations (§10).

The headline finding of the investigation behind this RFC: **most of the machinery already exists.** `main.yml` is already a reusable workflow that accepts installer URLs for all three platforms and already produces HTML + JSON reports. What's missing is not capability — it's a **contract**: a stable entrypoint, a stable result format, and a defined failure/triage policy.

---

## 2. Goals and non-goals

### Goals

| # | Goal |
|---|---|
| G1 | A development or RelEng team can trigger a Firefox desktop smoke run against an arbitrary build without QA involvement. |
| G2 | Results come back as **neutral artifacts** — JUnit XML, a versioned `summary.json`, and the existing HTML report — consumable by any CI system. |
| G3 | A consumer needs **zero Mozilla-QA credentials** (no TestRail, no BigQuery, no Slack). |
| G4 | The run clearly distinguishes *build regression* from *flake* from *infrastructure failure*. |
| G5 | The input contract is versioned, so we can evolve internals without breaking callers. |

### Non-goals (for this RFC)

- **Bring-your-own-tests.** Hosting other teams' test code brings ownership, review-load, and flake-budget problems that dwarf the BYOB work. Deferred.
- **Framework-as-a-library.** Packaging `modules/` for `pip install` is a different product with a different maintenance contract. Deferred.
- **Replacing TestRail** for our own scheduled runs. TestRail remains the system of record for QA's Beta/DevEdition/RC reporting. The service path simply doesn't write to it.
- **Mobile, Thunderbird, or non-Firefox-desktop targets.**
- **Triage-as-a-service.** We return results; §9 discusses who interprets them, which is the open question this RFC most wants answered.

---

## 3. Consumers and their jobs-to-be-done

| Consumer | What they want | Trigger style |
|---|---|---|
| **Firefox feature teams** | "Did my patch break anything outside my feature?" Run smoke on a try build before landing. | Ad-hoc, human-initiated, or from their own CI |
| **RelEng** | "Is this candidate build sane before we ship it?" Gate a release step on a smoke verdict. | Automated, pipeline-initiated, needs an exit code |
| **Engineering managers / release drivers** | "Give me a one-glance verdict on build N." | Ad-hoc, wants the HTML report and a summary |

All three are **internal to Mozilla**. That materially simplifies the security model: we can assume GitHub org membership and we are not defending against hostile callers. We are defending against *accidental* credential exposure and *accidental* pollution of QA's TestRail data.

---

## 4. What already works

An honest inventory, because the gap is smaller than it looks.

| Capability | Where | Notes |
|---|---|---|
| Reusable workflow with `workflow_call` | `.github/workflows/main.yml:6` | Already the right shape for a service API |
| Accepts arbitrary build URLs for all 3 platforms | `main.yml` (`win_installer_link`, `mac_installer_link`, `linux_tarball_link`) | The download/install machinery exists. **Correction:** these were originally declared on `workflow_dispatch` *only*, so a `workflow_call` caller passing them was rejected with "Invalid input". Fixed in Phase 2 by declaring them on `workflow_call` too — until then the BYOB path was unreachable from another repo. |
| Linux job already gated on BYOB input | `main.yml:509-510` (`Smoke-Linux`, `if: inputs.linux_tarball_link`) | Linux coverage comes free with BYOB |
| Candidate-build resolution from archive.mozilla.org | `.github/workflows/run-firefox-candidate.yml` | A working self-serve façade; validates version, finds latest `buildN`, dispatches |
| Test selection vocabulary | `manifests/key.yaml` + `scripts/choose_test_split.py` | Splits: `smoke` (72), `functional1/2/3` (183/112/119), `nightly` (263), `ci` (10), `ci-extended` (11), `glean` (5) |
| Per-platform skip/status manifest | `manifests/key.yaml` | `result:` can be per-OS, so selection already respects platform |
| JSON + HTML reports | `config/ci_pyproject.toml:15` → `artifacts/report.json`, `artifacts/report.html` | pytest-json-report + pytest-html already installed |
| Artifact upload | `main.yml:317-322`, `:502-507`, `:622-626` | `artifacts-win` / `artifacts-mac` / `artifacts-linux` |
| **TestRail is already cleanly gated** | `conftest.py:360-365` | `TESTRAIL_REPORT` falsy → integration skipped entirely, before any network call. The decoupling we feared is largely done. |
| Dry-run / preview modes | `main.yml` `dry_run`, `ci-dispatch.yml` `preview_only` | Good precedent for safe exploration |
| Secrets are all optional on `workflow_call` | `main.yml:30-46` (`required: false`) | Callers aren't *forced* to supply them |

**Conclusion:** we are not building a service. We are putting a contract and a façade on one that already runs.

---

## 5. Gaps

Ordered by how hard they block G1–G5.

### 5.1 Blockers

**B1 — Cross-repo reuse is broken by the checkout steps.**
GitHub allows a public repo's reusable workflow to be called from another repo (`uses: mozilla/fx-desktop-qa-automation/.github/workflows/main.yml@v1`). But a called reusable workflow runs with the **caller's** repository as the default checkout target. Every `actions/checkout` in `main.yml` (`:90`, `:337`, `:514`, `:637`) omits `repository:` and `ref:`, so a cross-repo call would check out *the caller's code* and then fail to find `tests/`, `scripts/`, and `manifests/`.
*This single omission is what prevents the most valuable delivery model from working today.*

**B2 — No JUnit XML.** Confirmed absent: no `--junitxml` in `pyproject.toml:193` or any of the seven `config/*_pyproject.toml` variants. JUnit XML is the lingua franca every consuming CI already parses. G2 is unmet without it.

**B3 — Unconditional credentialed steps will fail for credential-less callers.** `Auth to Google Cloud` (`main.yml:298-303`, `:483-488`) runs on `if: always() && inputs.dry_run != true` and feeds `secrets.GC_CREDENTIAL_STABILITY` into `google-github-actions/auth`. A caller who doesn't pass that secret gets an empty `credentials_json` and a hard job failure *after* their tests already passed. Same pattern for the BigQuery upload step and for `notifier.py` in `Use-Artifacts` (`main.yml:670-679`).

**B4 — No result contract.** `artifacts/report.json` is pytest-json-report's internal shape: large, unversioned, and free to change when we bump the plugin. Nothing expresses the things a consumer actually needs — which build, which channel, which platform, what the *verdict* is, and which failures were flakes.

**B5 — Flaky-vs-real is invisible, and it poisons the verdict.** CI addopts carry `--reruns 3` (`config/ci_pyproject.toml:15`). A test that fails twice and passes on the third attempt is currently indistinguishable, at the job-exit-code level, from a clean pass — and conversely a single genuine failure fails the entire request with no nuance. RelEng cannot gate on this (G4).

**B6 — Infrastructure failure is indistinguishable from test failure.** If geckodriver fails to download or the installer URL 404s, the job fails. A consumer gating a release step cannot tell "your build is broken" from "our CI had a bad day." This is the fastest way to lose a consumer's trust.

### 5.2 Friction

**F1 — Two pytest runs per platform, two reports.** Each platform runs headless (`report.json`) and then headed (`report_headed.json`, `main.yml:267-296`, which uses `always()` so it runs even after a headless failure). Nothing merges them. A consumer gets two partial pictures.

**F2 — No versioning.** The repo has **zero git tags**. Callers would have to pin `@main` and ride every change. We cannot promise a stable contract without release tags.

**F3 — Selection is by split only.** `STARFOX_SPLIT` picks a maintained bucket. There is no "run the `downloads` and `pdf_viewer` suites." (Note: `STARFOX_CATEGORY` / `TestKey.gather_category` at `manifests/testkey.py:314` is a *result-status* filter — `pass`/`flaky`/`unstable` — not a feature taxonomy. No feature or owner taxonomy exists in `key.yaml`.)

**F4 — No ownership metadata.** No `CODEOWNERS`; `.github/` contains only `pull_request_template.md`. When a tenant run fails, there is no encoded answer to "whose test is this?"

**F5 — No at-a-glance result.** Nothing writes to `$GITHUB_STEP_SUMMARY`. Every consumer must download a zip to learn anything.

**F6 — `Use-Artifacts` hard-depends on Windows + macOS.** `main.yml:630-635` has `needs: [Test-Windows, Test-MacOS]`, so a Linux-only or single-platform request can't use that aggregation path.

---

## 6. Proposed design

### 6.1 Two delivery models — ship both, in order

**Model A — Reusable workflow (`uses:`). Recommended first.**

The consumer adds ~10 lines to their own repo:

```yaml
jobs:
  fx-smoke:
    uses: mozilla/fx-desktop-qa-automation/.github/workflows/main.yml@main
    with:
      starfox_repository: mozilla/fx-desktop-qa-automation
      starfox_ref: main
      win_installer_link: ${{ needs.build.outputs.win_url }}
      test_set: smoke
      fail_on: non-flaky-failure
```

| Property | Consequence |
|---|---|
| Runs on the **caller's** runners | Their macOS minutes, their budget, their queue. Solves cost allocation for free. |
| Uses the caller's `GITHUB_TOKEN` | We grant nothing. No secrets cross the boundary. |
| Artifacts land in the caller's run | They already have the retention and access policy they want. |
| Requires fixing **B1** | ~4 lines of YAML. |

This is the highest-leverage change in the whole RFC: it turns a cost-and-access problem into a non-problem. It requires the repo to be public, which it appears to be (mozilla org, MPL `LICENSE`, unauthenticated clone URL) — *verify before relying on it.*

**Model B — Hosted dispatch.** For consumers with no CI of their own (an engineer who just wants an answer) and for the `run-firefox-candidate.yml`-style convenience path. They `workflow_dispatch` (or `repository_dispatch`) into our repo; we run it on our runners; they fetch artifacts via the GitHub API.

| Property | Consequence |
|---|---|
| Runs on **our** runners | We absorb macOS cost. Needs a quota/concurrency policy. |
| Needs write-ish access to our repo | Org members with write, or a narrowly-scoped GitHub App. |
| Results fetched by API | Needs documented artifact names + a polling recipe. |

Ship A first because it's ~a day of work and has no ongoing cost. Ship B second for reach.

### 6.2 The front door: `.github/workflows/fx-test-request.yml`

A **thin, versioned, documented** wrapper over `main.yml`. The point of a separate file is that `main.yml` is 25 KB of QA-internal logic that we want to keep refactoring freely; the façade is the only thing we promise not to break.

Proposed input contract (**v1**):

| Input | Type | Default | Description |
|---|---|---|---|
| `firefox_version` | string | — | e.g. `155.0.1`, `153.0esr`, `156.0b2`. If given, we resolve candidate URLs ourselves (reuse `run-firefox-candidate.yml` logic). Mutually exclusive with the `*_link` inputs. |
| `win_installer_link` | string | `''` | Direct URL. `.exe` or `.zip`. |
| `mac_installer_link` | string | `''` | Direct URL. `.dmg`. |
| `linux_tarball_link` | string | `''` | Direct URL. `.tar.xz`. |
| `channel` | enum | `beta` | `beta` \| `rc` \| `esr` \| `nightly` \| `custom`. Metadata only; affects naming, not selection. |
| `test_set` | enum | `smoke` | `smoke` \| `functional1` \| `functional2` \| `functional3` \| `nightly`. Validated against `manifests/key.yaml` splits. |
| `platforms` | string | `win,mac,linux` | Comma-separated subset. Lets a caller pay for only what they need. |
| `fail_on` | enum | `non-flaky-failure` | `any-failure` \| `non-flaky-failure` \| `never`. Controls the workflow's exit status. Addresses **B5**. |
| `request_id` | string | `''` | Opaque caller-supplied correlation ID, echoed into `summary.json`. |

Deliberately **not** exposed in v1: `dry_run` (internal), `is_pull_request` (internal), anything TestRail. TestRail reporting is **off, unconditionally**, on this path — `TESTRAIL_REPORT=false`, which `conftest.py:360` already honours. No tenant run can pollute QA's plans.

Outputs: `verdict`, `summary_json_artifact`, `run_url`, plus per-platform pass/fail counts.

### 6.3 The result contract: `results/v1/`

Every run produces one bundle per platform, uploaded as `fx-results-<platform>`:

```
results/v1/
  summary.json      # versioned, hand-authored schema — the contract
  junit.xml         # merged headless + headed, for generic CI ingestion
```

This is **additive**: the existing `artifacts-<os>` upload is untouched and keeps
serving as the debug bundle (HTML report, raw `report.json`, per-test chrome/content
logs, screenshots). Two artifacts, two audiences — a consumer gating a pipeline
downloads a few KB, while a human triaging a failure downloads the full zip. It also
means no existing consumer of `artifacts-win` / `artifacts-mac` / `artifacts-linux`
breaks, which a rename would have risked.

`summary.json`:

```jsonc
{
  "schema_version": "1.0",
  "request_id": "releng-155.0.1-build2",
  "verdict": "pass",                 // pass | flaky | fail | infra_error
  // what the caller should actually gate on: the verdict judged against fail_on
  "gate":  { "fail_on": "non-flaky-failure", "failed": false },
  "run":   { "url": "...", "backend": "github-actions" },
  "build": {
    "channel": "rc", "version": "155.0.1-build2",
    "source_url": "...", "platform": "windows",
    "os_version": "Windows 11", "arch": "x86_64"
  },
  "selection": { "test_set": "smoke", "test_count": 72, "suites": ["tabs", "downloads"] },
  "totals": {
    "passed": 70, "failed": 1, "error": 0,
    "skipped": 1, "xfailed": 0, "flaky": 1, "reruns": 3
  },
  "failures": [{
    "nodeid": "tests/downloads/test_download_pdf.py::test_download_pdf",
    "suite": "downloads", "message": "TimeoutException: ...",
    "duration_s": 42.1, "attempts": 4, "flaky": false,
    "artifacts": ["logs/test_download_pdf_chrome.txt", "screenshots/..."]
  }],
  "infra_errors": []
}
```

Three design decisions worth defending:

1. **Both JUnit *and* `summary.json`.** JUnit so that every existing CI test-reporter just works with no code. `summary.json` because JUnit cannot express `channel`, `build.version`, `flaky`, or `verdict` — exactly the fields a RelEng gate needs.
2. **`verdict` is computed, not inferred from the exit code.** It applies the `fail_on` policy and separates `flaky` (passed on rerun) and `infra_error` (we broke, not you) from `fail`. This directly resolves **B5** and **B6**.
3. **`report.json` is shipped but declared non-contractual.** It's genuinely useful for debugging and costs nothing to include; saying so in writing stops it becoming a de-facto API.

New script: **`scripts/build_result_bundle.py`** — reads `artifacts/report.json` + `artifacts/report_headed.json`, merges them (**F1**), classifies reruns as flake (**B5**), reads build metadata from the existing env vars (`FX_VERSION`, `FX_CHANNEL`), emits `summary.json` + `junit.xml`, and writes a markdown table to `$GITHUB_STEP_SUMMARY` (**F5**). Schema published at `schemas/result-summary-v1.json`.

### 6.4 Worked examples

**RelEng gating a release step (Model A):**

```yaml
  smoke:
    uses: mozilla/fx-desktop-qa-automation/.github/workflows/main.yml@main
    with:
      starfox_repository: mozilla/fx-desktop-qa-automation
      starfox_ref: main
      win_installer_link: ${{ needs.resolve.outputs.win_url }}
      channel: rc
      fail_on: non-flaky-failure
      request_id: release-${{ inputs.candidate }}
  gate:
    needs: smoke
    if: needs.smoke.outputs.windows_verdict != 'pass'
    runs-on: ubuntu-latest
    steps: [{ run: 'echo "Smoke failed — blocking ship"; exit 1' }]
```

**A feature team checking a try build (Model B):** they open Actions → *Fx Test Request* → paste their try artifact URLs → read the job summary. No YAML, no credentials.

---

## 7. Phased plan

### Phase 0 — Unblock. ✅ **Implemented.** Makes BYOB genuinely usable.

| # | Change | How |
|---|---|---|
| 0.1 | Cross-repo checkout (**B1**) | Added optional `starfox_repository` / `starfox_ref` `workflow_call` inputs, wired into all four checkout steps as `repository: ${{ inputs.starfox_repository \|\| github.repository }}` / `ref: ${{ inputs.starfox_ref }}`. Both default to `''`, so same-repo and fork runs keep their exact current behaviour (triggering SHA); only cross-repo callers set them. |
| 0.2 | Guard credentialed steps (**B3**) | Added `HAS_BQ_CREDS` / `HAS_SLACK_CREDS` to the workflow-level `env` block, gating the three `Auth to Google Cloud` steps, the three BigQuery uploads, and the Slack notify step. |
| 0.3 | JUnit XML (**B2**) | `--junitxml=artifacts/junit.xml` in the 3 headless CI configs; `artifacts/junit_headed.xml` in the 3 headed ones, so the headed pass can't clobber the headless one. |
| 0.4 | Single-platform runs (**F6**) | `Use-Artifacts` now uses `!cancelled()` instead of implicit `success()`, both downloads are `continue-on-error`, and the listing step tolerates an absent directory. |
| 0.5 | Artifact retention | `retention-days: 30` on all three uploads. |

Two notes for implementers:

- The Slack guard sits on the **step**, not the job. The `env` context is not available in a job-level `if:` (only `github`, `needs`, `vars`, `inputs`), so a job-level `env.HAS_SLACK_CREDS` check would silently evaluate false and disable notifications entirely.
- 0.4 has a **deliberate behaviour change**: `Use-Artifacts` previously inherited an implicit `success()`, so a failing Windows or macOS job skipped the Slack notification. It now runs on failure too. That is almost certainly the intent — a notifier that stays silent exactly when tests fail is not much of a notifier — but it is a change to production behaviour worth a reviewer's eye.

**Available today, pre-façade.** Until Phase 2 ships `fx-test-request.yml`, a cross-repo caller invokes `main.yml` directly and passes the two new inputs itself:

```yaml
  fx-smoke:
    uses: mozilla/fx-desktop-qa-automation/.github/workflows/main.yml@main
    with:
      starfox_repository: mozilla/fx-desktop-qa-automation
      starfox_ref: main            # pin to a tag once Phase 2.4 lands
      job_to_run: Test-Windows
      win_installer_link: https://.../firefox-setup.exe
      test_set: smoke
```

Results arrive as the `artifacts-win` / `artifacts-mac` / `artifacts-linux` artifacts, now containing `junit.xml` and `junit_headed.xml` alongside the existing HTML and JSON reports. Note that `test_set` must be set explicitly: left empty, `scripts/choose_test_split.py` falls through to its git-diff path and selects the `ci` split.

### Phase 1 — The contract. ✅ **Implemented.** Makes results consumable.

| # | Change | How |
|---|---|---|
| 1.1 | Result bundle builder | `scripts/build_result_bundle.py`. Merges the headless and headed JSON reports, classifies flakes, emits `summary.json` + a merged `junit.xml`, and writes a markdown table to `$GITHUB_STEP_SUMMARY` (**F1**, **F5**). |
| 1.2 | Published schemas + tests | `schemas/result-summary-v1.json` and `schemas/test-request-v1.json`; 32 unit tests in `scripts/tests/`. |
| 1.3 | Infra-error classification (**B6**) | Missing/unreadable report, zero tests collected, or a failed collector all become `infra_errors`, which force `verdict: infra_error`. Workflow steps can inject more via `--infra-error`. |
| 1.4 | `fail_on` policy | `fail_on` input on `main.yml` → `gate.failed` in the summary → an `Enforce result gate` step. |
| 1.5 | Caller-facing artifact | **Deviation:** added `fx-results-<platform>` *alongside* the existing `artifacts-<os>` rather than renaming it. Renaming risked breaking `notifier.py` and unknown downstream consumers for no benefit. |

Implementation notes worth a reviewer's attention:

- **The flake signal was verified against the real plugin, not assumed.** pytest-json-report records a test that fails then passes within `--reruns` as outcome `"rerun"` — *not* `"passed"` — while JUnit XML records it as an ordinary pass with no trace of the retries. So the verdict must come from the JSON and cannot come from the XML. `test_pytest_json_report_marks_a_retried_pass_as_rerun` pins this by running a real flaky test through pytest in a subprocess, so a plugin upgrade that changes the representation fails loudly instead of silently reclassifying every flake as a clean pass.
- **`fail_on` defaults to `never` on `main.yml`** so existing scheduled QA runs keep their current semantics (pytest's exit code decides, the gate is informational). The Phase 2 façade will default it to `non-flaky-failure`, which is the documented service default.
- **Gate enforcement is a separate step from bundle construction**, so the bundle is always uploaded even when the gate fails.
- A merge conflict between the headless and headed reports resolves to the *worse* outcome, so merging can never hide a failure.
- **A request schema was added beyond the original plan** (`schemas/test-request-v1.json`). The request previously existed only as workflow YAML inputs, which welds the contract to GitHub. Defining it as a backend-neutral document is what lets the execution plane move to Taskcluster later without consumers noticing — see §11.

### Phase 2 — The front door. ✅ **Implemented** (except 2.4). Makes it a service.

| # | Change | How |
|---|---|---|
| 2.1 | Façade workflow | `.github/workflows/fx-test-request.yml`, with the §6.2 contract on all three triggers. A `Resolve` job validates before any runner minutes are spent. |
| 2.2 | Candidate resolution | `scripts/resolve_test_request.py` replaces the inline bash in `run-firefox-candidate.yml`, now unit-tested (30 tests). |
| 2.3 | `platforms` filtering | Implemented **by omission**: `main.yml` starts a platform job only when that platform's link is non-empty, so dropping a URL drops the job. No change to `main.yml`'s job conditions was needed. |
| 2.4 | `v1` tag + release | ⬜ **Not done.** Policy is written up in `SERVICE.md`; cutting and pushing the tag is deliberately left until after review. |
| 2.5 | Consumer docs | `SERVICE.md`. |
| 2.6 | `repository_dispatch` | Supported as event type `fx-test-request`, reading `client_payload`. Not subject to the 10-input limit. |

Supporting changes to `main.yml`:

- **The BYOB inputs were declared on `workflow_dispatch` only.** `win_installer_link`,
  `mac_installer_link`, `linux_tarball_link` and `firefox_version` are now on
  `workflow_call` as well. This was a latent blocker: Phase 0's analysis (§4) took
  their presence as proof that BYOB already worked, but a cross-repo `uses:` caller
  passing them would have been rejected with "Invalid input". Model A did not
  actually function until this landed.
- `windows_verdict` / `macos_verdict` / `linux_verdict` exposed as `workflow_call`
  outputs — there was previously no way for a caller to read a result at all.
- `job_to_run` became optional, since the façade selects platforms purely by which
  installer links it passes.

**The constraint that shaped this phase: expressions are not permitted in `uses:`.**
A nested reusable workflow therefore cannot forward a dynamic ref, so a cross-repo
caller pinning `fx-test-request.yml@v1` would still get whatever `main.yml` the
façade hardcodes — silently breaking the pin. The resolution:

- **Model A (cross-repo) calls `main.yml` directly** with `starfox_repository` /
  `starfox_ref`. The pin is honest. The cost is skipping the façade's validation,
  which `SERVICE.md` states plainly.
- **Model B (dispatch) goes through the façade**, which runs inside this repo where
  the relative `uses:` resolves correctly.

This is worth knowing before anyone tries to "simplify" by routing Model A through
the façade.

**Two tenancy decisions made during implementation:**

- The façade does **not** use `secrets: inherit`. That would hand a tenant-triggered
  run our BigQuery and Slack credentials, making `HAS_BQ_CREDS` true and pushing
  tenant results into QA's `fx_qa_ci` table. Only `CI_WAF_TOKEN` is passed, which the
  FxA tests need.
- `Use-Artifacts` (the Slack notifier) is skipped whenever `request_id` is set, so
  service requests never notify the QA channel.

### Phase 3 — Operability (ongoing). Makes it sustainable.

| # | Change |
|---|---|
| 3.1 | Suite-level selection (`suites: downloads,pdf_viewer`) (**F3**) |
| 3.2 | `owners:` taxonomy in `manifests/key.yaml` + `CODEOWNERS` (**F4**) |
| 3.3 | Concurrency groups + quota for Model B |
| 3.4 | Service dashboard: request volume, verdict distribution, flake rate per tenant (extend `dashboards/`) |
| 3.5 | Published SLA and a documented triage path (§9) |

---

## 8. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| **Triage load swamps QA.** Every tenant failure becomes a QA question. This is the real cost of the service — not compute. | **High** | Verdict + flake classification answers most questions mechanically. Then: publish an explicit triage policy (§9) *before* announcing the service. |
| **Flake erodes trust fast.** A RelEng gate that false-fails once gets disabled permanently. | **High** | `fail_on: non-flaky-failure` as the default; track per-tenant flake rate (3.4) as a service KPI. |
| **macOS runner cost** under Model B. | Medium | Model A pushes cost to the caller. For Model B: quota, `platforms` input, and smoke-only by default. |
| **Contract ossification** — callers depend on internals we wanted to change. | Medium | The thin façade + `v1` tag + "`report.json` is non-contractual" declaration are all defences against exactly this. |
| **Accidental TestRail pollution** from a tenant run. | Medium | Hard-code `TESTRAIL_REPORT=false` on the service path; `conftest.py:360` already short-circuits before any network call. Add a test asserting it. |
| **Suite drift** — `smoke` changes meaning and a caller's baseline moves. | Low | Record `selection.test_count` and the resolved suite list in `summary.json` so drift is visible in the artifact itself. |

---

## 9. Open questions

These need decisions from stakeholders, not from the implementation.

1. **Who triages a failure in a tenant run?** The most important question in this document. Options: (a) the consuming team, with QA providing only artifacts; (b) QA triages on a best-effort basis; (c) QA triages within an SLA. This determines whether the service is cheap or expensive. **Recommendation: (a) for v1**, with the flake/infra classification doing the heavy lifting, and revisit once we see real volume.
2. **Model A or Model B first?** This RFC recommends A, on cost-allocation grounds. Does RelEng's pipeline live somewhere that can call a GitHub reusable workflow?
3. **Is the repo definitely public?** Model A depends on it. Needs a one-line confirmation.
4. **Which build sources are in scope?** `archive.mozilla.org` candidates are trivially supported today. Do we need Taskcluster try-build artifacts, which may require authentication?
5. **Does any tenant run ever write to TestRail?** Recommendation: no, never, in v1.
6. **What's the support commitment?** Best-effort, or a real SLA with an on-call rotation? Announce accordingly — an unstated SLA will be assumed to be 24/7.
7. **Do we need a `v1` → `v2` deprecation policy now,** or is "we'll tag and tell you" enough for internal consumers?

---

## 10. Deferred: the other two models

Recorded here so they aren't re-litigated from scratch.

**Bring-your-own-tests.** Would require: an ownership model, a review-capacity commitment from QA, per-tenant flake budgets with an eviction policy, and a sandboxing story for tenant code running with our secrets. The infrastructure is the easy part; the governance is not. Revisit once BYOB has real users and we understand the demand.

**Framework-as-a-library.** Would require: extracting `modules/` from the repo root, a stable public API (`BasePage` is currently free to change — see the PR checklist, which only asks that changes be *noted*), semantic versioning, and a release process. Highest long-term leverage, highest cost. Revisit if multiple teams ask for it specifically.

---

## 11. Is GitHub Actions the right substrate for a *cloud* service?

Raised during review; recorded because it determines how far this design scales.

**Short answer: yes for now, provided we keep one distinction straight — a workflow
file is not an API.** Phases 0–2 produce a request contract, a result contract, and
neutral artifacts. Those are the durable assets and they survive a backend change.
The failure mode is mistaking the façade workflow for the service.

### What actually decides this: the macOS fleet

Firefox desktop tests need real GUI desktop OSes. Apple licensing requires macOS on
Apple hardware, so a genuine cloud service means owning or renting a Mac fleet
(MacStadium; EC2 Mac, with its 24-hour minimum dedicated-host allocation). That is
the entire reason commercial device clouds cost what they do.

GitHub Actions supplies that fleet for a 10× minutes multiplier and zero ops. **This,
not the elegance of the control plane, is the expensive decision in the whole design.**
Stay on Actions until something forces us off.

### Where GitHub Actions genuinely breaks as a service backend

| Wall | Consequence |
|---|---|
| `workflow_dispatch` returns 204 with **no body** — no run id | A request cannot be correlated to a run. The workaround is embedding a unique id in `run-name` and polling `/actions/runs`. It works; it is a clear signal of being off-piste. |
| **10-input ceiling** on `workflow_dispatch` | The §6.2 contract already uses 9. |
| No per-tenant quota, priority or fair scheduling | One tenant's large run starves the rest. `concurrency:` groups are the only lever. |
| No tenant isolation | Anyone who can read the repo reads every tenant's logs and artifacts. |
| Model B bills all minutes to the repo owner | No chargeback — and macOS is the expensive platform. |
| Artifacts capped at 90 days, zip-only, not queryable | Fine as a result drop, useless as a data plane. |

**Model A sidesteps four of those six**, which is the strongest argument for it. For
internal consumers it is the most cloud-native option available: serverless from our
side, zero ops, zero queue management, zero cost, and the caller's own quota governs
their usage. We ship a contract instead of operating a service.

### If we outgrow it, the answer is Taskcluster, not a bespoke cloud

Building a new cloud service at Mozilla when Taskcluster already exists would be an
odd call. It is a real CI-as-a-service with worker pools, scopes-based authZ, an API,
and artifact storage — and this repo already uses it, though **currently Linux-only**
(`t-linux-wayland` across all nine kinds in `taskcluster/kinds/`; Windows and macOS
run exclusively on GitHub Actions). Outgrowing Actions means extending Taskcluster
usage to Windows/macOS worker pools, not greenfielding a control plane.

### The layering to preserve

| Layer | Today | Later | Swappable? |
|---|---|---|---|
| **Control plane** — intake, auth, quota, scheduling | a workflow file | a small service, if ever | n/a |
| **Execution plane** — run tests on real desktop OSes | GitHub Actions | Taskcluster | **yes, if the contracts stay clean** |
| **Data plane** — results, history, trends | BigQuery (`scripts/upload_results_to_bq.py`) | unchanged | this is what survives a migration |

Keeping the execution plane swappable is precisely why `summary.json` carries a
`run.backend` field and why the request contract is published as a schema rather than
living only in workflow YAML.

### Decision criteria

Let evidence decide, not architecture taste:

- **A few teams, a handful of runs a day** → Model A on Actions is correct permanently; a cloud service would be waste.
- **Dozens of teams needing quota, chargeback and a synchronous API** → move the execution plane to Taskcluster. Because the contracts are versioned and backend-neutral, consumers should not need to change anything.

---

## Appendix A — Coupling audit

What is genuinely Mozilla-QA-specific in the test execution path, and how hard it is to bypass:

| Coupling | Location | Bypass difficulty |
|---|---|---|
| TestRail reporting | `conftest.py:355-383`, `modules/testrail_integration.py` | **Trivial** — already gated on `TESTRAIL_REPORT` |
| TestRail project `17` / config group `95` | `modules/testrail_integration.py` | N/A on the service path (never reached) |
| `test_case` fixture per test file | every `tests/**/test_*.py` | **None** — only consumed when reporting is on |
| BigQuery upload | `main.yml:305-315`, `scripts/upload_results_to_bq.py` | **Easy** — needs a secret-presence guard (0.2) |
| Slack notification | `main.yml:670-679`, `scripts/notifier.py` | **Easy** — same guard |
| Taskcluster secret fetch | `conftest.py:369-380` | **None** — gated on `TASKCLUSTER_ROOT_URL` |
| Checkout assumes same-repo | `main.yml:90`, `:337`, `:514`, `:637` | **Easy, but blocking** (0.1) |
| `switch_config.py` rewrites `pyproject.toml` | `scripts/switch_config.py` | None — works fine, just needs `--junitxml` added to the variants |

**The encouraging conclusion:** the test *execution* path is already almost free of Mozilla-QA-internal dependencies. The coupling lives in the *reporting* path, and that path is already behind a clean environment-variable gate that someone had the foresight to build.
