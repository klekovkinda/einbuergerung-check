import json
import os

import boto3
import requests

def handler(event, context):
    owner = "klekovkinda"
    repo = "einbuergerung-check"
    workflow_id = "run-check.yml"

    # Retrieve the GitHub token from AWS Secrets Manager
    secret_arn = os.getenv("GITHUB_TOKEN_SECRET_ARN")
    secrets_client = boto3.client("secretsmanager")
    try:
        secret_value = secrets_client.get_secret_value(SecretId=secret_arn)
        github_token = secret_value["SecretString"]
    except Exception as e:
        print("Error retrieving GitHub token from Secrets Manager:", e)
        return {
            "statusCode": 500,
            "body": "Failed to retrieve GitHub token"
        }

    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "User-Agent": "AWS-Lambda",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }
    payload = {
        "ref": "master"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print("GitHub API Response:", response.text)
        return {
            "statusCode": response.status_code,
            "body": response.text
        }
    except requests.exceptions.RequestException as e:
        print("Error triggering GitHub workflow:", e)
        return {
            "statusCode": 500,
            "body": str(e)
        }
handler(None, None)
