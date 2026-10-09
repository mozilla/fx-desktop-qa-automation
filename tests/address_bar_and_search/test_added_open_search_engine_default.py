import pytest
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox, Keys

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_prefs import AboutPrefs

SEARCH_ENGINE = "Starfox Search"
TEXT = "test"
TEST_TEXT = "Firefox"

# A local site that advertises an OpenSearch engine. A real site
# (addons.mozilla.org) served a bot challenge instead of its OpenSearch file to
# CI machines, so Firefox couldn't add the engine there.
PAGE = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>{SEARCH_ENGINE}</title>
    <link rel="search" type="application/opensearchdescription+xml"
          title="{SEARCH_ENGINE}" href="/opensearch.xml" />
  </head>
  <body><h1>{SEARCH_ENGINE}</h1></body>
</html>"""

OPENSEARCH = """<?xml version="1.0" encoding="UTF-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName>{name}</ShortName>
  <Description>{name}</Description>
  <InputEncoding>UTF-8</InputEncoding>
  <Url type="text/html" method="get" template="{search_url}?q={{searchTerms}}" />
</OpenSearchDescription>"""


@pytest.fixture()
def test_case():
    return "3028769"


@pytest.fixture()
def search_site():
    """
    Serve the site and its OpenSearch engine. Uses its own server on a free
    port: the suite's httpserver is pinned to port 5312, which only one xdist
    worker can bind at a time.
    """
    server = HTTPServer(host="127.0.0.1", port=0)
    server.start()
    server.expect_request("/").respond_with_data(PAGE, content_type="text/html")
    server.expect_request("/opensearch.xml").respond_with_data(
        OPENSEARCH.format(name=SEARCH_ENGINE, search_url=server.url_for("/search")),
        content_type="application/opensearchdescription+xml",
    )
    server.expect_request("/search").respond_with_data(
        "<html><body>Starfox results</body></html>", content_type="text/html"
    )
    yield server
    server.stop()


def test_added_open_search_engine_default(driver: Firefox, search_site: HTTPServer):
    """
    C3028769 - Added Open Search Engine can be made default search engine
    """

    # Instantiate objects
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")
    tabs = TabBar(driver)

    # Open website that has autodiscovery
    driver.get(search_site.url_for("/"))

    # Click in the address bar and delete/add a letter in the URL to enter the edit mode
    nav.type_in_awesome_bar(TEXT)

    # Open the Unified Search button and click on the option to add the search engine :
    # "Add + name_of_search_engine"
    nav.add_search_mode(SEARCH_ENGINE)

    # Open about:preferences#search in a new tab
    prefs.open()

    # Set the newly added engine as a default engine.
    prefs.select_default_search_engine_by_key(SEARCH_ENGINE)

    # Open a new tab and in the address bar type a search string and press enter
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    nav.type_in_awesome_bar(TEST_TEXT + Keys.ENTER)

    # Check that search is performed with the newly added default engine and search results
    # are displayed
    assert nav.url_contains(search_site.url_for("/search") + f"?q={TEST_TEXT}")
