from time import sleep, time

import pytest

from modules.util import Utilities


@pytest.fixture()
def suite_id():
    return ("65334", "Address Bar 138+")


@pytest.fixture(scope="session")
def httpserver_listen_address():
    """Set port for local http server"""
    return ("127.0.0.1", 5312)


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [
        ("browser.aboutConfig.showWarning", False),
        ("privacy.donottrackheader.enabled", False),
        ("telemetry.fog.test.localhost_port", 5312),
        ("datareporting.healthreport.uploadEnabled", True),
        ("browser.newtabpage.enabled", True),
        ("browser.newtabpage.activity-stream.system.showSponsored", True),
        ("browser.newtabpage.activity-stream.showSponsoredTopSites", True),
        ("browser.topsites.useRemoteSetting", True),
        ("browser.topsites.contile.enabled", True),
        ("browser.search.region", "US"),
        ("browser.urlbar.scotchBonnet.enableOverride", True),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def search_modes():
    return {
        "site": ["Google", "Amazon", "Bing", "DuckDuckGo", "eBay", "Wikipedia"],
        "browser": [
            ("*", "Bookmarks"),
            ("%", "Tabs"),
            ("^", "History"),
            (">", "Actions"),
        ],
    }


@pytest.fixture()
def google_telemetry_runner():
    def _assert_json_value(
        utils: Utilities, json_data, path: str, expected_value: int
    ) -> bool:
        result = utils.assert_json_value(json_data, path, expected_value)
        if isinstance(result, tuple):
            return result[0]
        return result

    def _is_google_captcha_page(driver) -> bool:
        page_source = driver.page_source.lower()
        current_url = driver.current_url.lower()
        return "recaptcha" in page_source or "google.com/sorry" in current_url

    def _telemetry_paths_recorded(
        driver,
        telemetry_cls,
        telemetry_expectations,
        telemetry_timeout: int,
        telemetry_load_wait: int,
        raw_json_wait: int,
        poll_interval: int,
    ) -> bool:
        utils = Utilities()
        end_time = time() + telemetry_timeout

        while time() < end_time:
            telemetry = telemetry_cls(driver).open()
            sleep(telemetry_load_wait)
            telemetry.open_raw_json_data()
            sleep(raw_json_wait)

            try:
                json_data = utils.decode_url(driver)
                if all(
                    _assert_json_value(utils, json_data, path, expected_value)
                    for path, expected_value in telemetry_expectations
                ):
                    return True
            except Exception:
                pass

            sleep(poll_interval)

        return False

    def _run(
        driver,
        telemetry_cls,
        search_action,
        telemetry_expectations,
        post_search_action=None,
        max_captcha_attempts: int = 5,
        after_search_wait: int = 5,
        after_action_wait: int = 0,
        after_reset_wait: int = 2,
        telemetry_timeout: int = 15,
        telemetry_load_wait: int = 2,
        raw_json_wait: int = 1,
        poll_interval: int = 1,
    ):
        for attempt in range(1, max_captcha_attempts + 1):
            driver.get("about:newtab")
            search_action()
            sleep(after_search_wait)

            if _is_google_captcha_page(driver):
                if attempt < max_captcha_attempts:
                    driver.delete_all_cookies()
                    driver.get("about:newtab")
                    sleep(after_reset_wait)
                    continue
                pytest.skip(
                    f"Google CAPTCHA triggered repeatedly after "
                    f"{max_captcha_attempts} attempts."
                )

            if post_search_action:
                post_search_action()
                if after_action_wait:
                    sleep(after_action_wait)

            if _telemetry_paths_recorded(
                driver=driver,
                telemetry_cls=telemetry_cls,
                telemetry_expectations=telemetry_expectations,
                telemetry_timeout=telemetry_timeout,
                telemetry_load_wait=telemetry_load_wait,
                raw_json_wait=raw_json_wait,
                poll_interval=poll_interval,
            ):
                return

            formatted_paths = "\n".join(path for path, _ in telemetry_expectations)
            pytest.fail(
                f"Telemetry paths were not recorded within {telemetry_timeout} "
                f"seconds:\n{formatted_paths}"
            )

    return _run
