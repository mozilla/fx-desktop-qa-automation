# Intro

This document explains what Page and Browser Object Models are, how to create
them for Python Selenium, and what principles, strategy, and structure we use
in this repo to implement and use them.

## What is a Page Object Model?

A Page Object Model is a code model of a given page under test—the structures,
elements, and constants (like label text) are attributes or class functions of
the object in question. This makes writing tests much easier, as the test dev
no longer has do the work of selecting the relevant DOM elements. POMs also
make tests more readable, as elements now have uniform and descriptive names.

## Why do we also have a Browser Object Model?

Because the chrome context of Firefox (the parts of the browser that perform
functions like navigation and configuration) is itself a markup document, we
can do the same thing we do for web pages/apps for the browser itself.

# File Structure

Page and Browser Object files live in `./modules`, where they are all
imported (and thus re-exported) by either `page_object.py` or
`browser_object.py`. The filename for an individual Page Object should be
`page_object_xxxx.py` where `xxxx` is replaced by a very short name for the
page being described. All constants, attributes, and functions for the page
should be contained in the file unless that would make the file unsuitably
large.

Browser Object files should follow a similar convention. As areas of the
chrome context aren't explicitly defined, please use caution when creating
a new Browser Object file so as to avoid overlap in concerns.

All Page and Browser Object files should include the line:
`from modules.page_base import BasePage` and all POM/BOM classes should
inherit from `BasePage`.

# The Fluent Interface Strategy

This repo attempts to implement a Fluent Interface strategy when designing
POMs and BOMs.

## The Basics

The fundamental principle behind Fluent Interface is this: by creating an
API (or in our case, a POM) in a certain way, we can write test as a
subject (the system under test) followed by a list of actions we take in
the test. In this way, the test code resembles the human-language test
plan. To do this we ensure that relevant POM class methods return `self`,
so that methods can be chained together.

## How that works here

Here is a very basic example of a class method from the `AboutLogins`
class:

```Python
def click_add_login_button(self) -> Page:
    self.add_login_button().click()
    return self
```

We can then use that method in a chain, as we see in this example from
`./tests/credential/conftest.py`:

```Python
def add_login(origin: str, username: str, password: str):
    about_logins = AboutLogins(driver).open()
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": origin,
            "username": username,
            "password": password,
        }
    )
```

## Convention

The primary Python formatting convention document, PEP-8, requests that
Python users not use the backspace to split lines, even though the
interpreter will read this correctly. PEP-8 recommends that lines be
split inside (), [], or {} pairs. To abide by these formatting
guidelines but keep code readable, there are two reasonable options:

1. Enclose all method chains in a parenthesis pair
2. Convert the method chains into multiple statements

We have chosen the second option. We create our tests by _reiterating
the object_, as can be seen in the `add_login()` function above.
