## FxIncidentSmoketests
A Python Selenium based set of tests for emergency incident testing of Firefox.

### Build under test
Get the build to be smoke tested from the [candidates](https://ftp.mozilla.org/pub/firefox/candidates/) directory. Ask 
the RelMan contact for the current Incident what the build versions is. 

The test suite needs to know exactly where the build under test is located. 
Install the build in a Custom directory as follows per Platform:
- Windows:
  - Download the .exe: (as example) /pub/firefox/candidates/121.0.1-candidates/build1/win64/en-US/Firefox Setup 121.0.1.exe
  - Install in:"C:\Program Files\\**_Custom Firefox_**\\"
- macOS: 
  - Download the .dmg: (as example) /pub/firefox/candidates/121.0.1-candidates/build1/mac/en-US/Firefox 121.0.1.dmg
  - Install as: "/Applications/**_Custom Firefox.app_**/ (renamed from the default Firefox.app)
- Linux: 
  - Download the tar file: (as example) /pub/firefox/candidates/121.0.1-candidates/build1/linux-x86_64/en-US/firefox-121.0.1.tar.bz2
  - Install in: "/home/*user*/Desktop/**_Custom Firefox_**/" (*user* = your system username)

Launch the build manually one time to navigate through any system permission dialogs, then exit Firefox.

### Getting set up
- If you don't have Python 3.10 or higher installed, download and install it from the official website
  [Python Downloads](https://www.python.org/downloads/). Make sure to check the option to add Python 
  to the system PATH during installation. For Ubuntu, consider using the
  [Deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) if your version's apt repo
  does not contain a version higher than 3.9.
- Install pip - run `python -m ensurepip`
  confirm: `pip --version`
- Download and install GeckoDriver: 
  - Get the latest version of [GeckoDriver](https://github.com/mozilla/geckodriver/releases) for your Platform.
  - Extract and install it, then ensure that directory is in your PATH
- Get the project from git:
  - On Linux:
    - run: `sudo apt install git`
  - On Windows:
    - run: `choco install git` (have to install chocolatey, if not present)
  - On MacOS:
    - run: `git --version` (likely already installed, follow install prompts if not)
  - In a location of your choice, run: `git clone https://github.com/Tracy-Walker/FxIncidentSmoketests FxSmoketests`
- Use pip to install Pipenv:
  - run: `pip install --user pipenv`. If prompted to add a directory to PATH, please do so. Windows
    users may need to restart their shell.
- Install dependencies: `pipenv install`
- Start virtual environment: `pipenv shell`
  - Ensure pynput is installed
    - run: `pip list` to see if it's in the list
      - if not, run:`python -m pip install pynput`
    - you still may run into problems when running the test suite later. 
      If pynput is not found, ensure the libraries are in your PATH.
- Ensure your system allows the following to run in the virtual env:
  - Firefox (incident build)
  - Terminal

### Run the tests
- CD into the FxSmoketests project directory
- run: `pytest`
- IMPORTANT: On MacOS you may be prompted to allow Terminal to control accessibility settings.
  Allow this. You may need to re-run the tests.
- Test results are displayed inline.

- ### Notable command line options
- --run_headless=True (run the tests in headless mode)
- --fx_edition=option (options are Custom(default), Firefox, Nightly)
- -rA shows print statements in terminal
- --html=report.html (creates an html report file, report.html, in top project directory)

- On Failure:
  - rerun the test suite as above - run: `pytest`
  - or just the failed test; i.e.: `pytest test_amazon.py`
