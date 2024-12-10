import json
import os
from asana_client import AsanaClient
from redis_utils import get_value_from_redis
from webhook_utils import handle_webhook_handshake, process_webhook_event


def lambda_handler(event, context):
    ASANA_PERSONAL_KEY = os.getenv("ASANA_PERSONAL_KEY")
    asana_client = AsanaClient(ASANA_PERSONAL_KEY)

    # Make all headers lowercase since AWS turns them into lowercase, but Asana sends them as camelCase
    # This makes sure the code works in both the AWS and the local environment
    headers = {k.lower(): v for k, v in event.get("headers", {}).items()}
    query_params = event.get("queryStringParameters", {})
    body = event.get("body", "")
    x_hook_secret = headers.get("x-hook-secret")
    x_asana_signature = headers.get("x-asana-request-signature")

    counter_key = query_params.get("counter_key")
    prefix = query_params.get("prefix")

    if not counter_key or not prefix:
        return {"statusCode": 400, "body": json.dumps({"message": "Missing counter_key or prefix"})}

    if x_hook_secret:
        return handle_webhook_handshake(prefix, x_hook_secret)

    if x_asana_signature:
        hook_secret = get_value_from_redis(f"{prefix}_hook_secret")
        if not hook_secret or not asana_client.verify_signature(hook_secret, body, x_asana_signature):
            return {"statusCode": 403, "body": json.dumps({"message": "Invalid signature"})}
        try:
            if body:
                process_webhook_event(asana_client, json.loads(body), counter_key, prefix)
            return {"statusCode": 200, "body": json.dumps({"message": "Webhook event processed"})}
        except json.JSONDecodeError:
            return {"statusCode": 400, "body": json.dumps({"message": "Invalid JSON payload"})}

    return {"statusCode": 400, "body": json.dumps({"message": "Invalid request"})}
