import yaml

MANIFEST = "manifests/key.yaml"

if __name__ == "__main__":
    errors = []
    with open(MANIFEST) as fh:
        manifest_info = yaml.safe_load(fh)
    for key in manifest_info:
        for test in manifest_info[key]:
            ptr = manifest_info[key][test]
            trail = [key, test]
            while "result" not in ptr:
                next_level = list(ptr.keys())[0]
                ptr = ptr[next_level]
                trail.append(next_level)
            if ptr["result"] == "unstable" or (
                isinstance(ptr["result"], dict)
                and any(ptr["result"][k] == "unstable" for k in ptr["result"])
            ):
                if "http" not in ptr.get("comment", ""):
                    errors.append(f"{'/'.join(trail)}: marked unstable without link")

    if errors:
        raise ValueError("\n".join(errors))
