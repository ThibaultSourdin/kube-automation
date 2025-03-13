def scale_down(api_instance, namespace: str):
    """Scale down deployments."""

    deployments = api_instance.list_namespaced_deployment(namespace).items
    for deployment in deployments:
        name = deployment.metadata.name
        print(f"Scaling down Deployment: {name} in namespace {namespace}")
        body = {"spec": {"replicas": 0}}
        api_instance.patch_namespaced_deployment_scale(name, namespace, body)


def scale_up(api_instance, namespace: str):
    """Scale up deployments."""

    deployments = api_instance.list_namespaced_deployment(namespace).items
    for deployment in deployments:
        name = deployment.metadata.name
        print(f"Scaling up Deployment: {name} in namespace {namespace}")
        body = {"spec": {"replicas": 1}}
        api_instance.patch_namespaced_deployment_scale(name, namespace, body)
