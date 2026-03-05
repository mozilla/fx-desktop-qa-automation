# Project Summary

**Firefox Desktop QA Automation** is a test automation framework for the Mozilla Firefox desktop browser.

## Core Stack

| Tool | Purpose |
|---|---|
| Python | Primary language |
| pytest | Test framework |
| Selenium WebDriver | Browser automation (Firefox/geckodriver) |
| GitHub Actions | Primary CI |
| Taskcluster | Mozilla CI for beta/DevEdition runs |

## Architecture

### Design Pattern — Page/Browser Object Models (POM/BOM)

All Firefox UI elements are modeled as Python classes inheriting from `BasePage`. The project uses a **Fluent Interface** strategy where methods return `self` to allow readable, chain-style test code.

- Page Object files: `modules/page_object_*.py`
- Browser Object files: `modules/browser_object_*.py`
- Shared utilities: `modules/util.py` (e.g., `BrowserActions`, `PomUtils`)

### Test Organization

Tests live under `tests/`, grouped by Firefox feature area:

```
tests/
  address_bar_and_search/
  audio_video/
  bookmarks_and_history/
  downloads/
  drag_and_drop/
  find_toolbar/
  ... (and more)
```

Each suite has its own `conftest.py` for suite-level fixtures and Firefox preferences.

### Test Types

| Type | Location | Description |
|---|---|---|
| Smoke tests | `tests/` | Quick sanity checks on beta/DevEdition builds |
| Functional tests | `tests/` | Deeper per-feature coverage |
| L10n / Credit Manager tests | `l10n_CM/` | Localization and autofill tests across many locales and e-commerce sites |
| Stability tests | `tests/` | Reliability and flakiness monitoring |

### L10n / Credit Manager Tests

The `l10n_CM/` directory contains tests for address and credit card autofill across 50+ e-commerce sites in multiple locales (US, DE, FR, CA, GB, BE, etc.). Per-site configuration lives in `l10n_CM/constants/<site>/<locale>/`.

## CI/CD

### GitHub Actions (`.github/workflows/`)

| Workflow | Purpose |
|---|---|
| `main.yml` | Core smoke test execution (callable, dispatchable) |
| `smoke-test-beta.yml` | Smoke tests against Firefox Beta |
| `smoke-test-devedition.yml` | Smoke tests against Firefox DevEdition |
| `functional-test-beta.yml` | Functional test runs against Beta |
| `main-l10n.yml` / `test-l10n-beta.yml` | L10n test runs |
| `main-stability.yml` / `stability-test-dispatch.yml` | Stability monitoring runs |
| `ci-dispatch.yml` | Manual dispatch entrypoint |

### Taskcluster (`taskcluster/`)

Handles additional CI tasks such as linting (`kinds/lint/`) and scheduled Beta/DevEdition QA runs (`kinds/new-beta-qa/`, `kinds/new-devedition-qa/`).

## Integrations

- **TestRail:** Each test includes a `test_case` fixture returning a TestRail case ID. Scripts in `modules/testrail_scripts/` manage test status in bulk.
- **Slack:** `taskcluster/scripts/slack_notifier.py` sends CI result notifications.

## Key Files & Directories

```
modules/          # POMs, BOMs, utilities, and support classes
tests/            # Functional and smoke test suites
l10n_CM/          # Localization and Credit Manager test suites
taskcluster/      # Taskcluster CI configuration and scripts
data/             # Test assets (PDFs, images, HTML pages, bookmarks)
conftest.py       # Root-level pytest fixtures (driver setup, etc.)
BEST_PRACTICE.md  # Developer guidelines for writing tests
OBJECT_MODELS.md  # Guide to POM/BOM conventions used in this repo
```
