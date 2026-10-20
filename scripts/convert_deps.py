import os
import re
import sys

IMPORT_RX = re.compile(r"from modules.[^t]")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--local":
        replacer = ""
    else:
        replacer = "auto_fxui"
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            loc = os.path.join(root, f)
            print(loc)
            if not loc.endswith(".py"):
                print("not a script")
                continue
            with open(loc) as fh:
                script = fh.readlines()
            outscript = []
            for line in script:
                if IMPORT_RX.search(line):
                    outscript.append(line.replace("modules", replacer))
                else:
                    outscript.append(line)
            if script != outscript:
                with open(loc, "w") as fh:
                    fh.write("".join(outscript))
