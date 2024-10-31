import json
import os

from cryptography.fernet import Fernet


def get_key():
    return os.environ.get("SVC_ACCT_DECRYPT").encode()


def encrypt(source_file: str, target_file="", overwrite=False) -> str:
    """Encrypt an existing file, place in data/secrets"""
    if not target_file:
        target_file = os.path.splitext(source_file)[0]
    if not source_file.endswith(".json"):
        raise OSError("We only encrypt json files")
    target_loc = os.path.join("data", "secrets", f"{target_file}.json")
    if os.path.exists(target_loc) and not overwrite:
        raise OSError("Cannot overwrite existing file, set overwrite=True to ignore.")

    with open(source_file) as fh:
        secret = json.load(fh)
    token = encrypt_ends(secret)

    with open(target_loc, "w") as fh:
        json.dump(token, fh, indent=2)

    return target_loc


def encrypt_ends(secret: dict) -> dict:
    encrypter = Fernet(get_key())
    encrypts = []
    for key, value in secret.items():
        if isinstance(value, dict):
            encrypts.append((key, encrypt_ends(value)))
        elif isinstance(value, str):
            encrypts.append((key, encrypter.encrypt(value.encode()).decode()))
    for enc in encrypts:
        (key, value) = enc
        if isinstance(value, str):
            secret[key] = "[enc]||" + value
        else:
            secret[key] = value
    return secret


def decrypt(filename: str) -> dict:
    """Decrypt a file from data/secrets, return the secrets"""
    if not filename.endswith(".json"):
        filename = filename + ".json"

    if not os.path.exists(os.path.dirname(filename)):
        filename = os.path.join("data", "secrets", filename)

    if not os.path.exists(filename):
        raise OSError(f"File {filename} does not exist.")

    decrypter = Fernet(get_key())
    with open(filename) as fh:
        token = json.load(fh)

    return decrypt_ends(token)


def decrypt_ends(token: dict) -> dict:
    decrypter = Fernet(get_key())
    decrypts = []
    for key, value in token.items():
        if isinstance(value, dict):
            decrypts.append((key, decrypt_ends(value)))
        elif isinstance(value, str) and value.startswith("[enc]||"):
            secret = value.split("||")[1]
            decrypts.append((key, decrypter.decrypt(secret.encode()).decode()))
    for dec in decrypts:
        (key, value) = dec
        token[key] = value
    return token
