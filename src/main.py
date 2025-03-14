"""EKS automation - main module."""

import base64
import os
import re
import sys

import boto3
from botocore.signers import RequestSigner
from kubernetes import client, config

from src import deployment, loadbalancer, statefulset

AWS_REGION = os.getenv("AWS_REGION")
CLUSTER_NAME = os.getenv("CLUSTER_NAME")


def get_bearer_token():
    """Get STS bearer token."""
    sts_token_expires_in = 60
    session = boto3.session.Session(region_name=AWS_REGION)
    client = session.client("sts")
    service_id = client.meta.service_model.service_id
    signer = RequestSigner(
        service_id, AWS_REGION, "sts", "v4", session.get_credentials(), session.events
    )
    params = {
        "method": "GET",
        "url": f"https://sts.{AWS_REGION}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15",
        "body": {},
        "headers": {"x-k8s-aws-id": CLUSTER_NAME},
        "context": {},
    }
    signed_url = signer.generate_presigned_url(
        params,
        region_name=AWS_REGION,
        expires_in=sts_token_expires_in,
        operation_name="",
    )
    base64_url = base64.urlsafe_b64encode(signed_url.encode("utf-8")).decode("utf-8")
    # remove any base64 encoding padding:
    return "k8s-aws-v1." + re.sub(r"=*", "", base64_url)


def scale_down():
    """Scale eks down."""
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    namespaces = v1.list_namespace().items
    for ns in namespaces:
        namespace = ns.metadata.name
        print(f"Processing namespace: {namespace}")
        deployment.scale_down(apps_v1, namespace)
        statefulset.scale_down(apps_v1, namespace)
        loadbalancer.scale_down(v1, namespace)


def scale_up():
    """Scale eks up."""
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    namespaces = v1.list_namespace().items
    for ns in namespaces:
        namespace = ns.metadata.name
        print(f"Processing namespace: {namespace}")
        deployment.scale_up(apps_v1, namespace)
        statefulset.scale_up(apps_v1, namespace)
        loadbalancer.scale_up(v1, namespace)


def handler(event, context):  # noqa: ARG001
    """Lambda handler."""
    eks = boto3.client("eks", region_name=AWS_REGION)
    cluster_info = eks.describe_cluster(name=CLUSTER_NAME)
    cluster_endpoint = cluster_info["cluster"]["endpoint"]
    cert_authority = cluster_info["cluster"]["certificateAuthority"]["data"]

    kubeconfig = {
        "apiVersion": "v1",
        "clusters": [
            {
                "name": CLUSTER_NAME,
                "cluster": {
                    "certificate-authority-data": cert_authority,
                    "server": cluster_endpoint,
                },
            }
        ],
        "contexts": [
            {"name": "context1", "context": {"cluster": CLUSTER_NAME, "user": "user1"}}
        ],
        "current-context": "context1",
        "kind": "Config",
        "preferences": {},
        "users": [{"name": "user1", "user": {"token": get_bearer_token()}}],
    }
    config.load_kube_config_from_dict(config_dict=kubeconfig)

    scaling_mode = event["scaling_mode"]

    if scaling_mode == "down":
        scale_down()
    elif scaling_mode == "up":
        scale_up()


if __name__ == "__main__":
    scaling_mode = sys.argv[1]
    handler({"scaling_mode": scaling_mode}, {})
