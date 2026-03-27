import json
import time
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
            "selectorData": (
                "//div[@role='dialog'][.//text()[contains(.,'cookies') or contains(.,'Cookies')]]"
            ),
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


def _platform_select_all_key(driver: Firefox) -> str:
    caps = driver.capabilities or {}
    platform = (caps.get("platformName") or caps.get("platform") or "").lower()
    if "mac" in platform or "darwin" in platform:
        return Keys.COMMAND
    return Keys.CONTROL


def _clear_field(driver: Firefox, el) -> None:
    select_all = _platform_select_all_key(driver)
    el.send_keys(select_all, "a")
    el.send_keys(Keys.BACKSPACE)


def _assert_password_masked(password_element) -> None:
    assert password_element.get_attribute("type") == "password"


def _host(url: str) -> str:
    return urlparse(url).netloc


def _parse_secondary_from_ac_comment(raw: str) -> str:
    """
    Some builds expose ac-comment as a plain string ("From this website").
    Others expose a JSON string containing e.g. {"secondary":"From this website", ...}.
    """
    if not raw:
        return ""
    raw = raw.strip()
    if raw.startswith("{") and raw.endswith("}"):
        try:
            data = json.loads(raw)
            # The string we want is usually at top-level "secondary"
            sec = data.get("secondary")
            if isinstance(sec, str):
                return sec
        except Exception:
            pass
    return raw


def _get_dropdown_entries_by_username(
    autofill_popup: AutofillPopup, expected_usernames: set[str]
) -> dict[str, str]:
    """
    Returns {username(ac-value): secondary_text} for entries that match expected_usernames.
    Must be called in chrome context.
    """
    entries: dict[str, str] = {}
    for item in autofill_popup.get_elements("select-form-option"):
        username = item.get_attribute("ac-value")
        if username in expected_usernames:
            comment_raw = item.get_attribute("ac-comment")
            entries[username] = _parse_secondary_from_ac_comment(comment_raw)
    return entries


def _get_username_order_in_popup(autofill_popup: AutofillPopup) -> list[str]:
    """
    Must be called in chrome context.
    Returns the ac-value list in the order displayed in the popup.
    """
    order: list[str] = []
    for item in autofill_popup.get_elements("select-form-option"):
        val = item.get_attribute("ac-value")
        if val:  # ignore empty/footers
            order.append(val)
    return order


def _choose_username_via_keyboard(
    driver: Firefox,
    web_page: GenericPage,
    autofill_popup: AutofillPopup,
    field_name: str,
    desired_username: str,
) -> None:
    web_page.click_on(field_name)
    autofill_popup.ensure_autofill_dropdown_visible()

    with driver.context(driver.CONTEXT_CHROME):
        order = _get_username_order_in_popup(autofill_popup)

    assert desired_username in order, (
        f"'{desired_username}' not found in popup. Order={order}"
    )

    idx = order.index(desired_username)

    field_el = web_page.get_element(field_name)
    # First ArrowDown highlights the first entry, so press ArrowDown idx+1 times.
    for _ in range(idx + 1):
        field_el.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.05)
    field_el.send_keys(Keys.ENTER)


def _dismiss_facebook_cookies_if_present(page: GenericPage) -> None:
    dialogs = page.get_elements("facebook-cookie-dialog")
    if not dialogs:
        return

    decline_btns = page.get_elements("facebook-cookie-decline")
    allow_btns = page.get_elements("facebook-cookie-allow")

    btn = decline_btns[0] if decline_btns else (allow_btns[0] if allow_btns else None)
    if btn:
        page.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)


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

    # Seed saved logins via about:logins
    about_logins.open()
    about_logins.add_login(ETLD_PLUS_ONE_URL, ETLD_USERNAME, ETLD_PASSWORD)
    time.sleep(1)

    for url in SUBDOMAIN_URLS:
        username, password = SUBDOMAIN_CREDENTIALS[url]
        about_logins.add_login(url, username, password)
        time.sleep(1)

    web_page = GenericPage(driver, url=ETLD_PLUS_ONE_URL).open()
    web_page.elements |= temp_selectors

    _dismiss_facebook_cookies_if_present(web_page)

    # Step 3: select the eTLD+1 credential
    _choose_username_via_keyboard(
        driver, web_page, autofill_popup, "facebook-username-field", ETLD_USERNAME
    )

    web_page.element_attribute_contains(
        "facebook-username-field", "value", ETLD_USERNAME
    )
    web_page.element_attribute_contains(
        "facebook-password-field", "value", ETLD_PASSWORD
    )
    _assert_password_masked(web_page.get_element("facebook-password-field"))

    expected_usernames = {ETLD_USERNAME} | {
        u for (u, _) in SUBDOMAIN_CREDENTIALS.values()
    }

    # Step 4: clear username -> dropdown shows all logins + correct secondary text
    username_el = web_page.get_element("facebook-username-field")
    _clear_field(driver, username_el)
    web_page.click_on("facebook-username-field")

    autofill_popup.ensure_autofill_dropdown_visible()
    with driver.context(driver.CONTEXT_CHROME):
        entries = _get_dropdown_entries_by_username(autofill_popup, expected_usernames)

    assert expected_usernames.issubset(set(entries.keys()))
    assert entries[ETLD_USERNAME] == FROM_THIS_WEBSITE_TEXT

    assert (
        _host("https://ro-ro.facebook.com/")
        in entries[SUBDOMAIN_CREDENTIALS["https://ro-ro.facebook.com/"][0]]
    )
    assert (
        _host("https://fr-fr.facebook.com/")
        in entries[SUBDOMAIN_CREDENTIALS["https://fr-fr.facebook.com/"][0]]
    )
    assert (
        _host("https://www.prod.facebook.com/")
        in entries[SUBDOMAIN_CREDENTIALS["https://www.prod.facebook.com/"][0]]
    )
    assert (
        _host("https://th-th.facebook.com/")
        in entries[SUBDOMAIN_CREDENTIALS["https://th-th.facebook.com/"][0]]
    )

    # Step 5: select any username entry -> username + password fill, password masked
    chosen_url = "https://fr-fr.facebook.com/"
    chosen_username, chosen_password = SUBDOMAIN_CREDENTIALS[chosen_url]

    _choose_username_via_keyboard(
        driver, web_page, autofill_popup, "facebook-username-field", chosen_username
    )

    web_page.element_attribute_contains(
        "facebook-username-field", "value", chosen_username
    )
    web_page.element_attribute_contains(
        "facebook-password-field", "value", chosen_password
    )
    _assert_password_masked(web_page.get_element("facebook-password-field"))

    # Step 6: clear password -> dropdown shows all logins again (same expectations)
    web_page.click_on("facebook-password-field")
    password_el = web_page.get_element("facebook-password-field")
    _clear_field(driver, password_el)
    web_page.click_on("facebook-password-field")

    autofill_popup.ensure_autofill_dropdown_visible()
    with driver.context(driver.CONTEXT_CHROME):
        entries_pw = _get_dropdown_entries_by_username(
            autofill_popup, expected_usernames
        )

    assert expected_usernames.issubset(set(entries_pw.keys()))
    assert entries_pw[ETLD_USERNAME] == FROM_THIS_WEBSITE_TEXT

    # Step 7: select a username from password dropdown -> password fills (masked)
    _choose_username_via_keyboard(
        driver, web_page, autofill_popup, "facebook-password-field", chosen_username
    )

    web_page.element_attribute_contains(
        "facebook-username-field", "value", chosen_username
    )
    web_page.element_attribute_contains(
        "facebook-password-field", "value", chosen_password
    )
    _assert_password_masked(web_page.get_element("facebook-password-field"))
