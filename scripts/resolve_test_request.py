"""Validate and resolve a STARfox test request (see TESTING_AS_A_SERVICE.md).

Turns the service's public request contract (schemas/test-request-v1.json) into
the concrete installer URLs `main.yml` expects. Two jobs:

1. **Validate early.** A typo'd test set or an unsupported platform should fail
   in seconds, not after a caller has waited 40 minutes for a run that selected
   nothing.
2. **Resolve `firefox_version`** into archive.mozilla.org candidate URLs, picking
   the highest `buildN`. This replaces the inline bash in
   run-firefox-candidate.yml so the logic is unit-testable.

Platform filtering happens by omission: `main.yml` starts a platform job only
when that platform's link is non-empty, so dropping a URL drops the job. No
changes to `main.yml`'s job conditions are needed.

Writes resolved values to $GITHUB_OUTPUT. Exits 2 on an invalid request.
"""

import argparse
import os
import re
import sys
import urllib.error
import urllib.request

import yaml

MANIFEST_KEY = "manifests/key.yaml"
ARCHIVE_ROOT = "https://archive.mozilla.org/pub/firefox/candidates"
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+(\.[0-9]+)?(esr|b[0-9]+)?$")
BUILD_RE = re.compile(r"build([1-9][0-9]*)/")
PLATFORMS = ("win", "mac", "linux")
FAIL_ON = ("any-failure", "non-flaky-failure", "never")
CHANNELS = ("beta", "rc", "esr", "nightly", "custom")
TIMEOUT = 30


class RequestError(Exception):
    """The request is invalid. The message is shown to the caller verbatim."""


def channel_for(version: str) -> str:
    if version.endswith("esr"):
        return "esr"
    if re.search(r"b[0-9]+$", version):
        return "beta"
    return "rc"


def candidate_urls(version: str, build: int) -> dict[str, str]:
    base = f"{ARCHIVE_ROOT}/{version}-candidates/build{build}"
    return {
        "win": f"{base}/win64/en-US/Firefox%20Setup%20{version}.exe",
        "mac": f"{base}/mac/en-US/Firefox%20{version}.dmg",
        "linux": f"{base}/linux-x86_64/en-US/firefox-{version}.tar.xz",
    }


def read_url(url: str) -> str:
    with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:  # noqa: S310
        return resp.read().decode("utf-8", errors="replace")


def url_exists(url: str) -> bool:
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT):  # noqa: S310
            return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return False


def latest_build(version: str, fetch=read_url) -> int:
    """Highest buildN published for a candidate version."""
    root = f"{ARCHIVE_ROOT}/{version}-candidates/"
    try:
        listing = fetch(root)
    except Exception as exc:  # noqa: BLE001 - surfaced to the caller as-is
        raise RequestError(f"could not list candidates for {version}: {exc}") from exc
    builds = [int(m) for m in BUILD_RE.findall(listing)]
    if not builds:
        raise RequestError(f"no buildN directories found at {root}")
    return max(builds)


def known_splits(manifest_path: str = MANIFEST_KEY) -> set[str]:
    """Every split name defined anywhere in the manifest."""
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)
    found: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "splits" and isinstance(value, list):
                    found.update(v for v in value if isinstance(v, str))
                else:
                    walk(value)

    walk(manifest)
    return found


def parse_platforms(raw: str) -> list[str]:
    requested = [p.strip().lower() for p in raw.split(",") if p.strip()]
    if not requested:
        raise RequestError("platforms must name at least one of: win, mac, linux")
    unknown = [p for p in requested if p not in PLATFORMS]
    if unknown:
        raise RequestError(
            f"unsupported platform(s): {', '.join(unknown)}. Expected: {', '.join(PLATFORMS)}"
        )
    # preserve a stable order rather than the caller's
    return [p for p in PLATFORMS if p in requested]


def resolve(args, fetch=read_url, head=url_exists) -> dict[str, str]:
    """Validate the request and return the values main.yml needs."""
    links = {
        "win": args.win_installer_link.strip(),
        "mac": args.mac_installer_link.strip(),
        "linux": args.linux_tarball_link.strip(),
    }
    version = args.firefox_version.strip()

    if version and any(links.values()):
        raise RequestError(
            "firefox_version and the *_link inputs are mutually exclusive: "
            "give a version to resolve, or explicit URLs, not both"
        )
    if not version and not any(links.values()):
        raise RequestError(
            "nothing to test: supply firefox_version, or at least one of "
            "win_installer_link / mac_installer_link / linux_tarball_link"
        )
    if args.fail_on not in FAIL_ON:
        raise RequestError(f"fail_on must be one of: {', '.join(FAIL_ON)}")

    platforms = parse_platforms(args.platforms)

    splits = known_splits()
    if args.test_set not in splits:
        raise RequestError(
            f"unknown test_set {args.test_set!r}. Defined in {MANIFEST_KEY}: "
            f"{', '.join(sorted(splits))}"
        )

    channel = args.channel.strip().lower()
    resolved_version = version

    if version:
        if not VERSION_RE.match(version):
            raise RequestError(
                f"invalid firefox_version {version!r}. Examples: 155.0.1, 153.0esr, 156.0b2"
            )
        build = latest_build(version, fetch=fetch)
        links = candidate_urls(version, build)
        resolved_version = f"{version}-build{build}"
        if not channel or channel == "beta":
            # only infer when the caller did not deliberately pick one
            channel = channel_for(version)

    # platform filtering: drop the links we were not asked for
    links = {p: (url if p in platforms else "") for p, url in links.items()}

    if not any(links.values()):
        raise RequestError(
            f"no build URL for any requested platform ({', '.join(platforms)})"
        )

    if version and args.verify_urls:
        missing = [p for p, url in links.items() if url and not head(url)]
        if missing:
            raise RequestError(
                f"candidate build {resolved_version} has no artifact for: "
                f"{', '.join(missing)}. Try a different platform set or build."
            )

    if channel not in CHANNELS:
        raise RequestError(f"channel must be one of: {', '.join(CHANNELS)}")

    return {
        "win_installer_link": links["win"],
        "mac_installer_link": links["mac"],
        "linux_tarball_link": links["linux"],
        "channel": channel,
        "firefox_version": resolved_version,
        "test_set": args.test_set,
        "fail_on": args.fail_on,
        "platforms": ",".join(platforms),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Validate and resolve a STARfox test request."
    )
    ap.add_argument("--firefox-version", default="")
    ap.add_argument("--win-installer-link", default="")
    ap.add_argument("--mac-installer-link", default="")
    ap.add_argument("--linux-tarball-link", default="")
    ap.add_argument("--channel", default="beta")
    ap.add_argument("--test-set", default="smoke")
    ap.add_argument("--platforms", default="win,mac,linux")
    ap.add_argument("--fail-on", default="non-flaky-failure")
    ap.add_argument(
        "--no-verify-urls",
        dest="verify_urls",
        action="store_false",
        help="skip the HEAD check on resolved candidate URLs",
    )
    args = ap.parse_args(argv)

    try:
        resolved = resolve(args)
    except RequestError as exc:
        print(f"::error::Invalid test request: {exc}", file=sys.stderr)
        return 2

    for key, value in resolved.items():
        print(f"{key}={value}")

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            for key, value in resolved.items():
                fh.write(f"{key}={value}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
