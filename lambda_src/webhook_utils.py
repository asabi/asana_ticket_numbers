import json
from redis_utils import get_value_from_redis, set_value_in_redis, increment_redis_key


def handle_webhook_handshake(prefix, x_hook_secret):
    set_value_in_redis(f"{prefix}_hook_secret", x_hook_secret)
    return {
        "statusCode": 200,
        "headers": {"X-Hook-Secret": x_hook_secret},
        "body": json.dumps({"message": "Webhook handshake successful"}),
    }


def process_webhook_event(asana_client, event_payload, counter_key, prefix):
    events = event_payload.get("events", [])
    for event in events:
        resource = event.get("resource", {})
        change = event.get("change", {})
        if resource.get("resource_type") == "task" and change.get("field") == "name":
            task_gid = resource.get("gid")
            task_info = asana_client.get_ticket(task_gid)
            if not task_info:
                print(f"Failed to retrieve task {task_gid}.")
                continue

            current_name = task_info.get("name", "")
            if f"{prefix}-" in current_name:
                print(f"Task {task_gid} name already updated.")
                continue

            ticket_number = increment_redis_key(counter_key)
            new_name = f"{prefix}-{ticket_number}: {current_name}"
            print(f"Updating task {task_gid} name to: {new_name}")

            updates = {"data": {"name": new_name}}
            updated_task = asana_client.update_task(task_gid, updates)
            if updated_task:
                print(f"Task {task_gid} updated successfully.")
            else:
                print(f"Failed to update task {task_gid}.")
