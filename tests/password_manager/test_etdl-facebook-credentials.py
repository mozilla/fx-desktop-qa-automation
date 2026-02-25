import json
import sys
from urllib.parse import urlparse

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import AutofillPopup
from modules.page_object import AboutLogins, GenericPage

ETLD_PLUS_ONE_URL = "https://www.facebook.com/"

SUBDOMAIN_URLS = [
    "https://ro-ro.facebook.com/",
    "https://fr-fr.facebook.com/",
    "https://www.prod.facebook.com/",
    "https://th-th.facebook.com/",
]

ETLD_USERNAME = "etld_user"
ETLD_PASSWORD = "etld_pass"

SUBDOMAIN_CREDENTIALS = {
    "https://ro-ro.facebook.com/": ("ro_user", "ro_pass"),
    "https://fr-fr.facebook.com/": ("fr_user", "fr_pass"),
    "https://www.prod.facebook.com/": ("prod_user", "prod_pass"),
    "https://th-th.facebook.com/": ("th_user", "th_pass"),
}

FROM_THIS_WEBSITE_TEXT = "From this website"


@pytest.fixture()
def test_case():
    return "2240890"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


@pytest.fixture()
def temp_selectors():
    # Facebook login fields + cookie dialog controls (content DOM)
    return {
        "facebook-username-field": {
            "selectorData": "input[name='email']",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "facebook-password-field": {
            "selectorData": "input[name='pass']",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        # Cookie consent modal (may or may not appear)
        "facebook-cookie-dialog": {
            "selectorData": "//div[@role='dialog'][.//text()[contains(.,'cookies') or contains(.,'Cookies')]]",
            "strategy": "xpath",
            "groups": ["doNotCache"],
        },
        "facebook-cookie-decline": {
            "selectorData": (
                "//div[@role='dialog']"
                "//*[self::button or @role='button']"
                "[contains(normalize-space(.),'Decline optional cookies') "
                "or contains(normalize-space(.),'Only allow essential cookies')]"
            ),
            "strategy": "xpath",
            "groups": ["doNotCache"],
        },
        "facebook-cookie-allow": {
            "selectorData": (
                "//div[@role='dialog']"
                "//*[self::button or @role='button']"
                "[contains(normalize-space(.),'Allow all cookies') "
                "or contains(normalize-space(.),'Accept all cookies')]"
            ),
            "strategy": "xpath",
            "groups": ["doNotCache"],
        },
    }


def _clear_field(el):
    """
    Cross-platform field clear:
    - Windows/Linux: CTRL + A
    - macOS: COMMAND + A
    """
    select_all_key = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
    el.send_keys(select_all_key, "a")
    el.send_keys(Keys.BACKSPACE)


def _assert_password_masked(password_element):
    # Masked == input type remains password (value may still be present in DOM)
    assert password_element.get_attribute("type") == "password"


def _host(url: str) -> str:
    return urlparse(url).netloc


def _extract_secondary_label(ac_comment: str) -> str:
    """
    On newer builds, Firefox stores JSON in ac-comment and the visible "secondary" label
    (e.g. "From this website", "ro-ro.facebook.com") is stored under:
      - data["secondary"] OR
      - data["fillMessageData"]["secondary"]
    Older builds may store plain text directly.
    """
    if not ac_comment:
        return ""

    # Older behavior: ac-comment is already the label
    if ac_comment == FROM_THIS_WEBSITE_TEXT:
        return ac_comment

    try:
        data = json.loads(ac_comment)
        if isinstance(data, dict):
            return data.get("secondary", "") or data.get("fillMessageData", {}).get(
                "secondary", ""
            )
    except Exception:
        pass

    return ac_comment


def _get_dropdown_entries_by_username(
    autofill_popup: AutofillPopup,
    expected_usernames: set[str],
) -> dict[str, str]:
    """
    Returns: {username(ac-value): secondary_label} for entries that match expected_usernames.
    Must be called in chrome context.
    """
    entries: dict[str, str] = {}
    for item in autofill_popup.get_elements("select-form-option"):
        username = item.get_attribute("ac-value")
        if username in expected_usernames:
            entries[username] = _extract_secondary_label(
                item.get_attribute("ac-comment")
            )
    return entries


def _dismiss_facebook_cookies_if_present(page: GenericPage) -> None:
    """
    Facebook sometimes shows a cookie consent modal that blocks clicks on the login fields.
    If present, dismiss it (prefer declining optional cookies).
    """
    dialogs = page.get_elements("facebook-cookie-dialog")
    if not dialogs:
        return

    decline_btns = page.get_elements("facebook-cookie-decline")
    allow_btns = page.get_elements("facebook-cookie-allow")

    btn = None
    if decline_btns:
        btn = decline_btns[0]
    elif allow_btns:
        btn = allow_btns[0]

    if btn:
        page.driver.execute_script("arguments[0].click();", btn)


def test_logins_autocomplete_includes_etld_plus_one_and_subdomains(
    driver: Firefox,
    temp_selectors,
):
    """
    Verify the autocomplete dropdown aggregates saved logins for eTLD+1 and subdomains,
    and that autofilled password remains masked.
    """
    about_logins = AboutLogins(driver)
    autofill_popup = AutofillPopup(driver)

    # Seed saved logins via about:logins (with small pauses as used in existing tests)
    about_logins.open()
    about_logins.add_login(ETLD_PLUS_ONE_URL, ETLD_USERNAME, ETLD_PASSWORD)

    for url in SUBDOMAIN_URLS:
        username, password = SUBDOMAIN_CREDENTIALS[url]
        about_logins.add_login(url, username, password)

    # Open eTLD+1 and reload (step 3)
    web_page = GenericPage(driver, url=ETLD_PLUS_ONE_URL).open()
    web_page.elements |= temp_selectors

    driver.refresh()
    _dismiss_facebook_cookies_if_present(web_page)

    # Trigger autocomplete on username field and select the eTLD+1 credential
    web_page.click_on("facebook-username-field")

    autofill_popup.ensure_autofill_dropdown_visible()
    with driver.context(driver.CONTEXT_CHROME):
        autofill_popup.click_on("select-form-option-by-value", labels=[ETLD_USERNAME])

    # Explicit wait for autofill to complete in content
    web_page.expect(
        lambda d: web_page.get_element("facebook-username-field").get_attribute("value")
        == ETLD_USERNAME
    )

    web_page.expect(
        lambda d: web_page.get_element("facebook-password-field").get_attribute("value")
        == ETLD_PASSWORD
    )
    _assert_password_masked(web_page.get_element("facebook-password-field"))

    expected_usernames = {ETLD_USERNAME} | {
        u for (u, _) in SUBDOMAIN_CREDENTIALS.values()
    }

    # Step 4: delete username -> dropdown shows all logins with correct secondary text
    username_el = web_page.get_element("facebook-username-field")
    _clear_field(username_el)
    web_page.click_on("facebook-username-field")

    autofill_popup.ensure_autofill_dropdown_visible()
    with driver.context(driver.CONTEXT_CHROME):
        entries = _get_dropdown_entries_by_username(autofill_popup, expected_usernames)

    assert expected_usernames.issubset(set(entries.keys()))
    assert entries[ETLD_USERNAME] == FROM_THIS_WEBSITE_TEXT

    assert entries[SUBDOMAIN_CREDENTIALS["https://ro-ro.facebook.com/"][0]] == _host(
        "https://ro-ro.facebook.com/"
    )
    assert entries[SUBDOMAIN_CREDENTIALS["https://fr-fr.facebook.com/"][0]] == _host(
        "https://fr-fr.facebook.com/"
    )
    assert entries[SUBDOMAIN_CREDENTIALS["https://www.prod.facebook.com/"][0]] == _host(
        "https://www.prod.facebook.com/"
    )
    assert entries[SUBDOMAIN_CREDENTIALS["https://th-th.facebook.com/"][0]] == _host(
        "https://th-th.facebook.com/"
    )

    # Step 5: select any username entry -> username + password fill, password masked
    chosen_url = "https://fr-fr.facebook.com/"
    chosen_username, chosen_password = SUBDOMAIN_CREDENTIALS[chosen_url]

    with driver.context(driver.CONTEXT_CHROME):
        autofill_popup.click_on("select-form-option-by-value", labels=[chosen_username])

    web_page.expect(
        lambda d: web_page.get_element("facebook-username-field").get_attribute("value")
        == chosen_username
    )
    web_page.expect(
        lambda d: web_page.get_element("facebook-password-field").get_attribute("value")
        == chosen_password
    )
    _assert_password_masked(web_page.get_element("facebook-password-field"))

    # Step 6: delete password -> dropdown shows all logins again (same expectations)
    password_el = web_page.get_element("facebook-password-field")
    web_page.click_on("facebook-password-field")
    _clear_field(password_el)
    web_page.click_on("facebook-password-field")

    autofill_popup.ensure_autofill_dropdown_visible()
    with driver.context(driver.CONTEXT_CHROME):
        entries_pw = _get_dropdown_entries_by_username(
            autofill_popup, expected_usernames
        )

    assert expected_usernames.issubset(set(entries_pw.keys()))
    assert entries_pw[ETLD_USERNAME] == FROM_THIS_WEBSITE_TEXT

    # Step 7: select any listed username from password dropdown -> only the masked password is auto-filled
    with driver.context(driver.CONTEXT_CHROME):
        autofill_popup.click_on("select-form-option-by-value", labels=[chosen_username])

    web_page.expect(
        lambda d: web_page.get_element("facebook-username-field").get_attribute("value")
        == chosen_username
    )
    web_page.expect(
        lambda d: web_page.get_element("facebook-password-field").get_attribute("value")
        == chosen_password
    )
    _assert_password_masked(web_page.get_element("facebook-password-field"))
