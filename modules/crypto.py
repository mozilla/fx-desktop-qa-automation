import json
import os

from cryptography.fernet import Fernet

KEY = os.environ.get("SVC_ACCT_DECRYPT").encode()


def encrypt(source_file: str, target_file: str, overwrite=False) -> str:
    """Encrypt an existing file, place in data/secrets"""
    if not source_file.endswith(".json"):
        raise OSError("We only encrypt json files")
    target_loc = os.path.join("data", "secrets", target_file)
    if os.path.exists(target_loc) and not overwrite:
        raise OSError("Cannot overwrite existing file, set overwrite=True to ignore.")

    encrypter = Fernet(KEY)
    with open(source_file) as fh:
        token = encrypter.encrypt(fh.read().encode())

    with open(target_loc, "w") as fh:
        fh.write(token.decode())

    return target_loc


def decrypt(filename: str) -> dict:
    """Decrypt a file from data/secrets, return the secrets"""
    if not os.path.exists(os.path.dirname(filename)):
        filename = os.path.join("data", "secrets", filename)

    if not os.path.exists(filename):
        raise OSError(f"File {filename} does not exist.")

    decrypter = Fernet(KEY)
    with open(filename) as fh:
        token = fh.read().encode()

    return json.loads(decrypter.decrypt(token).decode())
