import os
import sys

import toml


def dictmerge(a: dict, b: dict) -> dict:
    if a == b:
        return a

    merged = {}
    for key in set(list(a.keys()) + list(b.keys())):
        if isinstance(a.get(key), dict) and isinstance(b.get(key), dict):
            merged[key] = dictmerge(a[key], b[key])
        elif key not in a:
            merged[key] = b[key]
        elif key not in b:
            merged[key] = a[key]
        else:
            merged[key] = a.get(key) + b.get(key)

    return merged


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == "help" or sys.argv[1] == "-h":
        print(
            "Change the pyproject in the repo root. Overwrite pyproject.toml\n"
            "Usage: python scripts/switch_config.py <config_name>"
        )
        sys.exit(1)
    if not os.path.isfile("pyproject.toml"):
        sys.exit(
            "pyproject.toml not found in the current dir. Run this script "
            "from the repo root; it merges the chosen config onto existing "
            "pyproject.toml, so that file must be present."
        )
    with open("pyproject.toml") as f:
        pyproject = toml.loads(f.read())

    config_path = os.path.join("config", f"{sys.argv[1]}_pyproject.toml")

    if not os.path.isfile(config_path):
        sys.exit(f"Config not found at {config_path}")

    with open(config_path) as f:
        config = toml.loads(f.read())

    new_pyproject = dictmerge(pyproject, config)
    toml_text = toml.dumps(new_pyproject)

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
