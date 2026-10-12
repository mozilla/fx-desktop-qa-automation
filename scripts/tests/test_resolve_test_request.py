"""Unit tests for scripts/resolve_test_request.py (see TESTING_AS_A_SERVICE.md)."""

import pytest

from scripts.resolve_test_request import (
    RequestError,
    candidate_urls,
    channel_for,
    known_splits,
    latest_build,
    parse_platforms,
    resolve,
)

# a realistic archive.mozilla.org directory listing fragment
LISTING = """
<a href="/pub/firefox/candidates/155.0.1-candidates/build1/">build1/</a>
<a href="/pub/firefox/candidates/155.0.1-candidates/build2/">build2/</a>
<a href="/pub/firefox/candidates/155.0.1-candidates/build10/">build10/</a>
"""


class Args:
    def __init__(self, **kw):
        defaults = dict(
            firefox_version="",
            win_installer_link="",
            mac_installer_link="",
            linux_tarball_link="",
            channel="beta",
            test_set="smoke",
            platforms="win,mac,linux",
            fail_on="non-flaky-failure",
            verify_urls=False,
        )
        defaults.update(kw)
        self.__dict__.update(defaults)


def no_fetch(_url):
    raise AssertionError("network must not be touched for an explicit-URL request")


# --------------------------------------------------------------------------
# Version / channel / URL resolution
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version,expected",
    [("155.0.1", "rc"), ("155.0", "rc"), ("153.0esr", "esr"), ("156.0b2", "beta")],
)
def test_channel_for(version, expected):
    assert channel_for(version) == expected


def test_latest_build_picks_highest_not_last():
    """build10 must beat build2 - a lexical sort would get this wrong."""
    assert latest_build("155.0.1", fetch=lambda _: LISTING) == 10


def test_latest_build_errors_when_no_builds():
    with pytest.raises(RequestError, match="no buildN"):
        latest_build("155.0.1", fetch=lambda _: "<html>nothing here</html>")


def test_latest_build_wraps_network_failure():
    def boom(_url):
        raise OSError("connection refused")

    with pytest.raises(RequestError, match="could not list candidates"):
        latest_build("155.0.1", fetch=boom)


def test_candidate_urls_shape():
    urls = candidate_urls("155.0.1", 2)
    assert urls["win"].endswith("/build2/win64/en-US/Firefox%20Setup%20155.0.1.exe")
    assert urls["mac"].endswith("/build2/mac/en-US/Firefox%20155.0.1.dmg")
    assert urls["linux"].endswith("/build2/linux-x86_64/en-US/firefox-155.0.1.tar.xz")


def test_resolve_version_fills_all_three_links():
    out = resolve(Args(firefox_version="155.0.1"), fetch=lambda _: LISTING)
    assert out["firefox_version"] == "155.0.1-build10"
    assert out["channel"] == "rc"
    assert all(
        out[f"{k}_installer_link" if k != "linux" else "linux_tarball_link"]
        for k in ("win", "mac", "linux")
    )


def test_explicit_channel_is_not_overridden():
    out = resolve(
        Args(firefox_version="153.0esr", channel="custom"), fetch=lambda _: LISTING
    )
    assert out["channel"] == "custom"


# --------------------------------------------------------------------------
# Platform filtering (a dropped link means a skipped job in main.yml)
# --------------------------------------------------------------------------


def test_platform_filter_drops_unrequested_links():
    out = resolve(
        Args(firefox_version="155.0.1", platforms="linux"), fetch=lambda _: LISTING
    )
    assert out["win_installer_link"] == ""
    assert out["mac_installer_link"] == ""
    assert out["linux_tarball_link"]
    assert out["platforms"] == "linux"


def test_platform_order_is_normalised():
    assert parse_platforms("linux, win") == ["win", "linux"]
    assert parse_platforms("MAC") == ["mac"]


@pytest.mark.parametrize("raw", ["", "  ", "android", "win,solaris"])
def test_bad_platforms_rejected(raw):
    with pytest.raises(RequestError):
        parse_platforms(raw)


def test_explicit_link_for_unrequested_platform_is_dropped():
    with pytest.raises(RequestError, match="no build URL for any requested platform"):
        resolve(
            Args(
                win_installer_link="https://example.invalid/fx.exe", platforms="linux"
            ),
            fetch=no_fetch,
        )


# --------------------------------------------------------------------------
# Validation: fail in seconds, not after a 40-minute run
# --------------------------------------------------------------------------


def test_version_and_links_are_mutually_exclusive():
    with pytest.raises(RequestError, match="mutually exclusive"):
        resolve(
            Args(
                firefox_version="155.0.1",
                win_installer_link="https://example.invalid/a.exe",
            ),
            fetch=no_fetch,
        )


def test_empty_request_rejected():
    with pytest.raises(RequestError, match="nothing to test"):
        resolve(Args(), fetch=no_fetch)


@pytest.mark.parametrize(
    "bad", ["notaversion", "1x5.0", "155", "155.0.1.2", "155.0rc1"]
)
def test_invalid_version_rejected(bad):
    with pytest.raises(RequestError, match="invalid firefox_version"):
        resolve(Args(firefox_version=bad), fetch=lambda _: LISTING)


def test_unknown_test_set_rejected_with_the_valid_list():
    with pytest.raises(RequestError, match="unknown test_set 'smoek'"):
        resolve(
            Args(win_installer_link="https://example.invalid/a.exe", test_set="smoek"),
            fetch=no_fetch,
        )


def test_known_test_set_accepted():
    out = resolve(
        Args(win_installer_link="https://example.invalid/a.exe", test_set="smoke"),
        fetch=no_fetch,
    )
    assert out["test_set"] == "smoke"


def test_bad_fail_on_rejected():
    with pytest.raises(RequestError, match="fail_on must be one of"):
        resolve(
            Args(
                win_installer_link="https://example.invalid/a.exe", fail_on="sometimes"
            ),
            fetch=no_fetch,
        )


def test_real_manifest_defines_the_documented_splits():
    """The facade advertises these; if a rename lands, fail here not in prod."""
    splits = known_splits()
    for expected in ("smoke", "functional1", "functional2", "functional3", "nightly"):
        assert expected in splits, f"{expected} missing from manifests/key.yaml"


# --------------------------------------------------------------------------
# URL verification
# --------------------------------------------------------------------------


def test_missing_artifact_is_reported_per_platform():
    with pytest.raises(RequestError, match="no artifact for: mac"):
        resolve(
            Args(firefox_version="155.0.1", verify_urls=True),
            fetch=lambda _: LISTING,
            head=lambda url: "mac" not in url,
        )


def test_verification_skipped_for_explicit_links():
    """We did not build those URLs, so we do not second-guess them."""
    out = resolve(
        Args(
            win_installer_link="https://example.invalid/fx.exe",
            platforms="win",
            verify_urls=True,
        ),
        fetch=no_fetch,
        head=lambda _: (_ for _ in ()).throw(AssertionError("must not HEAD-check")),
    )
    assert out["win_installer_link"] == "https://example.invalid/fx.exe"
