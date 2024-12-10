import json
from urllib import request, parse, error
import hmac
import hashlib


class AsanaClient:
    def __init__(self, personal_access_token):
        """
        Initialize the AsanaClient with the personal access token.
        """
        self.base_url = "https://app.asana.com/api/1.0"
        self.headers = {
            "Authorization": f"Bearer {personal_access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _make_request(self, method, endpoint, data=None, params=None):
        """
        Internal method to make HTTP requests using urllib.
        """
        url = self.base_url + endpoint

        if params:
            url += "?" + parse.urlencode(params)

        data_bytes = None
        if data is not None:
            data_bytes = json.dumps(data).encode("utf-8")

        req = request.Request(url, data=data_bytes, method=method)
        for key, value in self.headers.items():
            req.add_header(key, value)

        try:
            with request.urlopen(req) as response:
                response_data = response.read()
                return json.loads(response_data.decode("utf-8"))
        except error.HTTPError as e:
            error_message = e.read().decode("utf-8")
            raise Exception(f"HTTPError: {e.code} - {error_message}")
        except error.URLError as e:
            raise Exception(f"URLError: {e.reason}")

    def verify_signature(self, secret, body, signature):
        computed_signature = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed_signature, signature)

    def get(self, endpoint, params=None):
        """
        Perform a GET request to the Asana API.
        """
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint, data=None):
        """
        Perform a POST request to the Asana API.
        """
        return self._make_request("POST", endpoint, data=data)

    def put(self, endpoint, data=None):
        """
        Perform a PUT request to the Asana API.
        """
        return self._make_request("PUT", endpoint, data=data)

    def delete(self, endpoint):
        """
        Perform a DELETE request to the Asana API.
        """
        return self._make_request("DELETE", endpoint)

    # Example API calls

    def get_workspaces(self):
        """
        Get the list of workspaces.
        """
        endpoint = "/workspaces"
        return self.get(endpoint).get("data", [])

    def get_projects(self, workspace_id):
        """
        Get the list of projects for a given workspace ID.
        """
        endpoint = "/projects"
        params = {"workspace": workspace_id}
        return self.get(endpoint, params=params).get("data", [])

    def create_webhook(self, resource_id, target_url):
        """
        Create a webhook for a given resource.
        """
        endpoint = "/webhooks"
        data = {"data": {"resource": resource_id, "target": target_url}}
        return self.post(endpoint, data=data).get("data", {})

    def delete_webhook(self, webhook_id):
        """
        Delete a webhook by its ID.
        """
        endpoint = f"/webhooks/{webhook_id}"
        status = self.delete(endpoint).get("data")
        return status == {}

    def get_webhooks(self, workspace_id, resource_id):
        """
        Get the list of webhooks for a specific resource (e.g., workspace, project).
        """
        endpoint = "/webhooks"
        params = {"resource": resource_id, "workspace": workspace_id}
        data = self.get(endpoint, params=params)
        return data.get("data", [])

    def get_ticket(self, ticket_gid):
        """
        Get a specific ticket by its GID.
        """
        endpoint = f"/tasks/{ticket_gid}"
        return self.get(endpoint).get("data", {})

    def update_task(self, task_gid, updates):
        """
        Update a specific task in Asana.
        """
        endpoint = f"/tasks/{task_gid}"
        return self.put(endpoint, data=updates).get("data", {})
