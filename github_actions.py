from pathlib import Path
from typing import Optional
import json

# GPT response
from utils import get_gpt_response

EVENTS_FILE = Path(__file__).parent / "github_events.json"


def get_recent_actions_events(limit: int = 10) -> str:
    """Get recent GitHub Actions events received via webhook.

    Args:
        limit: Maximum number of events to return (default: 10)
    """
    # Read events from file
    if not EVENTS_FILE.exists():
        return json.dumps([])
    with open(EVENTS_FILE, "r") as f:
        events = json.load(f)
    # Return most recent events
    recent = events[-limit:]

    return json.dumps(recent, indent=2)


def get_workflow_status(workflow_name: Optional[str] = None) -> str:
    """Get the current status of GitHub Actions workflows.

    Args:
        workflow_name: Optional specific workflow name to filter by
    """
    # Read events from file
    if not EVENTS_FILE.exists():
        return json.dumps({"message": "No GitHub Actions events received yet"})
    with open(EVENTS_FILE, "r") as f:
        events = json.load(f)
    if not events:
        return json.dumps({"message": "No GitHub Actions events received yet"})
    # Filter for workflow events
    workflow_events = [e for e in events if e.get("workflow_run") is not None]

    if workflow_name:
        workflow_events = [
            e for e in workflow_events if e["workflow_run"].get("name") == workflow_name
        ]
    # Group by workflow and get latest status
    workflows = {}
    for event in workflow_events:
        run = event["workflow_run"]
        name = run["name"]
        if name not in workflows or run["updated_at"] > workflows[name]["updated_at"]:
            workflows[name] = {
                "name": name,
                "status": run["status"],
                "conclusion": run.get("conclusion"),
                "run_number": run["run_number"],
                "updated_at": run["updated_at"],
                "html_url": run["html_url"],
            }

    return json.dumps(list(workflows.values()), indent=2)


def analyze_ci_results(workflow_status: str) -> str:
    """Analyzes the CI results and provides a summary.

    Args:
        workflow_status (str): The status of the workflow.

    Returns:
        str: A summary of the CI results.
    """

    prompt = f"""Analyze recent CI/CD results and provide insights.

    Format your response as:
    ## CI/CD Status Summary
    - **Overall Health**: [Good/Warning/Critical]
    - **Failed Workflows**: [List any failures with links]
    - **Successful Workflows**: [List recent successes]
    - **Recommendations**: [Specific actions to take]
    - **Trends**: [Any patterns you notice]
    
    The CI results are: 
    {workflow_status}"""
    results = get_gpt_response(full_prompt=prompt)

    return results


def create_deployment_summary(ci_results_summary: str) -> str:
    """Creates a deployment summary for team communication.

    Args:
        ci_results_summary (str): A summary of the CI results.

    Returns:
        str: A deployment summary.
    """
    prompt = f"""
        Format as a concise message suitable for Slack based on the below ci results:

        🚀 **Deployment Update**
        - **Status**: [✅ Success / ❌ Failed / ⏳ In Progress]
        - **Environment**: [Production/Staging/Dev]
        - **Version/Commit**: [If available from workflow data]
        - **Duration**: [If available]
        - **Key Changes**: [Brief summary if available]
        - **Issues**: [Any problems encountered]
        - **Next Steps**: [Required actions if failed]
        Keep it brief but informative for team awareness.
        
        The CI results are : {ci_results_summary}"""

    res = get_gpt_response(full_prompt=prompt)

    return res


if __name__ == "__main__":
    pass
