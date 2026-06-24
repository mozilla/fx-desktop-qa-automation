import os
import sys

import toml

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == "help" or sys.argv[1] == "-h":
        print(
            "Change the pyproject in the repo root. Overwrites pyproject.toml\n"
            "Usage: python scripts/switch_config.py <config_name>"
        )
    pyproject = toml.loads(open("pyproject.toml").read())
    config_path = os.path.join("config", f"{sys.argv[1]}_pyproject.toml")
    if not os.path.isfile(config_path):
        sys.exit(f"Config not found at {config_path}")
    config = toml.loads(open(config_path).read())
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
