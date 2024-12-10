# Load .env file

from dotenv import load_dotenv
import os
import sys

# Add the lambda_src directory to the system path
sys.path.insert(0, os.path.abspath("lambda_src"))

from lambda_src.asana_client import AsanaClient

load_dotenv()

# use the ASANA_PERSONAL_KEY variable to access the Asana API and get personal data about the user

ASANA_PERSONAL_KEY = os.getenv("ASANA_PERSONAL_KEY")
ASANA_WORKSPACE_ID = os.getenv("ASANA_WORKSPACE_ID")

asana_client = AsanaClient(ASANA_PERSONAL_KEY)

try:
    projects = asana_client.get_projects(ASANA_WORKSPACE_ID)
    print("projects:")
    # Show the list of projects and let the user choose one from a list (by index)
    for index, project in enumerate(projects):
        print(f"{index + 1}. {project['name']} (ID: {project['gid']})")
    # Get the index of the project that the user wants to use
    project_index = int(input("Choose a project: ")) - 1
    # Get the project ID from the selected project
    project_id = projects[project_index]["gid"]
    # Ask for the webhook URL
    webhook_url = input("Enter the webhook URL: ").strip()
    # Ask for the counter key
    prefix = input("Enter the prefix (used to get incremental numbers from a redis DB): ").strip()
    # Ask for the prefix
    webhook = asana_client.create_webhook(
        # ASANA_PROJECT_ID, "https://closely-welcomed-krill.ngrok-free.app?counter_key=PLATFORM&prefix=PLATFORM"
        project_id,
        f"{webhook_url}?counter_key={prefix}&prefix={prefix}",
    )
    print(f"Webhook created: {webhook}")
except Exception as e:
    print(f"An error occurred: {e}")
