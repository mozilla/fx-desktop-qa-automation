# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**STARfox** — Smoke Test Automation Repository for Firefox Desktop. A Python/Selenium/PyTest suite for smoke testing Firefox desktop builds, including incident smoke testing. Runs on Taskcluster for CI.

## Common Commands

```bash
# First-time setup
./devsetup.sh           # Sets up git hooks; re-run if hooks change

# Run all tests
pytest

# Run a single test file
pytest tests/tabs/test_open_new_tab.py

# Run with specific options
pytest --run-headless              # Headless mode
pytest --fx-channel=Nightly        # Test against Nightly build (Custom, Firefox, Nightly)
pytest --fx-executable=/path/to/firefox   # Override with explicit path
pytest --lf                        # Re-run last failed tests

# Generate documentation
pdoc --docformat "numpy" modules

# Add a new test to the manifest (also runs on commit via git hook)
python addtests.py

# Create a new POM or BOM
python scripts/new_model.py [ModelName|model_name] [pom|bom]

# Linting (ruff)
ruff check .
ruff format .
```

## Architecture

### Directory Structure

```
tests/                     # Test files, organized by feature suite
  <suite_name>/
    conftest.py            # Suite-level fixtures (suite_id, prefs_list)
    test_*.py              # Individual test files (one test per file)
modules/                   # Page/Browser Object Models and utilities
  page_base.py             # BasePage — all POM/BOM classes inherit from this
  page_object.py           # Re-exports all page objects (wildcard imports)
  browser_object.py        # Re-exports all browser objects (wildcard imports)
  page_object_*.py         # Page Object Models (web content context)
  browser_object_*.py      # Browser Object Models (Firefox chrome context)
  data/                    # JSON element manifests (*.components.json)
  classes/                 # Data classes (AutofillAddressBase, CreditCardBase, etc.)
  util.py                  # BrowserActions, PomUtils, Utilities helper classes
manifests/
  key.yaml                 # Single source of truth for test skip/pass status
  testkey.py               # Manifest parsing and test balancing logic
config/                    # pyproject.toml variants for different CI configurations
conftest.py                # Root fixtures: driver, fx_executable, use_secrets, etc.
scripts/                   # Utility scripts (new_model.py, addtests.py, etc.)
profiles/                  # Firefox profile zips for tests requiring pre-existing profiles
data/                      # Test data files (secrets, autofill forms, etc.)
```

### The POM/BOM System

All page and browser object models inherit from `BasePage` (`modules/page_base.py`), which itself extends `pypom.Page`. Each POM/BOM class automatically loads its element definitions from a JSON manifest at `modules/data/<snake_case_class_name>.components.json`.

**JSON manifest format:**
```json
{
  "element-name": {
    "strategy": "css|id|class|xpath|tag|name|link_text|partial_link_text",
    "selectorData": "#selector",
    "groups": ["requiredForPage", "doNotCache"],
    "shadowParent": "parent-element-name"   // optional, for shadow DOM
  }
}
```

- `requiredForPage`: checked during `page.loaded` property
- `doNotCache`: prevents Selenium object caching for this element
- `shadowParent`: chains through shadow DOM to find the element
- Labels (dynamic selectors): `{placeholder}` in `selectorData` gets replaced via `labels=["value"]`

**Context switching:** Browser chrome uses `CONTEXT_CHROME`; web content uses `CONTEXT_CONTENT`. BOMs declare `"context": "chrome"` at the top of their JSON. Use `@BasePage.context_chrome` / `@BasePage.context_content` decorators for methods that require a specific context.

### Fluent Interface Pattern

POM/BOM methods return `self` (typed as `Page`) to allow chaining. The convention here is to reassign the object rather than chain with `.`:

```python
about_logins = AboutLogins(driver).open()
about_logins.click_add_login_button()
about_logins.create_new_login({"origin": ..., "username": ..., "password": ...})
```

### Fixture Flow

The `driver` fixture in `conftest.py` is `autouse=True` and depends on:
- `prefs_list` — Firefox prefs to set before launch; defined in each suite's `conftest.py`
- `suite_id` — `(testrail_id, suite_name)` tuple; required in each suite's `conftest.py`
- `test_case` — TestRail case ID; defined as a fixture in each test file
- `use_profile` — return a profile zip name from `./profiles/` to use a pre-built profile

### Test Structure

Each test file should contain one test function with a `test_case` fixture returning the TestRail case ID:

```python
@pytest.fixture()
def test_case():
    return "134453"

def test_something_descriptive(driver: Firefox):
    browser = SomeObject(driver)
    # test steps using the fluent interface
```

### Manifest / Skip System (`manifests/key.yaml`)

Controls which tests run and on which platforms. Values other than `pass` skip the test:

```yaml
suite_folder_name:
  test_file_without_py:
    result: pass          # or "unstable", "deprecated", "out-of-scope"
    splits:
    - smoke
    - ci
  test_with_subtests:
    subtest_function_name:
      result:
        mac: pass
        win: unstable
        linux: pass
      splits:
      - ci
```

After adding a test, run `python addtests.py` to register it (this also runs on commit via git hook).

### Importing POMs/BOMs

Import from the aggregate modules, not individual files:

```python
from modules.page_object import AboutLogins, AboutPrefs, Navigation
from modules.browser_object import TabBar, Navigation, ContextMenu
```

### Key Fixtures (root conftest.py)

| Fixture | Description |
|---|---|
| `driver` | Firefox WebDriver (autouse) |
| `use_profile` | Override to return profile zip name from `./profiles/` |
| `use_secrets` | Function factory for decrypting test account secrets |
| `opt_ci` | `--ci` flag (session-scoped) |
| `opt_headless` | `--run-headless` flag |
| `sys_platform` | `platform.system()` string (session-scoped) |
| `delete_files` | Cleanup fixture for downloaded files |
| `hard_quit` | Return `True` to skip graceful driver.quit() |

### Firefox Build Setup

The build under test must be installed before running tests:
- **macOS**: `/Applications/Custom Firefox.app/` (rename from `Firefox.app`)
- **Windows**: `C:\Program Files\Custom Firefox\`
- **Linux**: `~/Desktop/Custom Firefox/`

Or use `--fx-executable=<path>` to specify any location.

## PR Checklist

Per `.github/pull_request_template.md`:
- Re-request reviews after changes
- Resolve all conversations before merging
- Update Bugzilla bugs or TestRail test cases if needed
- Delete branch after merging
- If `BasePage` changes, note it explicitly
- If new dependencies added, note to rerun `pipenv install`
- If hooks changed, note to rerun `./devsetup.sh`
- Code must be linted and formatted before submitting
