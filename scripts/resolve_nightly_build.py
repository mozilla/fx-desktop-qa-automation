"""Resolve manual installer URLs or today's complete morning Firefox Nightly."""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ARCHIVE_ROOT = "https://archive.mozilla.org/pub/firefox/nightly"
REQUEST_TIMEOUT_SECONDS = 30
REQUEST_RETRIES = 3


class LinkParser(HTMLParser):
    """Extract links from Mozilla's archive directory listings."""

    def __init__(self):
        super().__init__()
        self.links: set[str] = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.links.add(value)


def fetch_links(url: str) -> set[str]:
    """Read a directory listing, retrying network failures."""
    for attempt in range(REQUEST_RETRIES + 1):
        try:
            with urllib.request.urlopen(
                url, timeout=REQUEST_TIMEOUT_SECONDS
            ) as response:
                html = response.read().decode("utf-8")
            parser = LinkParser()
            parser.feed(html)
            return parser.links
        except (urllib.error.URLError, TimeoutError):
            if attempt == REQUEST_RETRIES:
                raise
            time.sleep(2**attempt)

    raise RuntimeError("Unable to read archive listing.")


def discover_build(build_date: date, cutoff: int) -> dict[str, str]:
    """Find the newest complete morning build for the supplied UTC date."""
    archive = f"{ARCHIVE_ROOT}/{build_date:%Y/%m}/"
    pattern = re.compile(
        rf"{build_date.isoformat()}-(\d{{2}})-\d{{2}}-\d{{2}}-mozilla-central/"
    )
    directories = sorted(
        {
            link
            for link in fetch_links(archive)
            if (match := pattern.fullmatch(link)) and int(match[1]) < cutoff
        },
        reverse=True,
    )

    for directory in directories:
        build_url = archive + directory
        try:
            files = fetch_links(build_url)
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"::warning::Could not read {build_url}: {error}")
            continue

        windows_files = [
            name
            for name in files
            if re.fullmatch(r"firefox-[0-9][^/]*\.en-US\.win64\.zip", name)
        ]
        if not windows_files:
            continue

        # Sort numeric version components, matching the shell's version sort.
        win_file = max(
            windows_files,
            key=lambda name: tuple(int(n) for n in re.findall(r"\d+", name)),
        )
        prefix = win_file.removesuffix(".en-US.win64.zip")
        mac_file = f"{prefix}.en-US.mac.dmg"
        linux_file = f"{prefix}.en-US.linux-x86_64.tar.xz"
        if linux_file not in files:
            linux_file = f"{prefix}.en-US.linux-x86_64.tar.bz2"

        if mac_file in files and linux_file in files:
            return {
                "win_installer_link": build_url + win_file,
                "mac_installer_link": build_url + mac_file,
                "linux_tarball_link": build_url + linux_file,
            }

    raise ValueError(
        f"No complete morning Nightly found for {build_date} UTC. "
        "The build may not be published yet; rerun after publication."
    )


def resolve_links() -> dict[str, str]:
    """Preserve supplied platforms, or discover today's morning build."""
    links = {
        "win_installer_link": os.environ.get("WIN_LINK", ""),
        "mac_installer_link": os.environ.get("MAC_LINK", ""),
        "linux_tarball_link": os.environ.get("LINUX_LINK", ""),
    }
    if any(links.values()):
        return links

    cutoff_value = os.environ.get("MORNING_CUTOFF_HOUR_UTC", "12")
    if not re.fullmatch(r"[0-9]{1,2}", cutoff_value) or int(cutoff_value) > 23:
        raise ValueError("MORNING_CUTOFF_HOUR_UTC must be between 0 and 23.")

    build_date = datetime.now(timezone.utc).date()
    return discover_build(build_date, int(cutoff_value))


def write_github_outputs(links: dict[str, str]) -> None:
    """Write installer outputs and a GitHub Actions summary."""
    if output := os.environ.get("GITHUB_OUTPUT"):
        with Path(output).open("a", encoding="utf-8") as file:
            for name, url in links.items():
                file.write(f"{name}={url}\n")

    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(summary).open("a", encoding="utf-8") as file:
            file.write(
                "### Resolved Nightly installers\n\n"
                "| Platform | URL |\n"
                "| --- | --- |\n"
                f"| Windows | {links['win_installer_link']} |\n"
                f"| macOS | {links['mac_installer_link']} |\n"
                f"| Linux | {links['linux_tarball_link']} |\n"
            )


def main() -> int:
    try:
        links = resolve_links()
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1

    write_github_outputs(links)
    print(json.dumps(links, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
