import sys
import boto3
import os
import base64
import re

from botocore.signers import RequestSigner
from kubernetes import client, config
from src import deployment
from src import statefulset
from src import loadbalancer


AWS_REGION = os.getenv("AWS_REGION")
CLUSTER_NAME = os.getenv("CLUSTER_NAME")


def get_bearer_token():
    STS_TOKEN_EXPIRES_IN = 60
    session = boto3.session.Session(region_name=AWS_REGION)
    client = session.client('sts')
    service_id = client.meta.service_model.service_id
    signer = RequestSigner(
        service_id,
        AWS_REGION,
        'sts',
        'v4',
        session.get_credentials(),
        session.events
    )
    params = {
        'method': 'GET',
        'url': 'https://sts.{}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15'.format(AWS_REGION),
        'body': {},
        'headers': {
            'x-k8s-aws-id': CLUSTER_NAME
        },
        'context': {}
    }
    signed_url = signer.generate_presigned_url(
        params,
        region_name=AWS_REGION,
        expires_in=STS_TOKEN_EXPIRES_IN,
        operation_name=''
    )
    base64_url = base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8')
    # remove any base64 encoding padding:
    return 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)


def scale_down():
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
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    namespaces = v1.list_namespace().items
    for ns in namespaces:
        namespace = ns.metadata.name
        print(f"Processing namespace: {namespace}")
        deployment.scale_up(apps_v1, namespace)
        statefulset.scale_up(apps_v1, namespace)
        loadbalancer.scale_up(v1, namespace)


if __name__ == "__main__":

    eks = boto3.client('eks', region_name=AWS_REGION)
    cluster_info = eks.describe_cluster(name=CLUSTER_NAME)
    cluster_endpoint = cluster_info['cluster']['endpoint']
    cert_authority = cluster_info['cluster']['certificateAuthority']['data']
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

    scaling_mode = sys.argv[1]

    if scaling_mode == "down":
        scale_down()
    elif scaling_mode == "up":
        scale_up()
