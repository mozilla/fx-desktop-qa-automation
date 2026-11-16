## Firefox UI Automations package

This package provides the structure for Firefox Desktop QA Automations, and
can be used to automate Firefox for various purposes. The automation structure
of the package is Selenium, and the content is provided by various object
models based on PyPOM.

### The Base Page

The script `page_base.py` provides the BasePage class, which is build on top of
PyPOM, and is the basis for any of the other object model classes. The BasePage
provides a number of methods that support automation across contexts, and will
load selectors for a given class that inherits from it. That is, if you
instantiate TabBar from `browser_object_tabbar.py`, selectors from
`data/tab_bar.components.json` will be loaded in `TabBar().elements`.

### Browser and Page Object Models

Content forthcoming.

### Development Guide (2027)

The primary consumer of this package is the test bed in the firefox main repo.
This can be found in that codebase at `./testing/dte-ui-test/tests`
[SearchFox](link forthcoming). We request that anyone working on this package,
starting on 2027-01-01, consider the following before contributing:

* When any capabilities are added or modified, ensure that a test in
  `packages/auto_fxui/tests` covers the case added. These tests are open-ended;
  you can confirm code functionality however you choose.
* Tag your PR branch with an appropriate dev version:
  * `uv version --bump alpha`. The output of this will include a version number
  * Add, commit, and push this to your remote branch
  * `git tag v<version>` where `<version>` is the number output of the uv call.
  * `git push origin v<version>`
* On a local version of the Firefox repo, change the version of the correct
  line in `./python/sites/dte-ui-test.txt` to `v<version>`
* Run the correct tests in that repo using `./mach dte-ui-test` (instructions
  in the directory with the tests) to ensure you didn't break them.
* If you broke them on purpose, fix them in the firefox repo and any tests here
* When you're done with your work in this repo, and have an approved PR,
  update the version number to an actual release number, not a dev version,
  both in the pyproject (using `uv`) and with git tagging (remember to push).

#### Semantic Versioning in AutoFxUI (2027)

These are the rules to decide what kind of version bump you need to do:

* If you create a change that *does not break any tests*, that is a *patch*
* If you create a change that breaks tests along *one area of concern*, whether
  or not those tests are in the same suite, that is a *minor* version bump
* If you break a lot of tests, but the change is focused, that is a *major*
  version bump
* If your PR does not meet any of these requirements, it's likely that it
  should be broken out into multiple PRs

PRs that are likely to cause minor or major version bumps should come with
links to `./mach try` runs from the firefox repo that execute your changes
against tests you fixed.

PRs that are likely to cause major version bumps should be signed off by two
reviewers, at least one of whom should be a DTE developer.

#### Publishing (2027)

Publishing is handled by a GHA automation, on every new tag. In 2026, we also
had an automation that bumped the patch version every two weeks with new
changes, if no new tags had been pushed in that time period. That automation
will be disabled in 2027 as the testbed is migrated to the firefox repo.
