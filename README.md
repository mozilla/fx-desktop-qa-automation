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
- If you don't have Python installed, download and install it from the official website
  [Python Downloads](https://www.python.org/downloads/). Make sure to 
  check the option to add Python to the system PATH during installation.
- Install pip - run: `sudo apt install python3-pip -y`
  confirm: `pip --version`
- Install Selenium: `pip install selenium`
- Download and install GeckoDriver: 
  - Get the latest version of [GeckoDriver](https://github.com/mozilla/geckodriver/releases) for your Platform.
  - Extract and install it, then ensure that directory is in your PATH
- Get the project from git:
  - On macOS and Linux:
    - run: `sudo apt install git`
  - For Windows
    - run: `choco install git` (have to install chocolatey, if not present)
  - In a location of your choice, run: `git clone https://github.com/Tracy-Walker/FxIncidentSmoketests FxSmoketests`
- Use pip to install Pipenv:
  - run: `pip install --user pipenv`
- Install virtualenv:
  - run: pip install virtualenv
  - cd to the project folder FxSmoketests
    - On macOS and Linux:
      - run: `virtualenv venv`
      - run: `source venv/bin/activate`
    - On Windows:
      - cd to path\to\your\FxSmoketests\venv\Scripts
      - run: `activate`
  - Then return to top level of the project directory (containing the test scripts)
- Install required packages:
  - run `pip install -r requirements.txt`
  - Ensure pynput is installed
    - run `python -m pip install pynput`
    - run: `pip list` to see if it's in the list
    - you still may run into problems when running the test suite later. 
      If pynput is not found, ensure the libraries are in your PATH.
- Ensure your system allows the following to run in the virtual env:
  - Firefox (incident build)
  - Terminal

### Run the tests
- CD into the FxSmoketests project directory
- run: `python main.py`
- There will be some warnings. Ignore them.
- Test results are displayed inline. ie:
  - Ran 7 tests in 51.361s
    - "OK" (test run passed all tests)
    - or "FAILED (errors=x)
- On Failure:
  - rerun the test suite as above - run: `python main.py`
  - or just the failed test; ie. `python test_Amazon.py`

### On the horizon
I'll rewrite these test in pytest format instead of unittest. 
This will give us the ability to print out a nice report to HTML file.
