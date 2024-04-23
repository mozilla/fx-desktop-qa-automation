# About

This document is a loosely-organized collection of guidelines, tips, and conventions
directed at test developers writing for this project.

## This Repository

This repo has been set up as a PyTest repo, running on Taskcluster for CI, using
Selenium to perform actions in the browser. Here are a few pointers:

### Individual Tests

Each test file is going to be named test_xxxxx.py, where the _xxxxx_ is a 
description of the test, in snake_case. These filenames should be unique and self-
explanatory, but do not have to be long.

Test files should ideally contain one test each (there may be cause to double up on
occasion). Test files are functions named test_yyyyy, where _yyyyy_ is a full
description of the test, in snake_case. Don't be afraid of long test function
names. A test file will also contain imports and may contain additional fixtures
or other functions.

Each individual test is going to need access to a Selenium WebDriver object. Usually
this will be done by _requesting_ the `driver` fixture like this:

```Python
import pytest
from selenium.webdriver import Firefox

def test_new_tab_opens_expected_page(driver: Firefox):
    # test goes here
```

There exist other fixtures that alter the session with setup before tests can
proceed. You will also likely want to import other Selenium modules, or our support
modules to assist with testing.

### Test Suites

Test cases in the same suite, in general, should be in the same folder:
`./tests/suite`, where _suite_ is a word or a few words that briefly identify the
feature under test. You may want to add `./tests/suite/conftest.py` with a PyTest
fixture called `set_prefs`, which the `driver` fixture requires, and which
sets Firefox preferences on the WebDriver instance. The `set_prefs` fixture can
also be set inside an individual test file.

### Support methods and classes

Certain utilities are bundled in `./modules/util.py`. These are organized by
general use case as classes, e.g. BrowserActions for helper functions that make
Selenium easier to use or PomUtils that help organize object models. Import the
class, but instantiate it inside the object model or test you're writing:
```Python
from modules.util import BrowserActions

def test_something(driver):
    ba = BrowserActions(driver)
    ba.search("soccer ball")
```

### Page and Browser Object Models

See [the Object Models doc](./OBJECT_MODELS.md) for best practices.

======

## PyTest

This project uses PyTest 8.0. The [PyTest documentation](https://docs.pytest.org/en/8.0.x/)
is a great place to learn the basic principles of the framework, but for the
purposes of brevity, we'll go over the most important things here:

#### Fixtures

PyTest relies heavily on functions called "Fixtures" to provide things like test
data, setup, teardown, and session information. Functions are identifies as
fixtures by the `@pytest.fixture` decorator. Fixtures are _requested_ by tests in
their function signatures. Fixtures can request other fixtures.
[PyTest Fixture Tutorial](https://docs.pytest.org/en/8.0.x/explanation/fixtures.html#about-fixtures)

#### conftest.py

PyTest has a special place for configuration settings and fixtures that don't
belong to just one test, called `conftest.py`. Multiple of these files exist in
the repo, and this is by design. Fixtures declared in `conftest.py` are available
to request in tests in `test_*.py` files.

#### Test Organization and Execution

The PyTest runner will collect and execute tests using the following logic:

1. Assume that all and only functions that start with `test` are tests.
2. Assume that all and only files named `test_*.py` or `*_test.py` contain tests.
3. For any given test, assume that every `conftest.py` file in the directory tree
between the current directory and the test's directory is relevant.
4. For any given test, assume that any parameter in the function signature that
matches the name of a fixture is that fixture, with priority given to fixtures
declared in the test's directory.

#### Note

This means that you can have a fixture declared in `./conftest.py` that requests
a fixture declared in `./tests/foo/conftest.py`, and that's very useful.

## Selenium Python

#### Basics

The basics of Selenium Python are out of scope of a repo doc like this, but we do
plan on finding and if necessary creating some documentation around the framework.

#### Finding Tricky Selectors

Please see 
[our guide to tricky selectors](https://mozilla-hub.atlassian.net/wiki/spaces/QA/pages/606503037/HOWTO+Find+difficult+selectors).
