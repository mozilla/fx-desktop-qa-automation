"""Get the link to download Fx or Geckodriver, for any supported platform.
Use -g to get geckodriver, otherwise you will get Fx. Use -n to just get the Fx version number.
Set env var FX_CHANNEL to get non-beta, blank string for Release.
Set env var FX_LOCALE to get a different locale build.
Set env var FX_PLATFORM to get a platform other than current system."""

import logging
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


def github_headers() -> dict:
    """
    Authorization header for the GitHub API, when a token is available.

    Unauthenticated calls are capped at 60/hour per IP, which CI runners share
    and routinely exhaust. A rate-limited reply is a populated JSON object with
    no "assets" key, so without a token the geckodriver lookup quietly drops to
    GECKO_FALLBACK_VERSION instead of failing.
    """
    token = environ.get("GITHUB_TOKEN") or environ.get("GH_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}


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


def main(args):
    number_only = False
    output = ""
    if "-g" in args:
        location_in_env = environ.get("GECKO_DOWNLOAD_URL")
        if location_in_env:
            return location_in_env

        gecko_rs_obj = requests.get(GECKO_API_URL, headers=github_headers()).json()

        # Retry on a missing "assets" key rather than on a falsy object. A
        # rate-limited reply is a populated dict carrying only "message", so the
        # old falsy check broke out on the first pass and fell straight through
        # to the pinned fallback. In mac, the request sometimes fails outright.
        for _ in range(4):
            if gecko_rs_obj.get("assets"):
                break
            sleep(2)
            gecko_rs_obj = requests.get(GECKO_API_URL, headers=github_headers()).json()

        # Still nothing, so fall back to the pinned release. Warn loudly: the
        # download otherwise looks successful and the mismatch only surfaces
        # later, as a test_gecko_version failure that names no cause.
        if not gecko_rs_obj.get("assets"):
            gd_platform = get_gd_platform()
            ext = "zip" if "win" in gd_platform else "tar.gz"
            logging.warning(
                "GitHub API returned no geckodriver assets (%s). Falling back to "
                "pinned v%s; test_gecko_version will fail if that is not the "
                "latest release. Set GITHUB_TOKEN to avoid rate limiting.",
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

        if channel == "-devedition":
            # Devedition has special requirements as it's testing a release

            this_devedition = BACKSTOP
            fx_download_dir_url = (
                "https://archive.mozilla.org/pub/devedition/releases/135.0b5/"
            )

            while True:
                (major, _) = this_devedition.split(".")
                major = int(major)
                this_devedition = f"{major + 1}.0b5"
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
            # Anything but devedition

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
            fx_download_dir_url = (
                "https://archive.mozilla.org/pub/firefox/candidates/"
                f"{latest_beta_ver}-candidates/"
            )
            response = requests.get(fx_download_dir_url)
            build = 1
            if response.status_code < 300:
                soup = BeautifulSoup(response.text, "html.parser")
                executable_name = ""
                # Extract the text of each line
                for line in soup.find_all("a"):
                    line_text = line.getText().split(".")
                    if not line_text[0]:
                        continue
                    # Get the executable name
                    build = max(int(line_text[0][-2]), build)
                fx_download_dir_url = (
                    "https://archive.mozilla.org/pub/firefox/candidates/"
                    f"{latest_beta_ver}-candidates/build{build}/{get_fx_platform()}/{language}/"
                )

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
