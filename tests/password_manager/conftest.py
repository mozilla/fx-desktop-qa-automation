import logging

import pytest
from faker import Faker
from faker.providers import internet, misc
from selenium.webdriver import Firefox

from modules.page_object import AboutLogins


@pytest.fixture()
def suite_id():
    return ("43517", "Password manager")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
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
def driver_and_saved_logins(driver: Firefox, faker: Faker, origins):
    """
    Adds 6 fake logins to the session's about:logins. The final two usernames are the same.
    Yields a Tuple of the WebDriver object under test and a five-element list of the
    unique usernames added. (Five, because the last element was reused.)

    logins = {"username@website": "password"}
    """
    faker.add_provider(internet)
    faker.add_provider(misc)

    def add_login(origin: str, username: str, password: str):
        logging.info("Adding login...")
        _about_logins = AboutLogins(driver).open()
        logging.info("about:logins opened. Clicking plus button...")
        _about_logins.click_add_login_button()
        logging.info("Plus button clicked. Adding new login...")
        _about_logins.create_new_login(
            {
                "origin": origin,
                "username": username,
                "password": password,
            }
        )

    usernames = []
    logins = {}
    for i in range(5):
        candidate_username = ""
        while candidate_username == "" or candidate_username[:5] in [
            u[:5] for u in usernames
        ]:
            candidate_username = faker.user_name()
        usernames.append(candidate_username)
        password = faker.password(length=15)
        add_login(origins[i], candidate_username, password)
        logins[candidate_username + "@" + origins[i]] = password

    # Add a cred with a matching username for a different origin
    password = faker.password(length=15)
    add_login(origins[-1], candidate_username, password)
    logins[candidate_username + "@" + origins[-1]] = password

    yield (driver, usernames, logins)
