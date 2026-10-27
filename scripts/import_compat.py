import os

PACKAGE_ROOT = os.path.join("packages", "auto_fxui", "src", "auto_fxui")
MODULE_ROOT = "modules"

if __name__ == "__main__":
    for root, dirs, files in os.walk(PACKAGE_ROOT):
        for f in files:
            module_name, ext = os.path.splitext(f)
            if ext != ".py":
                continue
            subunit = root.replace(PACKAGE_ROOT, "")
            print(root, f, f"%{subunit}%")
            stub_loc = os.path.join(MODULE_ROOT, f)
            if subunit:
                subunit = subunit[1:]
                stub_loc = os.path.join(MODULE_ROOT, subunit, f)
                module_name = f"{subunit}.{module_name}"
                subunit_loc = os.path.join(MODULE_ROOT, subunit)
                if not os.path.exists(subunit_loc):
                    print(f"Creating {subunit_loc}...")
                    os.mkdir(os.path.join(subunit_loc))
            import_call = f"from auto_fxui.{module_name} import *"
            print(f"Opening {stub_loc}...")
            print(f"Writing '{import_call}'...")
            with open(stub_loc, "w") as fh:
                fh.write(import_call)
