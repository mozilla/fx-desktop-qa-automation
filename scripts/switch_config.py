import os
import sys

import toml

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == "help" or sys.argv[1] == "-h":
        print(
            "Change the pyproject in the repo root. Overwrites pyproject.toml\n"
            "Usage: python scripts/switch_config.py <config_name>"
        )
        sys.exit(1)
    if not os.path.isfile("pyproject.toml"):
        sys.exit(
            "pyproject.toml not found in the current directory. Run this script "
            "from the repo root; it merges the chosen config onto the existing "
            "pyproject.toml, so that file must be present."
        )
    with open("pyproject.toml") as f:
        pyproject = toml.loads(f.read())

    config_path = os.path.join("config", f"{sys.argv[1]}_pyproject.toml")

    if not os.path.isfile(config_path):
        sys.exit(f"Config not found at {config_path}")

    with open(config_path) as f:
        config = toml.loads(f.read())

    pyproject |= config
    toml_text = toml.dumps(pyproject)

    # prettify the toml output
    toml_out = ""
    for line in toml_text.split("\n"):
        if len(line) < 80:
            toml_out = toml_out + line + "\n"
            continue
        line_out = line.replace('[ "', '[\n  "')
        line_out = line_out.replace(', "', ',\n  "')
        line_out = line_out.replace(",]", ",\n]")
        toml_out = toml_out + line_out + "\n"

    toml_out = toml_out[:-1]
    with open("pyproject.toml", "w") as fh:
        fh.write(toml_out)
