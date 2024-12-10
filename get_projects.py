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
    projects = asana_client.get_projects(ASANA_WORKSPACE_ID)
    print("projects:")
    for project in projects:
        print(f"- {project['name']} (ID: {project['gid']})")
except Exception as e:
    print(f"An error occurred: {e}")
