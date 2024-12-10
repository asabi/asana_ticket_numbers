# Asana Webhook Handler Lambda

This project provides a Python-based AWS Lambda function for handling Asana webhooks. It manages webhook handshakes, validates requests, and processes events such as task name updates while integrating Redis for managing incremental ticket counters and storing webhook secrets.

The goal was to create a Lambda that is simple to deploy and does not use any external libraries beyond the built in Python libs. That's why for example I did not use the requests module.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Getting Started](#getting-started)
   - [Local Development](#local-development)
   - [AWS Deployment](#aws-deployment)
4. [How Asana Webhooks Work](#how-asana-webhooks-work)
5. [Webhook Creation](#webhook-creation)
6. [Environment Variables](#environment-variables)
7. [About Upstash Redis](#about-upstash-redis)

---

## Overview

This Lambda function is designed to handle Asana webhook events for specific projects. It integrates with Redis to:

- Store and retrieve webhook secrets.
- Manage incremental ticket numbers for tasks.

The Lambda supports:

- **Webhook Handshakes:** Ensures proper registration with Asana.
- **Request Validation:** Verifies requests using HMAC-SHA256 signatures.
- **Event Handling:** Updates task names based on incoming events.
- If a task is already prefixed with the ticket number, it does not change it.

---

## Features

- **AWS Lambda Compatible:** Lightweight and deployable as a Lambda Function.
- **Secure Request Validation:** Ensures only legitimate requests are processed.
- **Integration with Redis:** Manages webhook secrets and ticket counters.
- **Dynamic Configuration:** Works with multiple projects via customizable prefixes.

---

## Getting Started

### Local Development

To run the webhook handler locally for testing purposes:

1. **Clone the Repository**:

   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Set Up a Python Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt # Needed for local development only
   ```

3. **Run the Local Server**: Uses the Python HTTP to simulate the webhook endpoint. Run:

   ```bash
   python local_webhook_handler.py
   ```

4. **Expose Locally Running Service to the Internet**:
   Use a tool like [ngrok](https://ngrok.com/) to expose your local server:

   ```bash
   ngrok http 8080
   ```

   Copy the provided ngrok URL and configure it as the webhook URL in Asana.

5. **Test Webhooks**:

   - Use Asana to send test events to the ngrok URL.
   - Monitor logs to verify events are processed correctly.

### AWS Deployment

#### Option 1: Deploy via AWS Console

1. **Zip the Lambda Function (in the lambda\_src folder)**

   ```bash
   zip -r function.zip .
   ```

2. **Create a Lambda Function**:

   - Log in to the AWS Management Console.
   - Navigate to the Lambda service and create a new function.
   - Choose "Upload a .zip file" and upload `function.zip`.

3. **Set Environment Variables**:
   Configure the following variables in the Lambda environment:

   - `ASANA_PERSONAL_KEY`
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`

4. **Configure a Lambda URL**:

   - Enable the Lambda Function URL for public access.
   - Use the generated URL for the Asana webhook setup.

5. **Test the Function**:
   Trigger the webhook and monitor CloudWatch logs to verify functionality.

#### Option 2: Deploy via AWS CLI

1. **Package the Lambda**:

   ```bash
   zip -r function.zip .
   ```

2. **Create Lambda Function**:

   ```bash
   aws lambda create-function \
       --function-name AsanaWebhookHandler \
       --runtime python3.13 \
       --role <execution_role_arn> \
       --handler lambda_function.lambda_handler \
       --zip-file fileb://function.zip \
       --environment Variables={ASANA_PERSONAL_KEY=<key>,UPSTASH_REDIS_REST_URL=<url>,UPSTASH_REDIS_REST_TOKEN=<token>}
   ```

3. **Update Lambda URL**:
   Create and link the Lambda URL to allow public access.

---

## How Asana Webhooks Work

### Overview

Asana webhooks allow you to receive notifications about changes in specific resources (e.g., tasks, projects). The webhook lifecycle includes:

1. **Creation:** Asana sends a handshake request with a `X-Hook-Secret` header.
2. **Validation:** The server must respond with the same `X-Hook-Secret` to validate the webhook.
3. **Event Delivery:** Asana sends events to the configured URL. Events contain a `X-Asana-Request-Signature` for request validation.

### Setting Up a Webhook in Asana

To create a webhook:

1. Use the `create_webhook` method in the `AsanaClient`:
   ```python
   asana_client.create_webhook(resource_id="<project_id>", target_url="<lambda_url>")
   ```
2. Ensure the Lambda is set up to handle the `X-Hook-Secret` for handshake validation.

---

## Webhook Creation

### Redis Integration

- **Storing Secrets:** Webhook secrets are stored in Redis for secure retrieval.
- **Incremental Counters:** Each task gets a unique ticket number using Redis counters.

#### Example Redis Commands:

- Store a secret:
  ```bash
  redis-cli set <prefix>_hook_secret <secret>
  ```
- Increment a counter:
  ```bash
  redis-cli incr <counter_key>
  ```

### Validating Asana Requests

Requests from Asana are verified using the HMAC-SHA256 signature. The Lambda compares the computed signature with `X-Asana-Request-Signature`.

---

## Environment Variables

Configure the following environment variables for both local and AWS deployments:

| Variable                   | Description                                      |
| -------------------------- | ------------------------------------------------ |
| `ASANA_PERSONAL_KEY`       | Personal Access Token for Asana API.             |
| `UPSTASH_REDIS_REST_URL`   | Redis REST URL for storing secrets and counters. |
| `UPSTASH_REDIS_REST_TOKEN` | Authentication token for Redis REST API.         |

---

## About Upstash Redis

[Upstash Redis](https://upstash.com/) is a serverless Redis service designed for low-latency data storage and retrieval. It is ideal for use cases like storing webhook secrets, counters, and other lightweight data with minimal overhead.

### Why Use Upstash Redis in This Project?

1. **Serverless Architecture**: Upstash Redis is serverless, making it a perfect fit for AWS Lambda, as it scales seamlessly with demand.
2. **Global Distribution**: Ensures low-latency access from AWS Lambda functions running in different regions.
3. **Ease of Integration**: Simple REST API allows easy integration without requiring additional Redis client libraries.
4. While we store the X-Hook-Secret, it does not provide access to Asana beyond verifying the authenticity of requests. The secret has no meaningful context outside its use in validating webhook requests, ensuring that storing it in Upstash Redis remains a secure practice.

### How It Is Used in the Project

1. **Webhook Secret Storage**:

   - The `X-Hook-Secret` sent during the Asana webhook handshake is stored securely in Upstash Redis.
   - This secret is later used to validate webhook requests from Asana.

2. **Ticket Number Increments**:

   - Upstash Redis is used to maintain an incremental counter for ticket numbers.
   - Each task name update receives a unique identifier based on this counter.

3. **Simple REST API Usage**:

   - The Lambda function interacts with Upstash Redis using its REST API for all operations, avoiding the need for additional Redis libraries.

### Example REST API Usage

- **Get a Value**:

  ```bash
  curl -X GET "<UPSTASH_REDIS_REST_URL>/get/<key>" -H "Authorization: Bearer <UPSTASH_REDIS_REST_TOKEN>"
  ```

- **Set a Value**:

  ```bash
  curl -X GET "<UPSTASH_REDIS_REST_URL>/set/<key>/<value>" -H "Authorization: Bearer <UPSTASH_REDIS_REST_TOKEN>"
  ```

- **Increment a Value**:

  ```bash
  curl -X GET "<UPSTASH_REDIS_REST_URL>/incr/<key>" -H "Authorization: Bearer <UPSTASH_REDIS_REST_TOKEN>"
  ```

Upstash Redis simplifies state management, making the webhook handler both efficient and scalable.

