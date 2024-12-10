from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("lambda_src"))
from lambda_src.webhook import lambda_handler

load_dotenv()


class LocalRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP server handler to simulate the Lambda invocation.
    """

    def do_POST(self):
        # Parse the request URL
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)  # Parse query string into a dictionary

        # Parse headers
        headers = {key: self.headers[key] for key in self.headers.keys()}

        # Read the body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        # Construct the simulated Lambda event
        simulated_event = {
            "headers": headers,
            "body": body,
            "queryStringParameters": {k: v[0] for k, v in query_params.items()},  # Flatten values
            "path": parsed_path.path,  # Include the path for additional context
        }
        simulated_context = {}  # Context can remain empty for local testing

        # Call the Lambda handler
        response = lambda_handler(simulated_event, simulated_context)

        # Respond with the Lambda output
        self.send_response(response["statusCode"])
        for header, value in response.get("headers", {}).items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(response["body"].encode("utf-8"))


def run_local_server(port=8080):
    """
    Run a local HTTP server to test the Lambda function.
    """
    server_address = ("", port)
    httpd = HTTPServer(server_address, LocalRequestHandler)
    print(f"Starting local server on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run_local_server()
