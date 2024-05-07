from taskgraph.transforms.base import TransformSequence

transforms = TransformSequence()


@transforms.add
def apply_config(config, tasks):
    for task in tasks:
        task["description"] = "Lint and format"

        env = task.setdefault("worker", {}).setdefault("env", {})

        yield task
