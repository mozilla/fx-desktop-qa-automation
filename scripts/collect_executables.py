"""Get the link to download Fx or Geckodriver, for any supported platform.
Use -g to get geckodriver, otherwise you will get Fx. Use -n to just get the Fx version number.
Set env var FX_CHANNEL to get non-beta, blank string for Release.
Set env var FX_LOCALE to get a different locale build.
Set env var FX_PLATFORM to get a platform other than current system.
Set env var FX_BUILD_BEFORE (ISO time) to get the newest Beta or Nightly published by then."""

import logging
from datetime import datetime, timedelta, timezone
from os import environ
from platform import uname
from sys import argv, exit
from time import sleep

import requests
from bs4 import BeautifulSoup

GECKO_API_URL = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"
BACKSTOP = "146.0b9"
# Used only when the GitHub API cannot be reached. Keep this current with the
# latest geckodriver release: tests/meta/test_version.py compares the running
# driver against the latest release on GitHub, so a stale pin fails CI.
GECKO_FALLBACK_VERSION = "0.37.1"
CANDIDATES_URL = "https://archive.mozilla.org/pub/firefox/candidates"
NIGHTLY_ARCHIVE_URL = "https://archive.mozilla.org/pub/firefox/nightly"
NIGHTLY_URL = f"{NIGHTLY_ARCHIVE_URL}/latest-mozilla-central"
# Steps back from the newest Beta before giving up on a pinned one
MAX_PIN_STEPS = 30
REQUEST_TIMEOUT = 10


def get_fx_platform():
    u = uname()
    _system = environ.get("FX_PLATFORM") or u.system
    if _system == "Darwin":
        return "mac"
    if _system == "Linux":
        # ARM specifications in uname().machine don't have 32/64
        if "64" in u.machine:
            return "linux-x86_64"
        elif "arm" in u.machine.lower():
            return "linux-aarch64"
        return "linux-i686"
    if _system == "Windows":
        if "arm" in u.machine.lower():
            return "win64-aarch64"
        elif "64" in u.machine:
            return "win64"
        return "win32"


def get_fx_executable_extension():
    u = uname()
    _system = environ.get("FX_PLATFORM") or u.system
    if _system == "Darwin":
        return "dmg"
    if _system == "Linux":
        return "xz"
    if _system == "Windows":
        return "exe"


def get_gd_platform():
    u = uname()
    _system = environ.get("FX_PLATFORM") or u.system
    if _system == "Darwin":
        return "macos"
    if _system == "Linux":
        if u.machine == "AMD64":
            return "linux-aarch64"
        if "64" in u.machine:
            return "linux64"
        return "linux32"
    if _system == "Windows":
        if u.machine == "AMD64" and not environ.get("GITHUB_ACTIONS"):
            return "win-aarch64"
        if "64" in u.machine:
            return "win64"
        return "win32"


def is_pull_request_run() -> bool:
    """True in a pull request run: GitHub pull_request event or Taskcluster level 1."""
    return (
        environ.get("GITHUB_EVENT_NAME") == "pull_request"
        or environ.get("MOZ_SCM_LEVEL") == "1"
    )


def get_build_dir(version: str, language: str) -> tuple[str, int]:
    """Return the URL of `version`'s latest build for this platform, and its number."""
    fx_download_dir_url = f"{CANDIDATES_URL}/{version}-candidates/"
    response = requests.get(fx_download_dir_url, timeout=REQUEST_TIMEOUT)
    build = 1
    if response.status_code < 300:
        soup = BeautifulSoup(response.text, "html.parser")
        for line in soup.find_all("a"):
            line_text = line.getText().split(".")
            if not line_text[0]:
                continue
            # Links look like "build2/", so [-2] is the build number
            build = max(int(line_text[0][-2]), build)
        fx_download_dir_url = (
            f"{fx_download_dir_url}build{build}/{get_fx_platform()}/{language}/"
        )
    return fx_download_dir_url, build


def build_numbers(version: str) -> list[int]:
    """Return `version`'s candidate build numbers, newest first."""
    names = listing(f"{CANDIDATES_URL}/{version}-candidates/")
    return sorted(
        (int(n[5:-1]) for n in names if n.startswith("build") and n[5:-1].isdigit()),
        reverse=True,
    )


def build_cutoff() -> datetime | None:
    """Return FX_BUILD_BEFORE (a PR's creation time) as a UTC datetime, or None."""
    value = environ.get("FX_BUILD_BEFORE")
    if not value:
        return None
    cutoff = datetime.fromisoformat(value)
    return (
        cutoff if cutoff.tzinfo else cutoff.replace(tzinfo=timezone.utc)
    ).astimezone(timezone.utc)


def listing(dir_url: str) -> dict[str, datetime | None]:
    """Return each entry of an archive.mozilla.org folder with its upload time (UTC)."""
    response = requests.get(dir_url, timeout=REQUEST_TIMEOUT)
    if response.status_code >= 300:
        return {}
    entries = {}
    for row in BeautifulSoup(response.text, "html.parser").find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 4 or not cells[1].a:
            continue
        uploaded = cells[3].getText().strip()
        entries[cells[1].a.getText()] = (
            datetime.strptime(uploaded, "%d-%b-%Y %H:%M").replace(tzinfo=timezone.utc)
            if uploaded
            else None
        )
    return entries


def installer_uploaded_at(build_dir_url: str) -> datetime | None:
    """Return when this platform's installer was uploaded to `build_dir_url`, or None."""
    return next(
        (
            uploaded
            for name, uploaded in listing(build_dir_url).items()
            if name.split(".")[-1] == get_fx_executable_extension()
        ),
        None,
    )


def has_installer(build_dir_url: str) -> bool:
    """True once this platform's installer is in `build_dir_url`."""
    return installer_uploaded_at(build_dir_url) is not None


def previous_beta(version: str) -> str:
    """Return the Beta before `version`, e.g. 159.0b1 gives 158.0's last Beta."""
    (major_minor, beta) = version.split("b")
    if int(beta) > 1:
        return f"{major_minor}b{int(beta) - 1}"
    (major, minor) = (int(n) for n in major_minor.split("."))
    previous = f"{major}.{minor - 1}b1" if minor else f"{major - 1}.0b1"
    # Walk up from b1 until the next Beta is missing
    while True:
        (major_minor, beta) = previous.split("b")
        next_beta = f"{major_minor}b{int(beta) + 1}"
        response = requests.get(
            f"{CANDIDATES_URL}/{next_beta}-candidates/", timeout=REQUEST_TIMEOUT
        )
        # Only a 404 means no such Beta; fail on anything else rather than guess
        if response.status_code == 404:
            return previous
        response.raise_for_status()
        previous = next_beta


def nightly_versions(platform: str, ext: str) -> list[str]:
    """Return the Nightly versions with an installer for `platform`, newest first."""
    response = requests.get(f"{NIGHTLY_URL}/", timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    suffix = f".en-US.{platform}.{ext}"
    versions = [
        name.removeprefix("firefox-").removesuffix(suffix)
        for name in (
            a.getText()
            for a in BeautifulSoup(response.text, "html.parser").find_all("a")
        )
        if name.startswith("firefox-") and name.endswith(suffix)
    ]
    return sorted(versions, key=lambda v: int(v.split(".")[0]), reverse=True)


def nightly_build_before(
    cutoff: datetime, platform: str, ext: str
) -> tuple[str, str] | None:
    """Return the URL and version of the newest Nightly for `platform` uploaded by `cutoff`."""
    stamp = f"{cutoff:%Y-%m-%d-%H-%M-%S}"
    # Folders are named after the build's start time (UTC); look back a month at most
    for month in (cutoff, cutoff.replace(day=1) - timedelta(days=1)):
        month_url = f"{NIGHTLY_ARCHIVE_URL}/{month:%Y/%m}/"
        builds = sorted(
            (
                name
                for name in listing(month_url)
                if name.endswith("-mozilla-central/") and name[:19] <= stamp
            ),
            reverse=True,
        )
        for build in builds:
            for name, uploaded in listing(f"{month_url}{build}").items():
                if (
                    name.startswith("firefox-")
                    and name.endswith(f".en-US.{platform}.{ext}")
                    and uploaded
                    and uploaded <= cutoff
                ):
                    version = name.removeprefix("firefox-").split(".en-US.")[0]
                    return f"{month_url}{build}{name}", version
    return None


def main(args):
    number_only = False
    output = ""
    if "-g" in args:
        location_in_env = environ.get("GECKO_DOWNLOAD_URL")
        if location_in_env:
            return location_in_env

        gecko_rs_obj = requests.get(GECKO_API_URL).json()

        # Retry on a missing "assets" key rather than on a falsy object. A
        # rate-limited reply is a populated dict carrying only "message", so the
        # old falsy check broke out on the first pass and fell straight through
        # to the pinned fallback. In mac, the request sometimes fails outright.
        for _ in range(4):
            if gecko_rs_obj.get("assets"):
                break
            sleep(2)
            gecko_rs_obj = requests.get(GECKO_API_URL).json()

        # Still nothing, so fall back to the pinned release. Warn loudly: the
        # download otherwise looks successful and the mismatch only surfaces
        # later, as a test_gecko_version failure that names no cause.
        if not gecko_rs_obj.get("assets"):
            gd_platform = get_gd_platform()
            ext = "zip" if "win" in gd_platform else "tar.gz"
            logging.warning(
                "GitHub API returned no geckodriver assets (%s). This is usually "
                "rate limiting: the API allows 60 calls/hour per IP and CI "
                "runners share addresses. Falling back to pinned v%s; "
                "test_gecko_version will fail if that is not the latest release.",
                gecko_rs_obj.get("message", "no message in response"),
                GECKO_FALLBACK_VERSION,
            )
            print(
                "https://github.com/mozilla/geckodriver/releases/download/"
                f"v{GECKO_FALLBACK_VERSION}/"
                f"geckodriver-v{GECKO_FALLBACK_VERSION}-{gd_platform}.{ext}"
            )
            exit()

        urls = [
            a.get("browser_download_url")
            for a in gecko_rs_obj.get("assets")
            if not a.get("browser_download_url").endswith(".asc")
        ]
        gecko_download_url = [u for u in urls if get_gd_platform() in u][0]
        output = gecko_download_url

    else:
        if "-n" in args:
            number_only = True
            version_in_env = environ.get("FX_VERSION")
            if version_in_env:
                return version_in_env
        else:
            location_in_env = environ.get("FX_DOWNLOAD_URL")
            if location_in_env:
                return location_in_env

        logging.warning(f"env channel: {environ.get('FX_CHANNEL')}")
        channel = environ.get("FX_CHANNEL")
        # if channel doesn't exist use beta, if blank leave blank (for Release)
        # ...otherwise prepend hyphen
        if channel is None:
            channel = "-beta"
        elif channel:
            channel = f"-{channel.lower()}"

        language = environ.get("FX_LOCALE")
        if not language:
            language = "en-US"

        if channel == "-nightly":
            train_resp = requests.get(
                "https://whattrainisitnow.com/api/release/schedule/?version=nightly"
            )
            train_resp.raise_for_status()
            train_json = train_resp.json()
            current_nightly = train_json.get("version")
            alpha = f"{current_nightly}a1"
            pfm = get_fx_platform()
            ext = get_fx_executable_extension()
            if "linux" in pfm:
                ext = "tar.xz"
            elif "win" in pfm:
                ext = "installer.exe"

            cutoff = build_cutoff()
            pinned = nightly_build_before(cutoff, pfm, ext) if cutoff else None
            if pinned:
                (url, version) = pinned
                logging.warning(f"Pinned to {url}, the newest Nightly by {cutoff}")
                return version if number_only else url
            if cutoff:
                logging.warning(f"No {pfm} Nightly by {cutoff}, so using the newest")

            # On merge day the new version is announced before its first Nightly
            # is built, so PR runs use the newest Nightly that has an installer
            if is_pull_request_run():
                available = nightly_versions(pfm, ext)
                if alpha not in available:
                    older = [
                        v
                        for v in available
                        if int(v.split(".")[0]) < int(alpha.split(".")[0])
                    ]
                    if older:
                        logging.warning(
                            f"No {pfm} installer for {alpha} yet, "
                            f"so this pull request run uses {older[0]}"
                        )
                        alpha = older[0]

            if number_only:
                return alpha
            return f"{NIGHTLY_URL}/firefox-{alpha}.en-US.{pfm}.{ext}"

        if channel == "-devedition":
            # Devedition has special requirements as it's testing a release

            this_devedition = BACKSTOP
            fx_download_dir_url = (
                "https://archive.mozilla.org/pub/devedition/releases/135.0b5/"
            )

            while True:
                (major, _) = this_devedition.split(".")
                major = int(major)
                this_devedition = f"{major + 1}.0b3"
                next_candidate = (
                    "https://archive.mozilla.org/pub/devedition/releases/"
                    f"{this_devedition}/"
                )

                rs = requests.get(next_candidate)
                if rs.status_code > 399:
                    break

                fx_download_dir_url = next_candidate

            devedition_version = fx_download_dir_url.split("/")[-2]
            fx_download_dir_url = (
                f"{fx_download_dir_url}{get_fx_platform()}/{language}/"
            )

        else:
            # Anything but devedition / nightly

            candidate_exists = True
            this_beta = BACKSTOP
            logging.warning(f"channel: {channel}")
            while candidate_exists:
                (major, minor_beta) = this_beta.split(".")
                (minor, beta) = minor_beta.split("b")
                major = int(major)
                minor = int(minor)
                beta = int(beta)

                next_major = f"{major + 1}.0b1"
                fx_download_dir_url = (
                    "https://archive.mozilla.org/pub/firefox/candidates/"
                    f"{next_major}-candidates/"
                )
                if channel == "-rc":
                    fx_download_dir_url = fx_download_dir_url.replace("b1", "")
                rs = requests.get(fx_download_dir_url)
                if rs.status_code < 300:
                    latest_beta_ver = next_major
                    this_beta = next_major
                    continue

                next_minor = f"{major}.{minor + 1}b1"
                fx_download_dir_url = (
                    "https://archive.mozilla.org/pub/firefox/candidates/"
                    f"{next_minor}-candidates/"
                )
                if channel == "-rc":
                    fx_download_dir_url = fx_download_dir_url.replace("b1", "")
                rs = requests.get(fx_download_dir_url)
                if rs.status_code < 300:
                    latest_beta_ver = next_minor
                    this_beta = next_minor
                    continue

                if channel != "-rc":
                    next_beta = f"{major}.{minor}b{beta + 1}"
                    fx_download_dir_url = (
                        "https://archive.mozilla.org/pub/firefox/candidates/"
                        f"{next_beta}-candidates/"
                    )
                    rs = requests.get(fx_download_dir_url)
                    if rs.status_code < 300:
                        latest_beta_ver = next_beta
                        this_beta = next_beta
                        continue

                candidate_exists = False

            # Look for the latest build
            if channel == "-rc":
                latest_beta_ver = latest_beta_ver.replace("b1", "")
            (fx_download_dir_url, build) = get_build_dir(latest_beta_ver, language)
            cutoff = build_cutoff() if channel == "-beta" else None

            # Pinned PR runs step back to the newest Beta build uploaded by the
            # cutoff; a respin (build2) after the cutoff falls back to build1
            if cutoff:
                pinned = None
                version = latest_beta_ver
                for _ in range(MAX_PIN_STEPS):
                    for number in build_numbers(version):
                        build_dir = (
                            f"{CANDIDATES_URL}/{version}-candidates/build{number}/"
                            f"{get_fx_platform()}/{language}/"
                        )
                        uploaded = installer_uploaded_at(build_dir)
                        if uploaded and uploaded <= cutoff:
                            pinned = (build_dir, number)
                            break
                    if pinned:
                        break
                    version = previous_beta(version)
                if pinned:
                    (fx_download_dir_url, build) = pinned
                    logging.warning(
                        f"Pinned to {version}-build{build}, the newest Beta by {cutoff}"
                    )
                else:
                    logging.warning(f"No Beta by {cutoff}, so using the newest")

            # On release day a Beta's folders appear before its installers, so
            # PR runs fall back to the previous Beta
            elif (
                channel == "-beta"
                and is_pull_request_run()
                and not has_installer(fx_download_dir_url)
            ):
                previous = previous_beta(latest_beta_ver)
                logging.warning(
                    f"No {get_fx_platform()} installer for {latest_beta_ver} yet, "
                    f"so this pull request run uses {previous}"
                )
                (fx_download_dir_url, build) = get_build_dir(previous, language)

        # Get the corresponding executable
        response = requests.get(fx_download_dir_url)
        status = response.status_code
        response_text = None
        for _ in range(3):
            if status < 300:
                response_text = response.text
            else:
                sleep(3)
                response = requests.get(fx_download_dir_url)
                status = response.status_code

        logging.warning(f"Collecting executable at {fx_download_dir_url}")

        if response_text is None:
            exit(f"Could not find build at {fx_download_dir_url}.")

        # Parse the HTML content
        soup = BeautifulSoup(response_text, "html.parser")

        executable_name = ""
        # Extract the text of each line
        for line in soup.find_all("a"):
            line_text = line.getText().split(".")
            if not line_text[0]:
                continue
            # Get the executable name
            if line_text[-1] == get_fx_executable_extension():
                executable_name = line.getText().replace(" ", "%20")

        fx_download_executable_url = rf"{fx_download_dir_url}{executable_name}"
        if number_only:
            if channel == "-devedition":
                output = devedition_version
            else:
                number_cand = fx_download_dir_url.split("/")[6]
                number = number_cand.split("-")[0]
                output = f"{number}-build{build}"
        else:
            output = fx_download_executable_url
    return output


def get_fx_version():
    return main(["-n"])


if __name__ == "__main__":
    print(main(argv))
