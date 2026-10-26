from taskgraph.transforms.base import TransformSequence

transforms = TransformSequence()


@transforms.add
def apply_config(config, tasks):
    for task in tasks:
        task["description"] = "Runs smoke test suite"

        env = task.setdefault("worker", {}).setdefault("env", {})
        env["GITHUB_BASE_REF"] = config.params.get("base_ref", "nightly")
        env["GITHUB_HEAD_REF"] = config.params.get("head_git_ref")

        yield task
