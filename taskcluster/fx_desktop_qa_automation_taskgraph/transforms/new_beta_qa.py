from taskgraph.transforms.base import TransformSequence

transforms = TransformSequence()


@transforms.add
def apply_config(config, tasks):
    for task in tasks:
        task["description"] = "Runs smoke test suite against new Beta, reports to TestRail"

        env = task.setdefault("worker", {}).setdefault("env", {})

        yield task
