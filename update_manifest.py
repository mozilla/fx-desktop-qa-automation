import json

from manifests.testkey import TestKey

if __name__ == "__main__":
    manifest = TestKey("manifests/key.yaml")
    with open("automated_test_overlap/responses.json") as fh:
        responses = json.load(fh)
    for test, resp in responses.items():
        print(test, resp)
        if resp == "Agree":
            try:
                entry = manifest.get_entry_from_filename(test)
            except KeyError:
                print(f"could not find {test}")
                continue
            ptr = entry
            trail = []
            i = 0
            for _ in range(5):
                if "result" in ptr:
                    break
                step = list(ptr.keys())[0]
                trail.append(step)
                ptr = ptr[step]
                i += 1
            else:
                raise ValueError("No result field in entry")
            if i == 2:
                (suite, test) = trail
                manifest.manifest[suite][test]["result"] = "covered-in-tree"
                print(manifest.manifest[suite][test])
            elif i == 3:
                (suite, test, subtest) = trail
                manifest.manifest[suite][test][subtest]["result"] = "covered-in-tree"
            else:
                raise ValueError("incorrect entry depth")
    manifest.write()
