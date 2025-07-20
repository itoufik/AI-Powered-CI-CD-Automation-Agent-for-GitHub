import requests
from ci_analyser import get_recent_actions_events, get_workflow_status, analyze_ci_results, create_deployment_summary
from dotenv import load_dotenv
import os
load_dotenv()

def send_slack_sms():
    events = get_recent_actions_events()
    workflow_status = get_workflow_status()
    analysis = analyze_ci_results(workflow_status=workflow_status)
    dep_sum = create_deployment_summary(ci_results_summary=analysis)
    url = os.getenv("SLACK_WEBHOOK_URL")
    payload = {"text": dep_sum}
    response = requests.post(url=url, json=payload, timeout=10)
    return response.status_code

if __name__ == "__main__":
    res = send_slack_sms()
    print(res)