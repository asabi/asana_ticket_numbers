# Load .env file

from dotenv import load_dotenv
import os
import sys

sys.path.insert(0, os.path.abspath("lambda_src"))
from lambda_src.asana_client import AsanaClient

load_dotenv()

# use the ASANA_PERSONAL_KEY variable to access the Asana API and get personal data about the user

ASANA_PERSONAL_KEY = os.getenv("ASANA_PERSONAL_KEY")
ASANA_WORKSPACE_ID = os.getenv("ASANA_WORKSPACE_ID")

asana_client = AsanaClient(ASANA_PERSONAL_KEY)

try:
    # show the list of projects and let the user select one to get the webhooks
    projects = asana_client.get_projects(ASANA_WORKSPACE_ID)
    print("projects:")
    for index, project in enumerate(projects):
        print(f"{index + 1}. {project['name']} (ID: {project['gid']})")

    if len(projects) == 0:
        print("No projects found.")
        exit()

    project_index = int(input("Enter the index of the project to get webhooks: ").strip())
    asana_project_id = projects[project_index - 1]["gid"]

    webhooks = asana_client.get_webhooks(ASANA_WORKSPACE_ID, asana_project_id)
    print("webhooks:")
    # show the list of webhooks and let the user select one to delete based on the index
    if len(webhooks) == 0:
        print("No webhooks found.")
        exit()

    for index, webhook in enumerate(webhooks):
        print(f"{index + 1}. {webhook['target']} (ID: {webhook['gid']})")

    webhook_index = int(input("Enter the index of the webhook to delete: ").strip())
    webhook_id = webhooks[webhook_index - 1]["gid"]
except Exception as e:
    print(f"An error occurred: {e}")


try:
    success = asana_client.delete_webhook(webhook_id)
    if success:
        print(f"Webhook {webhook_id} was deleted successfully.")
    else:
        print(f"Failed to delete webhook {webhook_id}.")
except Exception as e:
    print(f"An error occurred: {e}")
