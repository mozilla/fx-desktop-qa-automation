import os
import platform


def run_headless():
    # Swap comment for lines below to run in headless mode
    headless = False
    # headless = True
    return headless


def app_location():
    # Get the platform this is running on
    sys_platform = platform.system()

    # Comment out unwanted build versions and save the change before running tests
    # version = 'Firefox'
    # version = 'Nightly'
    version = 'Custom'

    # Path to build location.  Use Custom by installing your incident build to the coinciding path.
    location = ""
    if sys_platform == 'Windows':
        if version == 'Firefox':
            location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
        elif version == 'Nightly':
            location = "C:\\Program Files\\Nightly Firefox\\firefox.exe"
        elif version == 'Custom':
            location = "C:\\Program Files\\Custom Firefox\\firefox.exe"
    elif sys_platform == 'Darwin':
        if version == 'Firefox':
            location = "/Applications/Firefox.app/Contents/MacOS/firefox"
        elif version == 'Nightly':
            location = "/Applications/Nightly Firefox.app/Contents/MacOS/firefox"
        elif version == 'Custom':
            location = "/Applications/Custom Firefox.app/Contents/MacOS/firefox"
    elif sys_platform == 'Linux':
        user = os.environ.get('USER')
        if version == 'Firefox':
            location = "/home/" + user + "/Desktop/Firefox/firefox"
        elif version == 'Nightly':
            location = "/home/" + user + "/Desktop/Nightly Firefox/firefox"
        elif version == 'Custom':
            location = "/home/" + user + "/Desktop/Custom Firefox/firefox"

    return location
