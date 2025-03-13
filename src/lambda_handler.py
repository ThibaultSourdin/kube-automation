import sys
import boto3
import base64
import os
from src.scale import get_bearer_token, scale_down, scale_up

from kubernetes import client, config


AWS_REGION = os.getenv("AWS_REGION")
CLUSTER_NAME = os.getenv("CLUSTER_NAME")



def handler(event, context):
    eks = boto3.client('eks', region_name=AWS_REGION)
    cluster_info = eks.describe_cluster(name=CLUSTER_NAME)
    cluster_endpoint = cluster_info['cluster']['endpoint']
    cert_authority = cluster_info['cluster']['certificateAuthority']['data']
    with open('/tmp/ca.crt', 'wb') as f:
        f.write(base64.b64decode(cert_authority))

    # configuration = client.Configuration()
    # configuration.api_key['authorization'] = get_bearer_token()
    # configuration.api_key_prefix['authorization'] = 'Bearer'
    # configuration.host = cluster_endpoint
    # configuration.ssl_ca_cert = '/tmp/ca.crt'

    # api_client = client.ApiClient(configuration)

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

    # scaling_mode = sys.argv[1]
    scaling_mode = "down"

    if scaling_mode == "down":
        scale_down()
    elif scaling_mode == "up":
        scale_up()
