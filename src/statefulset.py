"""EKS automation - statefulset module."""


def scale_down(api_instance, namespace: str):
    """Scale down statefulsets."""
    statefulsets = api_instance.list_namespaced_stateful_set(namespace).items
    for statefulset in statefulsets:
        name = statefulset.metadata.name
        print(f"Scaling down StatefulSet: {name} in namespace {namespace}")
        body = {"spec": {"replicas": 0}}
        api_instance.patch_namespaced_stateful_set_scale(name, namespace, body)


def scale_up(api_instance, namespace: str):
    """Scale up statefulsets."""
    statefulsets = api_instance.list_namespaced_stateful_set(namespace).items
    for statefulset in statefulsets:
        name = statefulset.metadata.name
        print(f"Scaling up StatefulSet: {name} in namespace {namespace}")
        body = {"spec": {"replicas": 1}}
        api_instance.patch_namespaced_stateful_set_scale(name, namespace, body)
