import os
import re
import sys

SNAKE_RE = re.compile(r"^[a-z](_[a-z])*[a-z]$")
PASCAL_RE = re.compile(r"^[A-Z][a-zA-Z]*[a-z]$")


def snakify(pascal: str) -> str:
    chars = pascal[0].lower()
    for c in pascal[1:]:
        if c == c.upper():
            chars = chars + f"_{c.lower()}"
        else:
            chars = chars + c
    return chars


def pascalify(snake: str) -> str:
    chars = snake[0].upper()
    up_flag = False
    for c in snake[1:]:
        if up_flag:
            chars = chars + c.upper()
            up_flag = False
        elif c == "_":
            up_flag = True
        else:
            chars = chars + c
    return chars


model_type = None
model_name = None
if len(sys.argv) > 1:
    args = [a.lower() for a in sys.argv]
    if "bom" in args:
        model_type = "bom"
        del sys.argv[args.index("bom")]
    elif "pom" in args:
        model_type = "pom"
        del sys.argv[args.index("pom")]
    print(args)
    if len(sys.argv) > 1:
        if sys.argv[1][0] == sys.argv[1][0].upper():
            model_name = snakify(sys.argv[1])
        else:
            model_name = sys.argv[1]


if __name__ == "__main__":
    while not model_type:
        resp = input("What type of model is this? ")
        resp = resp.strip().lower()
        if resp not in ["pom", "bom"]:
            resp = None
        model_type = resp

    while not model_name:
        resp = input("What is the name of the model? ")
        resp = resp.strip()
        if SNAKE_RE.match(resp):
            model_name = resp
        elif PASCAL_RE.match(resp):
            model_name = snakify(resp)

    model_type_name = "page" if model_type == "pom" else "browser"

    manifest = os.path.join("modules", "data", f"{model_name}.components.json")
    if not os.path.exists(manifest):
        with open(manifest, "w") as fh:
            fh.write("{\n\n}")

    model = os.path.join("modules", f"{model_type_name}_object_{model_name}.py")
    if not os.path.exists(model):
        with open(model, "w") as fh:
            fh.write("from modules.page_base import BasePage\n")
            fh.write(f"\nclass {pascalify(model_name)}(BasePage):")

        generic_model = os.path.join("modules", f"{model_type_name}_object.py")
        with open(generic_model, "a") as fh:
            fh.write(f"\nfrom modules.{model[:-3]} import {pascalify(model_name)}")
