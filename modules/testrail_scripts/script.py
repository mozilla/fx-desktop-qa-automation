if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    from modules.testrail_integration import reportable

    load_dotenv()
    os.environ["TESTRAIL_REPORT"] = "True"
    os.environ["FX_L10N"] = "True"
    os.environ["TESTRAIL_USERNAME"] = "payalew@mozilla.com"
    os.environ["TESTRAIL_API_KEY"] = "1sshvwT1ivoQTO3Ln5KE-TVY6zRc6CS8axCTCAp3P"
    check = reportable()
    print(check)
