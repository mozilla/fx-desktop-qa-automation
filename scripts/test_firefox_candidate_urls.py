"""Tests for Firefox candidate URL resolution."""

import pytest

from scripts.firefox_candidate_urls import (
    candidate_download_url,
    github_environment,
    latest_build_from_html,
    validate_version,
)


@pytest.fixture()
def driver():
    """Keep resolver unit tests independent from the autouse browser driver."""
    return None


def test_latest_build_is_compared_numerically():
    html = """
    <a href="build1/">build1/</a>
    <a href="build10/">build10/</a>
    <a href="build2/">build2/</a>
    """

    assert latest_build_from_html(html) == 10


def test_non_build_links_are_ignored():
    html = """
    <a href="../">Parent Directory</a>
    <a href="build2/">build2/</a>
    <a href="build2.txt">build2.txt</a>
    <a href="build0/">build0/</a>
    """

    assert latest_build_from_html(html) == 2


def test_missing_build_raises_clear_error():
    with pytest.raises(ValueError, match="No buildN directories"):
        latest_build_from_html('<a href="../">Parent Directory</a>')


@pytest.mark.parametrize(
    "version", ("155.0", "155.0.1", "156.0b2", "153.0esr", "128.14.0esr")
)
def test_supported_versions(version):
    assert validate_version(version) == version


@pytest.mark.parametrize("version", ("155", "155.0a1", "155.0-candidates", "../155.0"))
def test_unsupported_version_is_rejected(version):
    with pytest.raises(ValueError, match="Unsupported Firefox version"):
        validate_version(version)


@pytest.mark.parametrize(
    ("platform", "expected_url"),
    (
        (
            "windows",
            "https://archive.mozilla.org/pub/firefox/candidates/155.0.1-candidates/build2/win64/en-US/Firefox%20Setup%20155.0.1.exe",
        ),
        (
            "macos",
            "https://archive.mozilla.org/pub/firefox/candidates/155.0.1-candidates/build2/mac/en-US/Firefox%20155.0.1.dmg",
        ),
        (
            "linux",
            "https://archive.mozilla.org/pub/firefox/candidates/155.0.1-candidates/build2/linux-x86_64/en-US/firefox-155.0.1.tar.xz",
        ),
    ),
)
def test_candidate_urls(platform, expected_url):
    assert candidate_download_url("155.0.1", 2, platform) == expected_url


@pytest.mark.parametrize(
    ("version", "platform", "expected_url"),
    (
        (
            "154.0",
            "windows",
            "https://archive.mozilla.org/pub/firefox/candidates/154.0-candidates/build1/win64/en-US/Firefox%20Setup%20154.0.exe",
        ),
        (
            "153.0esr",
            "macos",
            "https://archive.mozilla.org/pub/firefox/candidates/153.0esr-candidates/build1/mac/en-US/Firefox%20153.0esr.dmg",
        ),
    ),
)
def test_rc_and_esr_candidate_urls(version, platform, expected_url):
    assert candidate_download_url(version, 1, platform) == expected_url


def test_unknown_platform_raises_clear_error():
    with pytest.raises(ValueError, match="Unknown platform 'android'"):
        candidate_download_url("155.0.1", 2, "android")


def test_override_environment_does_not_fetch_a_build():
    assert (
        github_environment("155.0.1", "windows", "https://example.com/firefox.exe")
        == "MANUAL_DOWNLOAD_LINK=https://example.com/firefox.exe\nFX_VERSION=155.0.1"
    )


def test_override_rejects_newlines():
    with pytest.raises(ValueError, match="single line"):
        github_environment("", "linux", "https://example.com/file\nBAD=value")
