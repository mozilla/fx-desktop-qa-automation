import hashlib
import json
from urllib.parse import quote

import pytest
import requests
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "1549409"


LANGUAGES = [("it", "Lingua")]
NIGHTLY_LANGPACK_URL = "https://archive.mozilla.org/pub/firefox/nightly/latest-mozilla-central-l10n/linux-x86_64/xpi/firefox-{version}.{locale}.langpack.xpi"


@pytest.fixture()
def nightly_langpacks(driver: Firefox, browser_name: str):
    """On Nightly, point Firefox at its own language packs, since AMO only has Beta and Release ones."""
    if browser_name != "Nightly":
        return
    fx_version = driver.capabilities["browserVersion"]
    results = []
    for locale, _ in LANGUAGES:
        url = NIGHTLY_LANGPACK_URL.format(version=fx_version, locale=locale)
        response = requests.get(url, timeout=60)
        # The archive only keeps the newest Nightly's language packs
        if response.status_code == 404:
            pytest.skip(f"No Nightly language pack for {fx_version}: {url}")
        response.raise_for_status()
        sha256 = hashlib.sha256(response.content).hexdigest()
        results.append(
            {
                "target_locale": locale,
                "current_compatible_version": {
                    "files": [
                        {"platform": "all", "url": url, "hash": f"sha256:{sha256}"}
                    ]
                },
            }
        )
    listing = quote(json.dumps({"results": results}))
    with driver.context(driver.CONTEXT_CHROME):
        driver.execute_script(
            "Services.prefs.setStringPref('extensions.getAddons.langpacks.url', arguments[0]);",
            f"data:application/json,{listing}",
        )


@pytest.mark.usefixtures("nightly_langpacks")
@pytest.mark.parametrize("shortform, localized_text", LANGUAGES)
def test_language_pack_install_about_preferences(
    driver: Firefox, shortform: str, localized_text: str
):
    """
    C1549409: language packs can be installed from about:preferences and firefox is correctly localized
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="paneLanguages")

    about_prefs.open()
    about_prefs.set_alternative_language(shortform)

    about_prefs.open()
    about_prefs.element_attribute_contains(
        "browser-language-heading", "label", localized_text
    )
