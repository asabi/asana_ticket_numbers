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

asana_client = AsanaClient(ASANA_PERSONAL_KEY)

try:
    # ticket = asana_client.get_ticket("1208943116446990")
    ticket = asana_client.get_ticket("1208943116446992")
    print("ticket:")
    print(json.dumps(ticket, indent=4))
except Exception as e:
    print(f"An error occurred: {e}")
