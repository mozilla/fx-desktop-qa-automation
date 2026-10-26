"""Sign in to your prod Mozilla account once, so Smart Window chat tests can record."""

import argparse
import getpass
import os
import sys

import requests
from fxa.core import Client
from fxa.errors import ClientError

from modules.fxa_token import (
    CLIENT_ID,
    LOGIN_COMMAND,
    SCOPE,
    delete_refresh_token,
    load_refresh_token,
    save_refresh_token,
)

FXA_API_URL = "https://api.accounts.firefox.com"
REQUEST_BLOCKED = 125


def login():
    """Sign in, get a refresh token for Smart Window, save it and end the session."""
    # v1 on purpose: PyFxA's v2 login upgrades the account by changing its password.
    client = Client(FXA_API_URL, key_stretch_version=1)
    # PyFxA sends CI_WAF_TOKEN, the stage token, by itself.
    client.apiclient.headers.pop("fxa-ci", None)
    waf_token = os.environ.get("CI_WAF_TOKEN_PROD")
    if waf_token:
        client.apiclient.headers["fxa-ci"] = waf_token

    email = input("Mozilla account email: ").strip()
    password = getpass.getpass("Password (not saved): ")
    try:
        session = client.login(email, password, verification_method="email-otp")
    except ClientError as e:
        if e.errno != REQUEST_BLOCKED:
            raise
        client.send_unblock_code(email)
        code = input("FxA blocked the sign-in. Unblock code from your email: ")
        session = client.login(
            email, password, unblock_code=code.strip(), verification_method="email-otp"
        )
    del password

    if not session.verified:
        if session.verificationMethod == "totp-2fa":
            session.totp_verify(input("Code from your authenticator app: ").strip())
        else:
            code = input("Code we emailed you: ").strip()
            session.apiclient.post(
                "/session/verify_code", {"code": code}, auth=session._auth
            )

    try:
        resp = session.apiclient.post(
            "/oauth/token",
            {
                "grant_type": "fxa-credentials",
                "client_id": CLIENT_ID,
                "scope": SCOPE,
                "access_type": "offline",
            },
            auth=session._auth,
        )
        save_refresh_token(resp["refresh_token"])
    finally:
        # The refresh token outlives the session, so nothing else needs it.
        session.destroy_session()
    print("Signed in. Recording and live runs now get their own tokens.")


def logout():
    """Revoke the saved refresh token and remove it from the keychain."""
    token = load_refresh_token()
    if not token:
        print("No saved sign-in.")
        return
    requests.post(
        f"{FXA_API_URL}/v1/oauth/destroy",
        json={"client_id": CLIENT_ID, "token": token},
        timeout=30,
    ).raise_for_status()
    delete_refresh_token()
    print("Signed out.")


def check():
    """Say whether a sign-in is saved. Never fails."""
    if os.environ.get("MOZ_FXA_BEARER_TOKEN"):
        print("Recording uses the token in MOZ_FXA_BEARER_TOKEN.")
    elif load_refresh_token():
        print("Signed in. Recording and live runs get their own tokens.")
    else:
        print(f"To record Smart Window chat tests, sign in once with: {LOGIN_COMMAND}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help=check.__doc__)
    group.add_argument("--logout", action="store_true", help=logout.__doc__)
    args = parser.parse_args()
    if args.check:
        check()
    elif args.logout:
        logout()
    else:
        try:
            login()
        except ClientError as e:
            sys.exit(f"Sign-in failed: {e}")
