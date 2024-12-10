# Load .env file

from dotenv import load_dotenv
import os
import sys

sys.path.insert(0, os.path.abspath("lambda_src"))
from lambda_src.asana_client import AsanaClient

load_dotenv()

# use the ASANA_PERSONAL_KEY variable to access the Asana API and get personal data about the user

ASANA_PERSONAL_KEY = os.getenv("ASANA_PERSONAL_KEY")
asana_client = AsanaClient(ASANA_PERSONAL_KEY)

try:
    workspaces = asana_client.get_workspaces()
    print("Workspaces:")
    for workspace in workspaces:
        print(f"- {workspace['name']} (ID: {workspace['gid']})")
except Exception as e:
    print(f"An error occurred: {e}")
# Get the list of workspaces using the requests library
