"""Unit tests for Firefox candidate URL resolution."""

import unittest

from scripts.firefox_candidate_urls import (
    candidate_download_url,
    github_environment,
    latest_build_from_html,
    validate_version,
)


class FirefoxCandidateUrlTests(unittest.TestCase):
    def test_latest_build_is_compared_numerically(self):
        html = """
        <a href="build1/">build1/</a>
        <a href="build10/">build10/</a>
        <a href="build2/">build2/</a>
        """

        self.assertEqual(latest_build_from_html(html), 10)

    def test_non_build_links_are_ignored(self):
        html = """
        <a href="../">Parent Directory</a>
        <a href="build2/">build2/</a>
        <a href="build2.txt">build2.txt</a>
        <a href="build0/">build0/</a>
        """

        self.assertEqual(latest_build_from_html(html), 2)

    def test_missing_build_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "No buildN directories"):
            latest_build_from_html('<a href="../">Parent Directory</a>')

    def test_supported_versions(self):
        for version in ("155.0", "155.0.1", "156.0b2", "153.0esr", "128.14.0esr"):
            with self.subTest(version=version):
                self.assertEqual(validate_version(version), version)

    def test_unsupported_version_is_rejected(self):
        for version in ("155", "155.0a1", "155.0-candidates", "../155.0"):
            with self.subTest(version=version):
                with self.assertRaisesRegex(ValueError, "Unsupported Firefox version"):
                    validate_version(version)

    def test_candidate_urls(self):
        expected_urls = {
            "windows": "https://archive.mozilla.org/pub/firefox/candidates/155.0.1-candidates/build2/win64/en-US/Firefox%20Setup%20155.0.1.exe",
            "macos": "https://archive.mozilla.org/pub/firefox/candidates/155.0.1-candidates/build2/mac/en-US/Firefox%20155.0.1.dmg",
            "linux": "https://archive.mozilla.org/pub/firefox/candidates/155.0.1-candidates/build2/linux-x86_64/en-US/firefox-155.0.1.tar.xz",
        }

        for platform, expected_url in expected_urls.items():
            with self.subTest(platform=platform):
                self.assertEqual(
                    candidate_download_url("155.0.1", 2, platform), expected_url
                )

    def test_unknown_platform_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "Unknown platform 'android'"):
            candidate_download_url("155.0.1", 2, "android")

    def test_override_environment_does_not_fetch_a_build(self):
        self.assertEqual(
            github_environment("155.0.1", "windows", "https://example.com/firefox.exe"),
            "MANUAL_DOWNLOAD_LINK=https://example.com/firefox.exe\nFX_VERSION=155.0.1",
        )

    def test_override_rejects_newlines(self):
        with self.assertRaisesRegex(ValueError, "single line"):
            github_environment("", "linux", "https://example.com/file\nBAD=value")


if __name__ == "__main__":
    unittest.main()
