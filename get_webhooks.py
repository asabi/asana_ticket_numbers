# Load .env file

from dotenv import load_dotenv
import os
import json
import sys

sys.path.insert(0, os.path.abspath("lambda_src"))
from lambda_src.asana_client import AsanaClient

load_dotenv()

# use the ASANA_PERSONAL_KEY variable to access the Asana API and get personal data about the user

ASANA_PERSONAL_KEY = os.getenv("ASANA_PERSONAL_KEY")
ASANA_WORKSPACE_ID = os.getenv("ASANA_WORKSPACE_ID")

asana_client = AsanaClient(ASANA_PERSONAL_KEY)

try:
    # Show the list of projects and let the user select one to get the webhooks using an index
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
    for webhook in webhooks:
        # print json data with indentations
        print(json.dumps(webhook, indent=4))
except Exception as e:
    print(f"An error occurred: {e}")
