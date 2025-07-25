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
BACKSTOP = "135.0b9"
NUMBER_ONLY = False


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


if "-g" in argv:
    gecko_rs_obj = requests.get(GECKO_API_URL).json()

    # In mac, sometimes this request fails to produce a link
    for _ in range(4):
        if gecko_rs_obj:
            break
        sleep(2)
        gecko_rs_obj = requests.get(GECKO_API_URL).json()

    # If we failed, just dump any old link, maybe update this on new gecko release
    if not gecko_rs_obj.get("assets"):
        gd_platform = get_gd_platform()
        ext = "zip" if "win" in gd_platform else "tar.gz"
        print(
            f"https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-{gd_platform}.{ext}"
        )
        exit()

    urls = [
        a.get("browser_download_url")
        for a in gecko_rs_obj.get("assets")
        if not a.get("browser_download_url").endswith(".asc")
    ]
    gecko_download_url = [u for u in urls if get_gd_platform() in u][0]
    print(gecko_download_url)

else:
    if "-n" in argv:
        NUMBER_ONLY = True
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
            next_candidate = f"https://archive.mozilla.org/pub/devedition/releases/{this_devedition}/"

            rs = requests.get(next_candidate)
            if rs.status_code > 399:
                break

            fx_download_dir_url = next_candidate

        devedition_version = fx_download_dir_url.split("/")[-2]
        fx_download_dir_url = f"{fx_download_dir_url}{get_fx_platform()}/{language}/"

    else:
        # Anything but devedition

        candidate_exists = True
        this_beta = BACKSTOP
        while candidate_exists:
            (major, minor_beta) = this_beta.split(".")
            (minor, beta) = minor_beta.split("b")
            major = int(major)
            minor = int(minor)
            beta = int(beta)

            next_major = f"{major + 1}.0b1"
            fx_download_dir_url = f"https://archive.mozilla.org/pub/firefox/candidates/{next_major}-candidates/"
            rs = requests.get(fx_download_dir_url)
            if rs.status_code < 300:
                latest_beta_ver = next_major
                this_beta = next_major
                continue

            next_minor = f"{major}.{minor + 1}b1"
            fx_download_dir_url = f"https://archive.mozilla.org/pub/firefox/candidates/{next_minor}-candidates/"
            rs = requests.get(fx_download_dir_url)
            if rs.status_code < 300:
                latest_beta_ver = next_minor
                this_beta = next_minor
                continue

            next_beta = f"{major}.{minor}b{beta + 1}"
            fx_download_dir_url = f"https://archive.mozilla.org/pub/firefox/candidates/{next_beta}-candidates/"
            rs = requests.get(fx_download_dir_url)
            if rs.status_code < 300:
                latest_beta_ver = next_beta
                this_beta = next_beta
                continue

            candidate_exists = False

        # Look for the latest build
        fx_download_dir_url = f"https://archive.mozilla.org/pub/firefox/candidates/{latest_beta_ver}-candidates/"
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
            fx_download_dir_url = f"https://archive.mozilla.org/pub/firefox/candidates/{latest_beta_ver}-candidates/build{build}/{get_fx_platform()}/{language}/"

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
    if NUMBER_ONLY:
        if channel == "-devedition":
            print(devedition_version)
        else:
            number_cand = fx_download_dir_url.split("/")[6]
            number = number_cand.split("-")[0]
            print(f"{number}-build{build}")
    else:
        print(fx_download_executable_url)
