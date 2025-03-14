"""EKS automation - loadbalancer module."""

from kubernetes import client
from kubernetes.client.models.v1_object_meta import V1ObjectMeta


def scale_down(api_instance, namespace):
    """Scale down LoadBalancers."""
    services = api_instance.list_namespaced_service(
        namespace, label_selector="type=loadBalancer"
    ).items
    for service in services:
        name = service.metadata.name
        print(f"Updating Service: {name} in namespace {namespace} to ClusterIP")
        body = {"spec": {"type": "ClusterIP"}}
        api_instance.patch_namespaced_service(name, namespace, body)


def scale_up(api_instance, namespace):
    """Scale up LoadBalancers."""
    services = api_instance.list_namespaced_service(
        namespace, label_selector="type=loadBalancer"
    ).items
    for service in services:
        name = service.metadata.name
        print(f"Recreating Service: {name} in namespace {namespace} with LoadBalancer")

        service_spec = service.spec
        service_spec.type = "LoadBalancer"
        service_spec.cluster_ip = None
        service_spec.cluster_i_ps = None

        service_metadata = V1ObjectMeta(
            annotations=service.metadata.annotations,
            labels=service.metadata.labels,
            name=service.metadata.name,
            namespace=service.metadata.namespace,
        )

        api_instance.delete_namespaced_service(name, namespace)

        service_exists = True
        while service_exists:
            services_list = api_instance.list_namespaced_service(namespace)
            services_list = [
                existing_service.metadata.name
                for existing_service in services_list.items
            ]
            if service.metadata.name not in services_list:
                service_exists = False

        new_service = client.V1Service(metadata=service_metadata, spec=service_spec)
        api_instance.create_namespaced_service(namespace, new_service)
