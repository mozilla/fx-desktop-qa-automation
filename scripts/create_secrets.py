import os
import sys
from subprocess import call, check_output

from modules import crypto
from modules.util import Utilities


def main():
    u = Utilities()
    temp_file = u.random_string(12) + ".json"
    if check_output(["vim", "--version"]):
        call(["vim", temp_file])
        crypto.encrypt(temp_file, sys.argv[1])
        try:
            os.remove(temp_file)
        except FileNotFoundError:
            print("File was not written.")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main()
    else:
        sys.exit("Usage: python create_secrets file_name")
