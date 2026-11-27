"""Make a running Nightly use another locale and region, for localized tests."""

import hashlib

import pytest
import requests
from selenium.webdriver import Firefox

from .restart import restart_firefox

# Language packs work on any platform, and there's no Windows Nightly folder for them
NIGHTLY_LANGPACK_URL = "https://archive.mozilla.org/pub/firefox/nightly/latest-mozilla-central-l10n/linux-x86_64/xpi/firefox-{version}.{locale}.langpack.xpi"

_INSTALL_LANGPACK_JS = """
const [url, hash, done] = arguments;
(async () => {
  const { AddonManager } = ChromeUtils.importESModule(
    "resource://gre/modules/AddonManager.sys.mjs"
  );
  const install = await AddonManager.getInstallForURL(url, { hash });
  await install.install();
  return install.addon.id;
})().then(done, e => done("error: " + e));
"""

_LOCALE_STATE_JS = """
const { Region } = ChromeUtils.importESModule("resource://gre/modules/Region.sys.mjs");
return {
  appLocale: Services.locale.appLocaleAsBCP47,
  requested: Services.locale.requestedLocales,
  region: Region.home,
};
"""


def install_nightly_langpack(driver: Firefox, locale: str) -> None:
    """Install Nightly's own `locale` language pack, skipping the test if the archive has none."""
    version = driver.capabilities["browserVersion"]
    url = NIGHTLY_LANGPACK_URL.format(version=version, locale=locale)
    response = requests.get(url, timeout=60)
    # The archive only keeps the newest Nightly's language packs
    if response.status_code == 404:
        pytest.skip(f"No Nightly language pack for {version}: {url}")
    response.raise_for_status()
    sha256 = hashlib.sha256(response.content).hexdigest()
    with driver.context(driver.CONTEXT_CHROME):
        driver.set_script_timeout(60)
        result = driver.execute_async_script(
            _INSTALL_LANGPACK_JS, url, f"sha256:{sha256}"
        )
    assert not str(result).startswith("error"), f"Language pack install: {result}"


def switch_locale_and_region(driver: Firefox, locale: str, region: str) -> None:
    """
    Install the `locale` language pack, request it, pin `browser.search.region`
    to `region` and restart so both apply. Needs a Nightly build.
    """
    install_nightly_langpack(driver, locale)
    with driver.context(driver.CONTEXT_CHROME):
        driver.execute_script(
            """
            Services.prefs.setStringPref("intl.locale.requested", arguments[0]);
            Services.prefs.setStringPref("browser.search.region", arguments[1]);
            Services.prefs.setBoolPref("browser.region.update.enabled", false);
            """,
            locale,
            region,
        )
    restart_firefox(driver)


def get_locale_state(driver: Firefox) -> dict:
    """Return the app locale, requested locales and Region.home of the running Firefox."""
    with driver.context(driver.CONTEXT_CHROME):
        return driver.execute_script(_LOCALE_STATE_JS)
