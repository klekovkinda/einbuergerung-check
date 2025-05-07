import json
import os

import boto3
import requests

def handler(event, context):
    owner = "klekovkinda"
    repo = "einbuergerung-check"
    workflow_id = "run-check.yml"

    parameter_name = os.getenv("GITHUB_TOKEN_PARAMETER_NAME")
    if not parameter_name:
        print("Environment variable GITHUB_TOKEN_PARAMETER_NAME is not set.")
        return {
            "statusCode": 500,
            "body": "Environment variable GITHUB_TOKEN_PARAMETER_NAME is not set."
        }

    ssm_client = boto3.client("ssm")
    try:
        parameter = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        github_token = parameter["Parameter"]["Value"]
    except Exception as e:
        print("Error retrieving GitHub token from Parameter Store:", e)
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
