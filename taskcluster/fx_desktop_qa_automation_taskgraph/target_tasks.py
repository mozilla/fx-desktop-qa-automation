from taskgraph.target_tasks import register_target_task
from taskgraph.util.taskcluster import find_task_id

@register_target_task("new_beta_qa")
def target_tasks_beta_qa(full_task_graph, parameters, graph_config):
    """Select the set of tasks required for a Beta Smoke + Reporting session."""

    def filter(task, parameters):
        return task.attributes.get("beta-qa", False)

    return [l for l, t in full_task_graph.tasks.items() if filter(t, parameters)]
