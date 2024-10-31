def test_secrets(use_secrets):
    login = use_secrets("gmail", "primary")
    assert login.get("username") == "mozilla.testacount@gmail.com"
