"""Unit tests for Firefox train resolution and branch planning.

The filename intentionally does not match pytest's ``test_*.py`` pattern.
These tests are isolated from the repository's autouse WebDriver fixture.
"""

import json
import unittest
from unittest.mock import Mock, patch

from scripts import collect_executables
from scripts.firefox_branches import (
    BranchPlan,
    PromotionPlan,
    plan_branch_action,
    plan_promotion,
)
from scripts.firefox_train import (
    NIGHTLY_ARCHIVE_URL,
    FirefoxTrain,
    nightly_download_from_buildhub,
    parse_candidate_label,
    resolve_train_from_artifact,
    select_nightly_artifact,
    select_nightly_buildhub_files,
)


class FirefoxTrainTests(unittest.TestCase):
    def test_beta_candidate_artifact(self):
        artifact_url = (
            "https://archive.mozilla.org/pub/firefox/candidates/"
            "151.0b9-candidates/build1/linux-x86_64/en-US/"
            "firefox-151.0b9.tar.xz"
        )

        self.assertEqual(
            resolve_train_from_artifact(artifact_url),
            FirefoxTrain(
                channel="beta",
                version="151.0b9",
                major=151,
                automation_ref="main",
            ),
        )

    def test_nightly_artifact(self):
        artifact_url = (
            "https://archive.mozilla.org/pub/firefox/nightly/2026/08/"
            "2026-08-18-09-20-26-mozilla-central/"
            "firefox-156.0a1.en-US.linux-aarch64.tar.xz"
        )

        self.assertEqual(
            resolve_train_from_artifact(artifact_url),
            FirefoxTrain(
                channel="nightly",
                version="156.0a1",
                major=156,
                automation_ref="nightly",
            ),
        )

    def test_release_candidate(self):
        archive_url = (
            "https://archive.mozilla.org/pub/firefox/candidates/"
            "154.0-candidates/build1/"
        )

        self.assertEqual(
            resolve_train_from_artifact(archive_url),
            FirefoxTrain(
                channel="release",
                version="154.0",
                major=154,
                automation_ref="firefox154",
            ),
        )

    def test_dot_release_candidate(self):
        archive_url = (
            "https://archive.mozilla.org/pub/firefox/candidates/153.0.4-candidates/"
        )

        self.assertEqual(
            resolve_train_from_artifact(archive_url),
            FirefoxTrain(
                channel="release",
                version="153.0.4",
                major=153,
                automation_ref="firefox153",
            ),
        )

        two_digit_patch_url = archive_url.replace("153.0.4", "153.0.12")
        self.assertEqual(
            resolve_train_from_artifact(two_digit_patch_url),
            FirefoxTrain(
                channel="release",
                version="153.0.12",
                major=153,
                automation_ref="firefox153",
            ),
        )

        with self.assertRaises(ValueError):
            resolve_train_from_artifact(archive_url.replace("153.0.4", "153.0.123"))

    def test_esr_candidate(self):
        archive_url = (
            "https://archive.mozilla.org/pub/firefox/candidates/153.0esr-candidates/"
        )

        self.assertEqual(
            resolve_train_from_artifact(archive_url),
            FirefoxTrain(
                channel="esr",
                version="153.0esr",
                major=153,
                automation_ref="firefox153",
            ),
        )

    def test_candidate_label_keeps_exact_build(self):
        train, build = parse_candidate_label("151.0b9-build2")
        self.assertEqual(train.version, "151.0b9")
        self.assertEqual(train.automation_ref, "main")
        self.assertEqual(build, 2)

        release_train, release_build = parse_candidate_label("154.0-build1")
        self.assertEqual(release_train.channel, "release")
        self.assertEqual(release_build, 1)


class FirefoxBranchPlanTests(unittest.TestCase):
    nightly = FirefoxTrain("nightly", "156.0a1", 156, "nightly")
    beta = FirefoxTrain("beta", "155.0b9", 155, "main")
    release = FirefoxTrain("release", "154.0", 154, "firefox154")

    def test_nightly_uses_nightly_branch(self):
        self.assertEqual(
            plan_branch_action(
                self.nightly,
                {"refs/heads/main", "refs/heads/nightly"},
            ),
            BranchPlan(
                action="use",
                branch="nightly",
                source_ref=None,
                channel="nightly",
                version="156.0a1",
                reason="The compatible automation branch exists.",
            ),
        )

    def test_beta_uses_main(self):
        plan = plan_branch_action(self.beta, {"origin/main", "origin/nightly"})
        self.assertEqual(plan.action, "use")
        self.assertEqual(plan.branch, "main")

    def test_release_requires_numbered_branch(self):
        plan = plan_branch_action(self.release, {"main", "nightly"})
        self.assertEqual(plan.action, "missing")
        self.assertEqual(plan.branch, "firefox154")

    def test_rc_uses_active_beta_branch_before_archive_exists(self):
        plan = plan_branch_action(
            self.release,
            {"main", "nightly"},
            execution_channel="rc",
        )
        self.assertEqual(plan.action, "use")
        self.assertEqual(plan.branch, "main")

    def test_rc_uses_numbered_branch_after_beta_is_archived(self):
        plan = plan_branch_action(
            self.release,
            {"main", "nightly", "firefox154"},
            execution_channel="rc",
        )
        self.assertEqual(plan.action, "use")
        self.assertEqual(plan.branch, "firefox154")


class FirefoxPromotionPlanTests(unittest.TestCase):
    beta_156_b1 = FirefoxTrain("beta", "156.0b1", 156, "main")
    beta_156_b2 = FirefoxTrain("beta", "156.0b2", 156, "main")

    def test_missing_nightly_is_bootstrapped_from_main(self):
        plan = plan_promotion(self.beta_156_b2, {"main"})
        self.assertEqual(plan.action, "bootstrap")
        self.assertEqual(plan.source_ref, "main")
        self.assertEqual(plan.target_ref, "nightly")

    def test_api_promotion_is_blocked_until_nightly_is_bootstrapped(self):
        plan = plan_promotion(
            self.beta_156_b2,
            {"main"},
            promotion_requested=True,
            released_major=155,
        )
        self.assertEqual(plan.action, "blocked")
        self.assertIn("bootstrapped", plan.reason)

    def test_beta_one_promotes_and_applies_retention(self):
        self.assertEqual(
            plan_promotion(
                self.beta_156_b1,
                {"main", "nightly", "firefox153", "firefox154"},
                retention=2,
            ),
            PromotionPlan(
                action="promote",
                beta_version="156.0b1",
                beta_major=156,
                released_major=155,
                archive_branch="firefox155",
                source_ref="nightly",
                target_ref="main",
                delete_branches=("firefox153",),
                reason=(
                    "Archive the outgoing Beta, promote nightly to main, and retain "
                    "only the newest 2 numbered branches."
                ),
            ),
        )

    def test_later_beta_waits_without_api_request(self):
        plan = plan_promotion(self.beta_156_b2, {"main", "nightly"})
        self.assertEqual(plan.action, "noop")
        self.assertEqual(plan.delete_branches, ())

    def test_api_request_can_promote_after_beta_one(self):
        plan = plan_promotion(
            self.beta_156_b2,
            {"main", "nightly"},
            promotion_requested=True,
            released_major=155,
        )
        self.assertEqual(plan.action, "promote")
        self.assertEqual(plan.archive_branch, "firefox155")

    def test_existing_archive_makes_promotion_idempotent(self):
        plan = plan_promotion(
            self.beta_156_b1,
            {"main", "nightly", "firefox153", "firefox154", "firefox155"},
            retention=2,
        )
        self.assertEqual(plan.action, "noop")
        self.assertEqual(plan.delete_branches, ("firefox153",))

    def test_missing_main_blocks_transition(self):
        plan = plan_promotion(self.beta_156_b1, {"nightly"})
        self.assertEqual(plan.action, "blocked")


class NightlyDiscoveryTests(unittest.TestCase):
    archive_html = """
    <a href="firefox-155.0a1.en-US.linux-x86_64.tar.xz">old</a>
    <a href="firefox-156.0a1.en-US.mac.dmg">other platform</a>
    <a href="firefox-156.0a1.fr.linux-x86_64.tar.xz">other locale</a>
    <a href="firefox-156.0a1.en-US.linux-x86_64.tar.xz">current</a>
    <a href="firefox-156.0a1.en-US.win64.buildhub.json">win metadata</a>
    <a href="firefox-156.0a1.en-US.mac.buildhub.json">mac metadata</a>
    <a href="firefox-156.0a1.en-US.linux-x86_64.buildhub.json">linux metadata</a>
    <a href="firefox-157.0a1.en-US.win64.buildhub.json">incomplete newer version</a>
    """
    complete_archive_html = archive_html.replace(
        '<a href="firefox-157.0a1.en-US.win64.buildhub.json">'
        "incomplete newer version</a>",
        "",
    )
    dated_urls = {
        "win64": (
            "https://archive.mozilla.org/pub/firefox/nightly/2026/08/"
            "2026-08-18-09-20-26-mozilla-central/"
            "firefox-156.0a1.en-US.win64.installer.exe"
        ),
        "mac": (
            "https://archive.mozilla.org/pub/firefox/nightly/2026/08/"
            "2026-08-18-09-20-26-mozilla-central/"
            "firefox-156.0a1.en-US.mac.dmg"
        ),
        "linux-x86_64": (
            "https://archive.mozilla.org/pub/firefox/nightly/2026/08/"
            "2026-08-18-09-20-26-mozilla-central/"
            "firefox-156.0a1.en-US.linux-x86_64.tar.xz"
        ),
    }

    def nightly_response(self, url):
        response = Mock(status_code=200)
        if url == NIGHTLY_ARCHIVE_URL:
            response.text = self.complete_archive_html
            return response

        platform = next(
            platform
            for platform in self.dated_urls
            if f".{platform}.buildhub.json" in url
        )
        response.json.return_value = {
            "target": {
                "channel": "nightly",
                "version": "156.0a1",
                "platform": platform,
                "locale": "en-US",
            },
            "download": {"url": self.dated_urls[platform]},
        }
        return response

    def test_selects_newest_matching_nightly(self):
        filename, build = select_nightly_artifact(
            self.archive_html,
            "linux-x86_64",
        )
        self.assertEqual(filename, "firefox-156.0a1.en-US.linux-x86_64.tar.xz")
        self.assertEqual(build.version, "156.0a1")

    def test_selects_one_complete_buildhub_version(self):
        build, metadata_files = select_nightly_buildhub_files(
            self.complete_archive_html,
            ("win64", "mac", "linux-x86_64"),
        )
        self.assertEqual(build.version, "156.0a1")
        self.assertEqual(
            metadata_files,
            {
                "win64": "firefox-156.0a1.en-US.win64.buildhub.json",
                "mac": "firefox-156.0a1.en-US.mac.buildhub.json",
                "linux-x86_64": ("firefox-156.0a1.en-US.linux-x86_64.buildhub.json"),
            },
        )

    def test_does_not_fall_back_when_newest_nightly_is_incomplete(self):
        with self.assertRaisesRegex(ValueError, "Newest Nightly 157.0a1"):
            select_nightly_buildhub_files(
                self.archive_html,
                ("win64", "mac", "linux-x86_64"),
            )

    def test_detects_newest_nightly_before_buildhub_metadata_appears(self):
        archive_without_new_metadata = self.archive_html.replace(
            "firefox-157.0a1.en-US.win64.buildhub.json",
            "firefox-157.0a1.en-US.win64.installer.exe",
        )
        with self.assertRaisesRegex(ValueError, "Newest Nightly 157.0a1"):
            select_nightly_buildhub_files(
                archive_without_new_metadata,
                ("win64", "mac", "linux-x86_64"),
            )

    def test_validates_immutable_buildhub_download(self):
        build = FirefoxTrain("nightly", "156.0a1", 156, "nightly")
        metadata = self.nightly_response(
            NIGHTLY_ARCHIVE_URL + "firefox-156.0a1.en-US.linux-x86_64.buildhub.json"
        ).json()
        self.assertEqual(
            nightly_download_from_buildhub(
                metadata,
                build,
                "linux-x86_64",
            ),
            self.dated_urls["linux-x86_64"],
        )

    def test_rejects_mutable_buildhub_download(self):
        build = FirefoxTrain("nightly", "156.0a1", 156, "nightly")
        metadata = self.nightly_response(
            NIGHTLY_ARCHIVE_URL + "firefox-156.0a1.en-US.linux-x86_64.buildhub.json"
        ).json()
        metadata["download"]["url"] = (
            NIGHTLY_ARCHIVE_URL + "firefox-156.0a1.en-US.linux-x86_64.tar.xz"
        )

        with self.assertRaisesRegex(ValueError, "not a dated"):
            nightly_download_from_buildhub(
                metadata,
                build,
                "linux-x86_64",
            )

    @patch.dict(
        "os.environ",
        {"FX_CHANNEL": "nightly", "FX_LOCALE": "en-US"},
        clear=True,
    )
    @patch("scripts.collect_executables.get_fx_platform", return_value="linux-x86_64")
    @patch("scripts.collect_executables.requests.get")
    def test_collect_executables_returns_nightly_version_and_url(
        self,
        mock_get,
        _mock_platform,
    ):
        mock_get.side_effect = self.nightly_response

        self.assertEqual(collect_executables.main(["-n"]), "156.0a1")
        self.assertEqual(
            collect_executables.main([]),
            self.dated_urls["linux-x86_64"],
        )
        self.assertEqual(mock_get.call_count, 4)

    @patch("scripts.collect_executables.requests.get")
    def test_collects_one_pinned_nightly_build_set(self, mock_get):
        mock_get.side_effect = self.nightly_response

        build_set = json.loads(collect_executables.main(["--nightly-build-set"]))

        self.assertEqual(build_set["version"], "156.0a1")
        self.assertEqual(build_set["major"], 156)
        self.assertEqual(
            build_set["downloads"],
            {
                "win64": self.dated_urls["win64"],
                "mac": self.dated_urls["mac"],
            },
        )
        self.assertNotIn("linux-x86_64", build_set["downloads"])
        self.assertEqual(mock_get.call_count, 3)


class PinnedCandidateTests(unittest.TestCase):
    def test_latest_candidate_build_handles_multiple_digits(self):
        archive_html = """
        <a href="../">../</a>
        <a href="build1/">build1/</a>
        <a href="build2/">build2/</a>
        <a href="build10/">build10/</a>
        <a href="not-a-build/">not-a-build/</a>
        """

        self.assertEqual(collect_executables.latest_candidate_build(archive_html), 10)

    def test_latest_candidate_build_defaults_to_one(self):
        self.assertEqual(
            collect_executables.latest_candidate_build('<a href="../">../</a>'),
            1,
        )

    @patch.dict(
        "os.environ",
        {
            "FX_CHANNEL": "beta",
            "FX_LOCALE": "en-US",
            "FX_VERSION": "151.0b9-build2",
        },
        clear=True,
    )
    @patch("scripts.collect_executables.get_fx_platform", return_value="linux-x86_64")
    @patch("scripts.collect_executables.get_fx_executable_extension", return_value="xz")
    @patch("scripts.collect_executables.requests.get")
    def test_beta_download_uses_pinned_candidate_and_build(
        self,
        mock_get,
        _mock_extension,
        _mock_platform,
    ):
        mock_get.return_value = Mock(
            status_code=200,
            text='<a href="firefox-151.0b9.tar.xz">firefox-151.0b9.tar.xz</a>',
        )

        self.assertEqual(
            collect_executables.main([]),
            "https://archive.mozilla.org/pub/firefox/candidates/"
            "151.0b9-candidates/build2/linux-x86_64/en-US/"
            "firefox-151.0b9.tar.xz",
        )
        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
