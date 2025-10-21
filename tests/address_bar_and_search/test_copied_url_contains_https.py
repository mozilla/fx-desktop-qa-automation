import pytest


@pytest.fixture()
def test_case():
    return "3028769"


def test_copied_url_contains_https():
    """
    C3028712 - URLs copied from address bar contain https tags
    """

    #