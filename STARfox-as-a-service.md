# STARfox as a Service — Proposal

**Status:** Phases 0–2 built, awaiting review
**Owner:** Arash Eghtesadi, Desktop Test Engineering
**Last updated:** 2026-10-05

| If you want… | Read |
|---|---|
| The pitch, the status, and what we need decided | **this document** |
| To actually use the service | [SERVICE.md](SERVICE.md) |
| The engineering design and file-level plan | [TESTING_AS_A_SERVICE.md](TESTING_AS_A_SERVICE.md) |

---

## In one paragraph

STARfox is Mozilla QA's Firefox desktop test suite — 496 tests across 30 feature
areas, running on Windows, macOS and Linux. Today it is a closed loop: QA schedules
it against Beta/DevEdition/RC, and results go to TestRail. **We are opening a narrow,
well-specified front door** so that Firefox development teams and RelEng can point it
at a build of their own and get machine-readable results back, with no QA
involvement, no TestRail account, and no knowledge of how the tests work. The
implementation is done and awaiting review; what remains is mostly a decision about
who owns triage.

---

## The problem

A Firefox engineer who wants to know *"does my patch break anything outside my
feature?"* has no self-serve way to find out. Neither does a release driver asking
*"is this candidate sane before we ship it?"* Both have to ask QA and wait.

Meanwhile STARfox already runs this exact coverage several times a day. The capability
exists; the access path does not.

The gap turned out to be smaller than expected. `main.yml` could already download and
install an arbitrary Firefox build on all three platforms — that machinery was built
for manual QA runs. What was missing was not capability but **contract**: a stable way
to ask, a stable way to get an answer, and a defined meaning for that answer.

---

## What we are building

### What it does

> Give us a Firefox build. We run our suite against it. You get back JUnit XML and a
> versioned JSON summary with a clear verdict.

A request names a build — either a version like `155.0.1`, which we resolve to the
right archive.mozilla.org artifacts, or direct installer URLs for a try build. The
caller picks a test set (`smoke` is ~72 tests; `functional1-3` and `nightly` are
larger), picks which platforms to pay for, and picks how strict the pass/fail gate
should be.

### Two ways to consume it

**A. Call it from your own CI.** About ten lines of YAML in your repository. It runs
on *your* runners using *your* minutes, and results land in *your* workflow run. No
credentials cross the boundary in either direction. This is the recommended path and
costs QA nothing — we ship a contract rather than operating a service.

**B. Ask our repo to run it.** Click through the Actions UI, or POST to the GitHub
API. We run it on our runners. Best for one-off checks and for teams without CI of
their own.

### What you get back

Every run produces a small, stable artifact per platform containing a merged JUnit XML
file and a `summary.json`. The headline field is a four-way verdict, and the
distinction between those four is the point of the whole exercise:

| Verdict | Means | Why it's separate |
|---|---|---|
| `pass` | all green | — |
| `flaky` | everything passed, some only on retry | A flake is not a regression. Conflating them is how teams learn to ignore test results. |
| `fail` | a test failed outright | This is the signal worth acting on. |
| `infra_error` | **the run itself broke** | A 404 on your installer URL tells you nothing about your code. Saying so explicitly is what keeps the service trustworthy. |

The summary also reports which policy the caller chose and whether that policy was
violated, so a release gate can read one boolean rather than reimplementing the rules.

### What it deliberately is *not*

Scope was kept narrow on purpose. Three things are explicitly out:

- **Hosting other teams' tests.** The infrastructure for that is easy; the governance
  — ownership, review capacity, flake budgets, eviction policy — is not. Revisit when
  BYOB has real users.
- **Shipping the framework as a library** for teams to build their own suites on.
  Highest long-term leverage, highest cost. Revisit on demand.
- **Replacing TestRail.** It stays the system of record for QA's own scheduled runs.
  Service requests simply never write to it.

---

## Where we are

Phases 0 through 2 are implemented, locally verified, and committed on
`arash/fx-dte-as-a-service`. Nothing is pushed or merged.

| Phase | What it did | Status |
|---|---|---|
| **0 — Unblock** | Made the existing path callable from outside: cross-repo checkout, JUnit XML output, and guards so callers without QA secrets don't hard-fail after their tests already passed | ✅ |
| **1 — The contract** | The result bundle: flake classification, infrastructure-error detection, gate policy, two published JSON schemas | ✅ |
| **2 — The front door** | The request façade with up-front validation, candidate-build resolution, and consumer documentation | ✅ except the `v1` tag |
| **3 — Operability** | Quota, dashboards, ownership taxonomy, published SLA | ⬜ deliberately deferred |

62 unit tests cover the new logic. Linting and formatting are clean.

**Phase 3 is a backlog, not a blocker.** Quota and dashboards only earn their keep once
there are enough tenants to contend for runners. Building them now would be guessing.

### What has *not* been proven

Everything above was verified locally. **No cross-repo run has been exercised in real
CI**, and that is the one path that matters most. The risk is not hypothetical: while
building Phase 2 we found that the installer-URL inputs had been declared on only one
of `main.yml`'s two triggers, which meant the bring-your-own-build path was unreachable
from another repository — exactly the kind of defect only a real run surfaces. It is
fixed, but it is a reminder that a first live consumer run should precede any
announcement.

---

## Decisions we need

**1. Who triages a failure in a tenant run?** *(the important one)*

This, not compute, is the real cost of the service. Three options: the consuming team
owns it and we supply only artifacts; QA triages best-effort; QA triages to an SLA.

*Recommendation: the consuming team owns it for v1.* The flake and infrastructure-error
classification is specifically designed so most questions answer themselves. Revisit
once we can see real volume. **This should be settled before we announce anything**,
because an unstated support policy will be assumed to be generous.

**2. Who is the first consumer?** We want one real team through the whole path before
publicising it. RelEng gating a release candidate is the highest-value pilot.

**3. Do we commit to a support level?** Best-effort, or something firmer? Related to
(1), but a separate promise.

**4. Confirm the repository is public.** Model A depends on it. Everything observable
says yes; it needs one authoritative confirmation.

---

## Cost

| Item | Who pays |
|---|---|
| Model A runs | The consuming team — their runners, their minutes |
| Model B runs | QA's GitHub Actions budget. macOS is ~10× the per-minute cost of Linux, which is why callers can request a subset of platforms |
| Maintenance | Low: the service reuses the existing test suite and CI. The new surface is one workflow file, two small scripts, and two schemas |
| **Triage** | **Unresolved — see decision 1. This is the dominant cost and it is a staffing question, not an infrastructure one** |

---

## Risks

| Risk | Mitigation |
|---|---|
| **Flakes erode trust.** A release gate that false-fails once gets disabled permanently | Flakes are classified and, by default, do not fail a caller's gate |
| **Triage load swamps QA** | Mechanical classification answers most questions; publish the policy before announcing |
| **Tenant runs pollute QA's data** | Service requests pass no reporting credentials, so they cannot write to TestRail, BigQuery or Slack even by accident |
| **Consumers depend on internals we want to change** | A thin façade is the only promised contract; `main.yml`'s internals stay free to refactor |

---

## Why this approach

**Why GitHub Actions rather than building a real cloud service?** Because the hard part
of Firefox desktop testing is not the control plane — it is the **macOS fleet**. Apple
licensing requires macOS on Apple hardware, which is why commercial device clouds cost
what they do. GitHub gives us that fleet for a minutes multiplier and zero operations
work. Walking away from it is the expensive decision, and it has nothing to do with how
elegant the API is.

**What if we outgrow it?** Then the answer is Taskcluster, not a bespoke cloud service.
It is already a real CI-as-a-service with worker pools and proper authorization, and
this repo already uses it — currently for Linux only. That would be an extension, not a
greenfield build.

**What makes that migration possible later?** The request and result formats are
published as backend-neutral JSON schemas rather than living only inside workflow
files. The execution engine can change without consumers noticing. That was a
deliberate design choice, and it is the main reason to care about the schemas at all.

The honest framing: a workflow file is not an API. What we have built is a contract
that happens to be served by GitHub Actions today. Keeping that distinction clear is
what buys us the option to change our minds.

---

## Next steps

1. Review and merge the three phases.
2. Settle decision 1 (triage ownership).
3. Run one real cross-repo request end to end.
4. Cut the `v1` tag against that verified commit, so consumers have a stable pin.
5. Onboard a pilot consumer; let their experience decide which Phase 3 items matter.
6. Announce more widely only after the pilot.

Deliberately *not* on this list: building quota, dashboards, or an SLA before there is
usage to measure.
