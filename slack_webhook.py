import os
import requests
from dotenv import load_dotenv

from ci_analyser import (
    analyze_ci_results,
    create_deployment_summary,
    get_workflow_status,
)

load_dotenv()


def send_slack_message() -> str:
    """Fetches CI/CD workflow status, generates a summary, and sends it to Slack.

    This function orchestrates the process of:
    1. Retrieving the latest workflow status from GitHub Actions.
    2. Analyzing the status to create a concise summary.
    3. Formatting the summary into a deployment message.
    4. Sending the message to a specified Slack channel via a webhook.

    Returns:
        A string indicating the result of the Slack notification.
    """
    try:
        workflow_status = get_workflow_status()
        analysis = analyze_ci_results(workflow_status=workflow_status)
        deployment_summary = create_deployment_summary(ci_results_summary=analysis)
        
        slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not slack_webhook_url:
            return "❌ SLACK_WEBHOOK_URL environment variable not set."

        payload = {"text": deployment_summary}
        response = requests.post(slack_webhook_url, json=payload, timeout=10)

        if response.status_code == 200:
            return "✅ Message sent successfully to Slack"
        else:
            return f"❌ Failed to send message. Status: {response.status_code}, Response: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"❌ Error sending request to Slack: {e}"
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"


if __name__ == "__main__":
    result = send_slack_message()
    print(result)
