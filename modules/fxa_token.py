import os

import keyring
import requests
from keyring.errors import KeyringError

# Firefox's own OAuth client and the scopes Smart Window asks for.
CLIENT_ID = "5882386c6d801776"
SCOPE = "https://identity.mozilla.com/apps/smartwindow profile:uid"
OAUTH_TOKEN_URL = "https://oauth.accounts.firefox.com/v1/token"
KEYRING_SERVICE = "starfox-fxa"
KEYRING_USER = "refresh-token"
LOGIN_COMMAND = "uv run python -m scripts.fxa_login"


def saved_refresh_token() -> str | None:
    """Return the refresh token saved in the OS keychain by scripts/fxa_login.py."""
    try:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
    except KeyringError:
        return None


def load_refresh_token() -> str | None:
    """Return the refresh token from MOZ_FXA_REFRESH_TOKEN (CI) or the OS keychain."""
    return os.environ.get("MOZ_FXA_REFRESH_TOKEN") or saved_refresh_token()


def save_refresh_token(token: str):
    keyring.set_password(KEYRING_SERVICE, KEYRING_USER, token)


def delete_refresh_token():
    keyring.delete_password(KEYRING_SERVICE, KEYRING_USER)


def get_access_token() -> str | None:
    """
    Return a prod FxA access token for stage MLPA, or None with no credential.

    MOZ_FXA_BEARER_TOKEN, if set, is used as is; otherwise the saved refresh
    token is swapped for a fresh access token.
    """
    token = os.environ.get("MOZ_FXA_BEARER_TOKEN")
    if token:
        return token
    refresh_token = load_refresh_token()
    if not refresh_token:
        return None
    resp = requests.post(
        OAUTH_TOKEN_URL,
        json={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": refresh_token,
            "scope": SCOPE,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"FxA refused the saved refresh token (HTTP {resp.status_code}). "
            f"Sign in again with: {LOGIN_COMMAND}"
        )
    return resp.json()["access_token"]
