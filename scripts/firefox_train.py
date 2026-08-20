"""Resolve the STARfox automation train from a Firefox artifact URL."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from posixpath import basename
from urllib.parse import unquote, urlsplit


NIGHTLY_ARCHIVE_URL = (
    "https://archive.mozilla.org/pub/firefox/nightly/latest-mozilla-central/"
)
NIGHTLY_ARTIFACT_SUFFIXES = {
    "mac": "dmg",
    "linux-x86_64": "tar.xz",
    "linux-aarch64": "tar.xz",
    "linux-i686": "tar.xz",
    "win64": "installer.exe",
    "win64-aarch64": "installer.exe",
    "win32": "installer.exe",
}
FIREFOX_VERSION_RE = re.compile(
    r"(?<!\d)"
    r"(?P<major>\d{2,3})\."
    r"(?P<minor>\d+)"
    r"(?:\.(?P<patch>\d{1,2}))?"
    r"(?P<suffix>[ab]\d+|esr)?"
    r"(?!\.\d)"
    r"(?![A-Za-z0-9])",
    re.IGNORECASE,
)
CANDIDATE_LABEL_RE = re.compile(
    r"^(?P<version>\d{2,3}\.\d+(?:\.\d{1,2})?(?:[ab]\d+|esr)?)"
    r"(?:-build(?P<build>\d+))?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FirefoxTrain:
    """Firefox build identity and its compatible automation ref."""

    channel: str
    version: str
    major: int
    automation_ref: str


class _ArchiveLinksParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.filenames = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.filenames.append(unquote(basename(urlsplit(href).path)))


def _nightly_version_key(version: str) -> tuple[int, int, int]:
    match = FIREFOX_VERSION_RE.fullmatch(version)
    if not match or not (match.group("suffix") or "").lower().startswith("a"):
        raise ValueError(f"Invalid Firefox Nightly version: {version!r}")
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("suffix")[1:]),
    )


def parse_candidate_label(label: str) -> tuple[FirefoxTrain, int | None]:
    """Parse a version optionally pinned to a candidate build directory."""
    match = CANDIDATE_LABEL_RE.fullmatch(label.strip())
    if not match:
        raise ValueError(f"Invalid Firefox candidate label: {label!r}")

    version = match.group("version").lower()
    build = int(match.group("build")) if match.group("build") else None
    train = resolve_train_from_artifact(
        f"https://archive.invalid/firefox-{version}.tar.xz"
    )
    return train, build


def resolve_train_from_artifact(artifact_url: str) -> FirefoxTrain:
    """Resolve a Firefox automation train from an archive URL."""
    parsed_url = urlsplit(artifact_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError(f"Expected an HTTP(S) artifact URL, got {artifact_url!r}")

    matches = list(FIREFOX_VERSION_RE.finditer(unquote(parsed_url.path)))
    if not matches:
        raise ValueError(
            "Could not find a Firefox version in the archive URL. Use a candidate "
            "URL or a final Nightly artifact URL, not a dated Nightly directory URL."
        )

    versions = {match.group(0).lower() for match in matches}
    if len(versions) != 1:
        raise ValueError(
            f"Artifact URL contains conflicting versions: {artifact_url!r}"
        )

    match = matches[-1]
    major = int(match.group("major"))
    suffix = (match.group("suffix") or "").lower()
    version = match.group(0).lower()

    if suffix.startswith("a"):
        channel = "nightly"
        automation_ref = "nightly"
    elif suffix.startswith("b"):
        channel = "beta"
        automation_ref = "main"
    elif suffix == "esr":
        channel = "esr"
        automation_ref = f"firefox{major}"
    else:
        channel = "release"
        automation_ref = f"firefox{major}"

    return FirefoxTrain(
        channel=channel,
        version=version,
        major=major,
        automation_ref=automation_ref,
    )


def select_nightly_artifact(
    html: str,
    platform: str,
    locale: str = "en-US",
    requested_version: str | None = None,
) -> tuple[str, FirefoxTrain]:
    """Select the newest matching artifact from a Nightly archive listing."""
    if platform not in NIGHTLY_ARTIFACT_SUFFIXES:
        raise ValueError(f"Unsupported Nightly platform: {platform!r}")

    filename_re = re.compile(
        rf"^firefox-(?P<version>\d{{2,3}}\.\d+a\d+)\."
        rf"{re.escape(locale)}\.{re.escape(platform)}\."
        rf"{re.escape(NIGHTLY_ARTIFACT_SUFFIXES[platform])}$",
        re.IGNORECASE,
    )
    parser = _ArchiveLinksParser()
    parser.feed(html)
    matches = []
    for filename in parser.filenames:
        match = filename_re.fullmatch(filename)
        if not match:
            continue
        version = match.group("version").lower()
        if requested_version and version != requested_version.lower():
            continue
        build = resolve_train_from_artifact(f"https://archive.invalid/{filename}")
        matches.append((_nightly_version_key(version), filename, build))

    if not matches:
        requested = f" version {requested_version}" if requested_version else ""
        raise ValueError(
            f"Could not find Nightly{requested} for {platform}/{locale} in archive."
        )

    _, filename, build = max(matches)
    return filename, build


def select_nightly_buildhub_files(
    html: str,
    platforms: Sequence[str],
    locale: str = "en-US",
) -> tuple[FirefoxTrain, dict[str, str]]:
    """Select one Nightly version with Buildhub metadata for every platform."""
    requested_platforms = tuple(dict.fromkeys(platforms))
    unsupported = set(requested_platforms) - NIGHTLY_ARTIFACT_SUFFIXES.keys()
    if unsupported:
        raise ValueError(
            f"Unsupported Nightly platforms: {', '.join(sorted(unsupported))}"
        )
    if not requested_platforms:
        raise ValueError("At least one Nightly platform is required.")

    platform_pattern = "|".join(re.escape(platform) for platform in requested_platforms)
    filename_re = re.compile(
        rf"^firefox-(?P<version>\d{{2,3}}\.\d+a\d+)\."
        rf"{re.escape(locale)}\.(?P<platform>{platform_pattern})\.buildhub\.json$",
        re.IGNORECASE,
    )
    any_nightly_file_re = re.compile(
        r"^firefox-(?P<version>\d{2,3}\.\d+a\d+)\.",
        re.IGNORECASE,
    )
    parser = _ArchiveLinksParser()
    parser.feed(html)
    available_versions = set()
    files_by_version: dict[str, dict[str, str]] = {}
    for filename in parser.filenames:
        version_match = any_nightly_file_re.match(filename)
        if version_match:
            available_versions.add(version_match.group("version").lower())
        match = filename_re.fullmatch(filename)
        if not match:
            continue
        version = match.group("version").lower()
        platform = match.group("platform").lower()
        files_by_version.setdefault(version, {})[platform] = filename

    if not available_versions:
        raise ValueError("Could not find a Firefox Nightly version in the archive.")

    version = max(available_versions, key=_nightly_version_key)
    metadata_for_version = files_by_version.get(version, {})
    missing_platforms = [
        platform
        for platform in requested_platforms
        if platform not in metadata_for_version
    ]
    if missing_platforms:
        raise ValueError(
            f"Newest Nightly {version} is missing Buildhub metadata for "
            f"{', '.join(missing_platforms)}."
        )

    build = resolve_train_from_artifact(
        f"https://archive.invalid/firefox-{version}.tar.xz"
    )
    return build, {
        platform: metadata_for_version[platform] for platform in requested_platforms
    }


def nightly_download_from_buildhub(
    metadata: Mapping,
    build: FirefoxTrain,
    platform: str,
    locale: str = "en-US",
) -> str:
    """Validate Buildhub metadata and return its immutable Nightly artifact URL."""
    target = metadata.get("target")
    download = metadata.get("download")
    if not isinstance(target, Mapping) or not isinstance(download, Mapping):
        raise ValueError(
            "Nightly Buildhub metadata is missing target or download data."
        )
    if (
        target.get("channel") != "nightly"
        or target.get("version") != build.version
        or target.get("platform") != platform
        or target.get("locale") != locale
    ):
        raise ValueError(
            f"Nightly Buildhub metadata does not match {build.version} "
            f"for {platform}/{locale}."
        )

    download_url = download.get("url")
    if not isinstance(download_url, str):
        raise ValueError("Nightly Buildhub metadata has no download URL.")
    parsed_url = urlsplit(download_url)
    if parsed_url.scheme != "https" or parsed_url.netloc != "archive.mozilla.org":
        raise ValueError(f"Unexpected Nightly download URL: {download_url!r}")

    expected_path = re.compile(
        r"^/pub/firefox/nightly/\d{4}/\d{2}/"
        r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-mozilla-central/"
        rf"firefox-{re.escape(build.version)}\.{re.escape(locale)}\."
        rf"{re.escape(platform)}\."
        rf"{re.escape(NIGHTLY_ARTIFACT_SUFFIXES[platform])}$",
        re.IGNORECASE,
    )
    if not expected_path.fullmatch(unquote(parsed_url.path)):
        raise ValueError(
            f"Nightly download URL is not a dated {platform}/{locale} artifact: "
            f"{download_url!r}"
        )
    return download_url


def main(argv: list[str] | None = None) -> int:
    """Print the resolved train as JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_url", help="Final Firefox archive artifact URL")
    args = parser.parse_args(argv)
    print(json.dumps(asdict(resolve_train_from_artifact(args.artifact_url))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
