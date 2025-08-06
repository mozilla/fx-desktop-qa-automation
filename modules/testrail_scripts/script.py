import os

from modules.testrail_integration import reportable

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    os.environ["FX_L10N"] = "True"
    os.environ["TESTRAIL_REPORT"] = "True"
    os.environ["TESTRAIL_USERNAME"] = "payalew@mozilla.com"
    check = reportable()
    print(check)
