from taskgraph.target_tasks import register_target_task
from taskgraph.util.taskcluster import find_task_id


@register_target_task("new_beta_qa")
def target_tasks_beta_qa(full_task_graph, parameters, graph_config):
    """Select the set of tasks required for a Beta Smoke + Reporting session."""

    def filter(task, parameters):
        return task.attributes.get("beta-qa", False)

    return [l for l, t in full_task_graph.tasks.items() if filter(t, parameters)]


@register_target_task("new_beta_func")
def target_tasks_beta_func(full_task_graph, parameters, graph_config):
    """Select the set of tasks required for a Beta Functional + Reporting session."""

    def filter(task, parameters):
        return task.attributes.get("beta-func", False)

    return [l for l, t in full_task_graph.tasks.items() if filter(t, parameters)]


@register_target_task("new_beta_glean")
def target_tasks_beta_glean(full_task_graph, parameters, graph_config):
    """Select the set of tasks required for a Beta Glean + Reporting session."""

    def filter(task, parameters):
        return task.attributes.get("beta-glean", False)

    return [l for l, t in full_task_graph.tasks.items() if filter(t, parameters)]


@register_target_task("new_devedition_qa")
def target_tasks_devedition_qa(full_task_graph, parameters, graph_config):
    """Select the set of tasks required for a DevEdition Smoke + Reporting session."""

    def filter(task, parameters):
        return task.attributes.get("devedition-qa", False)

    return [l for l, t in full_task_graph.tasks.items() if filter(t, parameters)]


@register_target_task("new_rc_qa")
def target_tasks_rc_qa(full_task_graph, parameters, graph_config):
    """Select the set of tasks required for a RC Smoke + Reporting session."""

    def filter(task, parameters):
        return task.attributes.get("rc-qa", False)

    return [l for l, t in full_task_graph.tasks.items() if filter(t, parameters)]


@register_target_task("new_rc_glean")
def target_tasks_rc_glean(full_task_graph, parameters, graph_config):
    """Select the set of tasks required for a RC Glean + Reporting session."""

    def filter(task, parameters):
        return task.attributes.get("rc-glean", False)

    return [l for l, t in full_task_graph.tasks.items() if filter(t, parameters)]
