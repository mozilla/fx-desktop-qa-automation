from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import Schema
from voluptuous import Required

transforms = TransformSequence()


@transforms.add
def apply_config(config, tasks):
    for task in tasks:
        task["description"] = "Collects Fx and Geckodriver"

        env = task.setdefault("worker", {}).setdefault("env", {})

        yield task
