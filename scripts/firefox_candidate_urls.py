"""Build Firefox candidate download URLs for a requested version."""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import Request, urlopen

ARCHIVE_ROOT = "https://archive.mozilla.org/pub/firefox/candidates/"
VERSION_PATTERN = re.compile(
    r"^[1-9][0-9]*\.[0-9]+(?:b[1-9][0-9]*|(?:\.[0-9]+)?esr|\.[0-9]+)?$"
)
BUILD_PATTERN = re.compile(r"build([1-9][0-9]*)")


class LinkParser(HTMLParser):
    """Collect links from an HTML directory listing."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.links.extend(
                value for name, value in attrs if name == "href" and value
            )


def validate_version(version: str) -> str:
    """Return a supported Firefox candidate version or raise ``ValueError``."""
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(
            "Unsupported Firefox version. Expected a release, dot release, Beta, "
            "or ESR version such as 155.0, 155.0.1, 156.0b2, or 153.0esr."
        )
    return version


def latest_build_from_html(html: str) -> int:
    """Return the highest build number found in a candidate directory listing."""
    parser = LinkParser()
    parser.feed(html)

    builds: list[int] = []
    for link in parser.links:
        path_part = urlsplit(link).path.rstrip("/").rsplit("/", maxsplit=1)[-1]
        match = BUILD_PATTERN.fullmatch(path_part)
        if match:
            builds.append(int(match.group(1)))

    if not builds:
        raise ValueError("No buildN directories were found for this Firefox version.")
    return max(builds)


def find_latest_build(version: str, timeout: int = 30) -> int:
    """Fetch the candidate listing and return its highest build number."""
    version = validate_version(version)
    candidate_url = urljoin(ARCHIVE_ROOT, f"{version}-candidates/")
    request = Request(candidate_url, headers={"User-Agent": "STARfox CI"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        html = response.read().decode("utf-8")
    return latest_build_from_html(html)


def candidate_download_url(version: str, build: int, platform: str) -> str:
    """Return the archive URL for one Firefox candidate platform artifact."""
    version = validate_version(version)
    base_url = urljoin(ARCHIVE_ROOT, f"{version}-candidates/build{build}/")
    platform_parts = {
        "windows": ("win64/en-US/", f"Firefox Setup {version}.exe"),
        "macos": ("mac/en-US/", f"Firefox {version}.dmg"),
        "linux": ("linux-x86_64/en-US/", f"firefox-{version}.tar.xz"),
    }
    if platform not in platform_parts:
        expected = ", ".join(platform_parts)
        raise ValueError(f"Unknown platform {platform!r}; expected one of: {expected}.")
    directory, filename = platform_parts[platform]
    return urljoin(base_url, f"{directory}{quote(filename)}")


def github_environment(version: str, platform: str, override: str = "") -> str:
    """Return environment-file entries for a resolved or overridden download URL."""
    if "\r" in override or "\n" in override:
        raise ValueError("A URL override must be a single line.")
    if version:
        validate_version(version)

    if override:
        download_url = override
    elif version:
        build = find_latest_build(version)
        download_url = candidate_download_url(version, build, platform)
    else:
        raise ValueError("Provide a Firefox version or URL override.")

    entries = [f"MANUAL_DOWNLOAD_LINK={download_url}"]
    if version:
        entries.append(f"FX_VERSION={version}")
    return "\n".join(entries)


def main() -> None:
    """Print entries suitable for appending to the GitHub Actions environment."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("platform", choices=("windows", "macos", "linux"))
    parser.add_argument("--version", default="", help="Firefox candidate version")
    parser.add_argument("--override", default="", help="Optional platform URL override")
    args = parser.parse_args()

    try:
        print(github_environment(args.version, args.platform, args.override))
    except (ValueError, URLError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
