# Suite conftest converter (DTE-5557)

Writes Firefox-tree versions of STARfox's suite conftests (`tests/<suite>/conftest.py`), so suites can move into `testing/dte-ui-test` without STARfox's root conftest.

For each suite conftest it:
- Drops fixtures that are code-identical to the Firefox root fixture they would shadow (for example `prefs_list` and `add_to_prefs_list`).
- Applies the agreed rules in `migration_rules.py`: drops `hard_quit`, moves `faker_seed` into `password_manager`.
- Rewrites imports from the `modules.*` re-export shims to `auto_fxui.*`, and removes only imports the conversion left unused.
- Reports what still blocks the conftest, and what the suite's tests still need from Firefox.

How it decides: it parses STARfox, the Firefox conftest, installed pytest plugins and pytest itself with `ast`, then resolves every test's fixtures twice, once in STARfox as it is and once in Firefox after migration. Nothing is imported or run, and the STARfox repo is only read.

## Prerequisites

- A STARfox checkout with its virtualenv set up (`uv sync`). The converter itself uses only the Python standard library (3.11+).
- A Firefox checkout. The converter reads `testing/dte-ui-test/tests/conftest.py` and the mach site files in `python/sites/`.
- No Firefox build or browser is needed.

## Run it

From the STARfox repo root:

```bash
uv run python -m scripts.fixture_inventory \
    --repo . \
    --out /tmp/dte-5557-conftests \
    --exclude-suite meta \
    --firefox-root ~/firefox \
    --firefox-conftest ~/firefox/testing/dte-ui-test/tests/conftest.py \
    --firefox-site ~/firefox/python/sites/dte-ui-test.txt \
    --firefox-site ~/firefox/python/sites/mach.txt
```

`--exclude-suite meta` leaves out `tests/meta`, which checks STARfox's own setup rather than Firefox.

| Option | Meaning |
|---|---|
| `--repo` | STARfox checkout to read (required) |
| `--out` | Folder to write to (required). Must be outside `--repo` and empty |
| `--overwrite` | Allow writing into a non-empty `--out` |
| `--firefox-conftest` | Firefox conftest that replaces STARfox's root conftest (required, repeatable) |
| `--firefox-site` | Firefox `python/sites/*.txt` file, to know which packages and plugins Firefox installs (repeatable) |
| `--firefox-root` | Firefox tree, so report paths are shown relative to it |
| `--exclude-suite` | Suite folder to leave out (repeatable) |
| `--tests-dir` | Tests folder, relative to `--repo` (default `tests`) |
| `--site-packages` | Where to read installed packages and plugins from (default: the running Python's, which is the STARfox venv under `uv run`) |

Example output:

```
30 suite conftests converted: 27 ready, 3 blocked (static analysis; not run)
/private/tmp/dte-5557-conftests
```

## Output

```
<out>/
  <suite>/conftest.py        one converted conftest per suite, nested paths kept
  conversion-report.md
  conversion-report.json
```

Copy `<out>/<suite>/conftest.py` to `testing/dte-ui-test/tests/<suite>/conftest.py` together with that suite's tests.

## Reading the reports

`conversion-report.md` has three parts:
- **Notes** about the analysis itself. For example, Firefox site requirements that aren't installed in the scanned venv, whose own dependencies are then unknown.
- **Root fixtures suite conftests need that Firefox lacks.** Anything listed here has to be added to the Firefox root conftest first. Against a Firefox conftest with [D345617](https://phabricator.services.mozilla.com/D345617), this shows "None."
- **Per conftest**, one row per suite:
  - **Conftest:** `ready` or `blocked`. This is for the conftest only.
  - **Removed / Moved in:** fixtures the conversion dropped or copied in.
  - **Conftest blockers:** why it is blocked.
  - **Tests still need:** root fixtures the suite's tests ask for that Firefox lacks, with test counts.
  - **Tests' STARfox-only imports:** repo-local modules imported anywhere in the suite.

`conversion-report.json` has the same data:
- `note` and `analysis_notes`
- `root_fixtures_firefox_lacks`: `name`, `requested_by`, `starfox_provides`
- `conftests`: per suite `status`, `blockers`, `removed` (with the reason), `moved_in`, `import_changes`, `kept`, `notes`, `tests_still_need`, `tests_repo_local_imports`

A note ending in "(cleanup candidate)" marks a kept fixture that no test uses. It is informational only and the fixture stays.

## Limitations

- **"Ready" is static.** It means the converted conftest parses and, by source analysis, everything it requests resolves in Firefox. It has not been run under Firefox's harness.
- **Current blockers:**
  - `pdf_viewer` and `reader_view` read files from the STARfox repo (`data/`).
  - `smart_window` imports STARfox-only `modules.fxa_token` and `modules.taskcluster`, and reads files from the STARfox repo.
- **The analysis doesn't see everything:**
  - Fixtures added at runtime (`pytest_plugins` strings, `pytest_generate_tests`, `getfixturevalue` with a variable name) aren't resolved.
  - Plugin fixtures are only found in a plugin's entry-point module.
  - Repo file reads are found by pattern (string literals, `Path(...)`, `os.path.join(...)`). Paths built from variables, and file reads inside hooks, aren't flagged.

## Tests

```bash
uv run pytest scripts/fixture_inventory
```

The tests build small fake repos in a temporary folder and never start Firefox.
