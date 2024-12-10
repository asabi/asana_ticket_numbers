import os
import json
import urllib.request


def get_redis_url_and_headers():
    redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
    redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    headers = {"Authorization": f"Bearer {redis_token}"}
    return redis_url, headers


def get_value_from_redis(key):
    redis_url, headers = get_redis_url_and_headers()
    url = f"{redis_url}/get/{key}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode())
        return result.get("result")


def set_value_in_redis(key, value):
    redis_url, headers = get_redis_url_and_headers()
    url = f"{redis_url}/set/{key}/{value}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    urllib.request.urlopen(request)


def increment_redis_key(counter_key):
    redis_url, headers = get_redis_url_and_headers()
    url = f"{redis_url}/incr/{counter_key}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode())
        return result.get("result")
