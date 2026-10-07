# STARfox as a Service — Proposal

**Status:** Contract layer built; execution plane needs a decision
**Owner:** Arash Eghtesadi, Desktop Test Engineering
**Last updated:** 2026-10-05

| If you want… | Read |
|---|---|
| The pitch, the status, and what needs deciding | **this document** |
| To use the service (GitHub-based callers, today) | [SERVICE.md](SERVICE.md) |
| The engineering design and file-level plan | [TESTING_AS_A_SERVICE.md](TESTING_AS_A_SERVICE.md) |

---

## In one paragraph

STARfox is Mozilla QA's Firefox desktop test suite — 496 tests across 30 feature
areas, on Windows, macOS and Linux. Today it is a closed loop: QA schedules it against
Beta/DevEdition/RC and results go to TestRail. **We propose opening a narrow,
well-specified front door** so Firefox development teams and RelEng can point it at a
build of their own and get machine-readable results back — no QA involvement, no
TestRail account, no knowledge of how the tests work. The request and result contracts
are built and tested. The open question is *where the service runs*, and since our
consumers work in the tree on Taskcluster, the answer is Taskcluster rather than
GitHub Actions.

---

## The problem

A Firefox engineer asking *"does my patch break anything outside my feature?"* has no
self-serve way to find out. Neither does a release driver asking *"is this candidate
sane before we ship?"* Both have to ask QA and wait.

STARfox already runs exactly this coverage several times a day. The capability exists;
the access path does not.

The missing piece was never capability — `main.yml` could already install an arbitrary
Firefox build on all three platforms. What was missing was **contract**: a stable way
to ask, a stable way to get an answer, and a defined meaning for that answer.

---

## What the service does

> Give us a Firefox build. We run our suite against it. You get back JUnit XML and a
> versioned JSON summary with an unambiguous verdict.

A request names a build — a version like `155.0.1`, which we resolve to the right
archive.mozilla.org artifacts, or a direct installer URL for a try build. The caller
picks a test set (`smoke` is ~72 tests; `functional1-3` and `nightly` are larger),
picks which platforms to pay for, and picks how strict the pass/fail gate should be.

### The verdict is the product

Every run yields a small, stable artifact per platform: a merged JUnit XML file and a
`summary.json`. The headline is a four-way verdict, and keeping those four distinct is
the whole point of the exercise:

| Verdict | Means | Why it's separate |
|---|---|---|
| `pass` | all green | — |
| `flaky` | everything passed, some only on retry | A flake is not a regression. Conflating them is how teams learn to ignore test results. |
| `fail` | a test failed outright | The signal actually worth acting on. |
| `infra_error` | **the run itself broke** | A 404 on your installer URL says nothing about your code. Saying so explicitly is what keeps the service trustworthy. |

The summary also records which gate policy the caller chose and whether it was
violated, so a release gate reads one boolean instead of reimplementing the rules.

### Deliberately out of scope

- **Hosting other teams' tests.** The infrastructure is easy; the governance —
  ownership, review capacity, flake budgets, eviction — is not.
- **Shipping the framework as a library.** Highest long-term leverage, highest cost.
- **Replacing TestRail.** It stays the system of record for QA's scheduled runs.
  Service requests never write to it.

---

## Where it should run

This is the decision the proposal turns on.

### We initially built on GitHub Actions. That was wrong for our consumers.

STARfox's own CI is GitHub Actions for Windows and macOS, so the first implementation
exposed the service there: a consumer would call our reusable workflow from their own
GitHub workflow. **That assumed consumers are on GitHub Actions. They are not** — the
tree is in Taskcluster, and a Taskcluster-based consumer cannot call a GitHub reusable
workflow at all.

A related correction: an earlier draft argued that GitHub hands us a macOS fleet we'd
otherwise have to rent, and that this made leaving Actions expensive. That was
overstated. STARfox already runs on `firefox-ci-tc.services.mozilla.com` — the same
Taskcluster deployment where Firefox's own macOS tests run. **Mozilla already owns
that fleet.** The cost of moving execution to Taskcluster is worker-pool capacity and
taskgraph work, not hardware.

### Taskcluster is not an alternative to a cloud service. It *is* one.

It also answers, natively, the limitations that made GitHub Actions a poor service
backend:

| What a service needs | GitHub Actions | Taskcluster |
|---|---|---|
| A request returns a job id | ❌ HTTP 204, no body — poll and guess | ✅ triggering a hook returns the `taskId` |
| Request validation | hand-rolled | ✅ a hook's `triggerSchema` **is** JSON Schema |
| Per-consumer authorization | ❌ repository-level only | ✅ scopes — already used here for secrets |
| Quota and priority | ❌ none | ✅ worker pools and `task-priority` |
| Durable, queryable results | ❌ 90-day zip files | ✅ artifacts + index; `public/results` already served from `firefoxci.taskcluster-artifacts.net` |
| Reachable by our consumers | ❌ | ✅ |

Because the request contract was written as a JSON schema rather than as workflow
inputs, [`schemas/test-request-v1.json`](schemas/test-request-v1.json) can become a
hook's `triggerSchema` largely as-is.

### Proposed shape

A **triggerable service in STARfox's own taskgraph** — no mozilla-central changes, and
a clean ownership boundary:

1. **Request.** A consumer (a try-push task, a RelEng pipeline, or a person) triggers
   a Taskcluster hook with a payload matching the request contract. The trigger
   returns a `taskId` immediately, so there is no polling guesswork.
2. **Execution.** The hook spawns a decision task — the same mechanism `.cron.yml`
   already uses — which generates one test task per requested platform.
3. **Results.** Each task publishes `public/results/summary.json` and `junit.xml` as
   Taskcluster artifacts at a predictable URL, with index routes so a consumer can
   look a run up by request id rather than task id.
4. **Authorization.** Per-consumer scopes on the hook. Per-team quota via worker pools.

---

## How far do we take it?

"Cloud service" can mean three quite different commitments. They are incremental, so
this is a question of where to stop, not which to pick.

### Tier 1 — Taskcluster-native service *(recommended)*

The shape above. Consumers trigger a hook and read artifacts. Authorization by scopes,
quota by worker pools, results by artifact + index.

- **Build:** worker pools for Windows/macOS, a hook, one taskgraph transform, a
  parameterised decision task.
- **Operate:** nothing new. Taskcluster is already operated for us.
- **Gets you:** everything originally asked for. A consumer can request a run and read
  a result without talking to QA.

### Tier 2 — Tier 1 plus a client

A thin wrapper so nobody has to hand-craft a hook payload: a CLI (`starfox request
--version 155.0.1 --platforms win,mac`) that triggers, waits, and prints the verdict.

- **Build:** small. **Operate:** nothing if it ships as a CLI rather than a server.
- **Gets you:** adoption. The gap between "possible" and "pleasant" is most of why
  internal tools go unused.
- **Worth noting:** this is pure UX. It adds no capability over Tier 1.

### Tier 3 — A managed service with its own control plane

An HTTP API with a request database, enforced quotas, a dashboard, and an SLA.

- **Build:** months. **Operate:** on-call, a service to keep up, a real headcount ask.
- **Gets you:** things Tier 1 already mostly provides — which is why this is hard to
  justify. Taskcluster *is* the control plane; a second one in front of it needs a
  specific reason to exist.

**Recommendation: commit to Tier 1, add Tier 2's CLI as sugar, and treat Tier 3 as
unjustified until a concrete need appears that Tier 1 demonstrably cannot meet.**

---

## Status

### Built, tested, committed (on `arash/fx-dte-as-a-service`; not pushed)

Roughly 80% of the work is execution-backend-neutral, which was deliberate, and
transfers to Taskcluster unchanged:

| Component | Status |
|---|---|
| Result bundle builder — flake classification, infra-error detection, gate policy | ✅ pure Python; runs identically on a Taskcluster worker |
| Request validation and candidate-build resolution | ✅ pure Python, 30 tests |
| Both JSON schemas; the four-verdict semantics; `run.backend` field | ✅ backend-neutral by design |
| JUnit XML output from the CI configs | ✅ |
| 62 unit tests; lint and format clean | ✅ |

### Needs building

| Work | Depends on |
|---|---|
| Windows and macOS Taskcluster worker pools | **RelEng / Taskcluster — see Dependencies** |
| A hook with the request contract as its `triggerSchema` | — |
| Parameterised decision task + transform for bring-your-own-build | Nothing today accepts a build URL; `.cron.yml` jobs are all fixed `target-tasks-method` |
| Artifact + index routes for result lookup | — |
| Taskcluster-side consumer docs | the above |

### Reusable but no longer the primary path

The GitHub Actions façade (`fx-test-request.yml`) and the cross-repo reusable-workflow
path still work, and remain useful for QA's own ad-hoc runs and for any Mozilla
consumer that *is* on GitHub Actions. They are no longer the headline.

### Not proven

Nothing has been exercised cross-system in real CI. That risk is not theoretical:
while building the façade we found that the installer-URL inputs had been declared on
only one of two workflow triggers, making the bring-your-own-build path unreachable
from outside — exactly the class of defect only a live run surfaces. One real
end-to-end consumer run should precede any announcement.

---

## Dependencies and asks

**1. Windows and macOS worker pools on Firefox CI Taskcluster.** `taskcluster/config.yml`
currently defines only `b-linux`, `images` and `t-linux-wayland`. The pools exist on
the instance; we need capacity and scopes. **This is the critical-path blocker** — it
gates every platform except Linux, and it is a conversation with RelEng/Taskcluster,
not something we can unblock ourselves. Until it lands, a Taskcluster-native service
is Linux-only and Windows/macOS must stay on GitHub Actions.

**2. Who triages a failure in a tenant run?** This, not compute, is the dominant cost,
and it is a staffing question. *Recommendation: the consuming team owns it for v1* —
the flake and infra-error classification exists precisely so most questions answer
themselves. **Settle this before announcing**, because an unstated support policy gets
assumed to be generous.

**3. A pilot consumer.** We want one real team through the whole path before
publicising it. RelEng gating a release candidate is the highest-value pilot.

**4. Scope-granting policy.** Who may trigger the hook, and how is that reviewed?

---

## Cost

| Item | Who bears it |
|---|---|
| Taskcluster execution | Existing Firefox CI worker pools — capacity allocation, not new spend |
| GitHub Actions runs (interim, Windows/macOS) | QA's Actions budget. macOS is ~10× Linux per minute, which is why callers can request a platform subset |
| Maintenance | Low. The service reuses the existing suite and CI; the new surface is a hook, a transform, two small scripts and two schemas |
| **Triage** | **Unresolved — see ask 2. The dominant cost, and a staffing question** |

---

## Risks

| Risk | Mitigation |
|---|---|
| **Worker-pool access doesn't materialise** | Hybrid fallback: Taskcluster for Linux, GitHub Actions for Windows/macOS, one contract spanning both. The `run.backend` field already anticipates this |
| **Flakes erode trust.** A gate that false-fails once gets disabled permanently | Flakes are classified and by default do not fail a caller's gate |
| **Triage load swamps QA** | Mechanical classification answers most questions; publish the policy before announcing |
| **Tenant runs pollute QA's data** | Service requests carry no reporting credentials, so they cannot write to TestRail, BigQuery or Slack even by accident |
| **Consumers couple to internals we want to change** | Only the contract is promised; the suite's internals stay free to refactor |

---

## Next steps

1. **Agree the tier** (recommendation: Tier 1 + the Tier 2 CLI).
2. **Open the worker-pool conversation with RelEng/Taskcluster** — critical path, and
   the longest lead time. Start it first.
3. Settle triage ownership (ask 2).
4. Review and merge the contract work already built.
5. Build the Taskcluster hook and parameterised decision task, Linux first — this
   delivers a working end-to-end service without waiting on worker pools.
6. Pilot with one real consumer on Linux; extend to Windows/macOS as pools land.
7. Announce only after the pilot.

Deliberately *not* on this list: building quota, dashboards or an SLA before there is
usage to measure.
