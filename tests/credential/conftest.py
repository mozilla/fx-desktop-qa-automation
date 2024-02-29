import pytest
from selenium.webdriver import Firefox

from modules.util import BrowserActions
from modules.shadow_dom import AboutLogins
from faker import Faker
from faker.providers import internet
from faker.providers import misc


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []


@pytest.fixture()
def origins():
    return [
        "facebook.com",
        "instagram.com",
        "tiktok.com",
        "twitter.com",
        "bsky.app",
        "mozilla.social",
    ]


@pytest.fixture()
def driver_and_saved_usernames(driver: Firefox, faker: Faker, origins):
    """
    Adds 6 fake logins to the session's about:logins. The final two usernames are the same.
    Yields a Tuple of the WebDriver object under test and a five-element list of the
    unique usernames added. (Five, because the last element was reused.)
    """
    ba = BrowserActions(driver)
    faker.add_provider(internet)
    faker.add_provider(misc)

    def add_login(origin: str, username: str, password: str):
        driver.get("about:logins")
        about_logins = AboutLogins(driver)
        about_logins.add_login_button().click()
        ba.clear_and_fill(about_logins.login_item_by_type("origin"), origin)
        ba.clear_and_fill(about_logins.login_item_by_type("username"), username)
        ba.clear_and_fill(about_logins.login_item_by_type("password"), password)
        try:
            about_logins.add_login_button()
        except:
            about_logins.login_item_save_changes_button().click()

    usernames = []
    for i in range(5):
        candidate_username = ""
        while candidate_username == "" or candidate_username[:5] in [
            u[:5] for u in usernames
        ]:
            candidate_username = faker.user_name()
        usernames.append(candidate_username)
        add_login(origins[i], candidate_username, faker.password(length=15))

    # Add a cred with a matching username for a different origin
    add_login(origins[-1], candidate_username, faker.password(length=15))

    yield (driver, usernames)
