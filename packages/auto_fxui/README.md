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

### Restarting Firefox

`restart_firefox(driver)` in `restart.py` quits Firefox cleanly and starts it
again on the same profile, so prefs and the session carry over. The same
`driver` object is reattached to the new Firefox, and its usual `quit()` closes
everything. The driver's geckodriver must be started with
`--allow-system-access`.

### Browser and Page Object Models

Content forthcoming.
