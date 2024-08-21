"""Get the link to download Fx or Geckodriver, for any supported platform.
Use -g to get geckodriver, otherwise you will get Fx.
Set env var FX_CHANNEL to get non-beta, blank string for Release.
Set env var FX_LOCALE to get a different locale build."""

from os import environ
from platform import uname
from sys import argv, exit
from time import sleep

import requests

GECKO_API_URL = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"


def get_fx_platform():
    u = uname()
    if u.system == "Darwin":
        return "osx"
    if u.system == "Linux":
        if "64" in u.machine:
            return "linux64"
        return "linux"
    if u.system == "Windows":
        if u.machine == "AMD64" and not environ.get("GITHUB_ACTIONS"):
            return "win64-aarch64"
        if "64" in u.machine:
            return "win64"
        return "win"


def get_gd_platform():
    u = uname()
    if u.system == "Darwin":
        return "macos"
    if u.system == "Linux":
        if u.machine == "AMD64":
            return "linux-aarch64"
        if "64" in u.machine:
            return "linux64"
        return "linux32"
    if u.system == "Windows":
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
            f"https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-{gd_platform}.{ext}"
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

    fx_download_url = f"https://download.mozilla.org/?product=firefox{channel}-latest-ssl&os={get_fx_platform()}&lang={language}"
    print(fx_download_url)
