import subprocess
import json
from pathlib import Path
from utils import get_gpt_response

# PR template directory (shared between starter and solution)
TEMPLATES_DIR = Path(__file__).parent/ "templates"

# Default PR templates
DEFAULT_TEMPLATES = {
    "bug.md": "Bug Fix",
    "feature.md": "Feature",
    "docs.md": "Documentation",
    "refactor.md": "Refactor",
    "test.md": "Test",
    "performance.md": "Performance",
    "security.md": "Security"
}

# Type mapping for PR templates
TYPE_MAPPING = {
    "bug": "bug.md",
    "fix": "bug.md",
    "feature": "feature.md",
    "enhancement": "feature.md",
    "docs": "docs.md",
    "documentation": "docs.md",
    "refactor": "refactor.md",
    "cleanup": "refactor.md",
    "test": "test.md",
    "testing": "test.md",
    "performance": "performance.md",
    "optimization": "performance.md",
    "security": "security.md"
}

def analyze_file_changes(base_branch: str = "master", include_diff: bool = True, max_diff_lines: int = 500,) -> str:
    """Get the full diff and list of changed files in the current git repository.
    
    Args:
        base_branch: Base branch to compare against (default: origin)
        include_diff: Include the full diff content (default: true)
        max_diff_lines: Maximum number of diff lines to include (default: 500)
    """
    cwd = str(Path(__file__).parent) # current directory
    print(f"Working on dir : {cwd}")
    # Get list of changed files
    files_result = subprocess.run(
        ["git", "diff", "--name-status", f"{base_branch}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
        cwd=cwd
    )
    
    # Get diff statistics
    stat_result = subprocess.run(
        ["git", "diff", "--stat", f"{base_branch}...HEAD"],
        capture_output=True,
        text=True,
        cwd=cwd
    )

    # Get the actual diff if requested
    diff_content = ""
    truncated = False
    if include_diff:
        diff_result = subprocess.run(
            ["git", "diff", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            cwd=cwd
        )
        diff_lines = diff_result.stdout.split('\n')
                    
        # Check if we need to truncate
        if len(diff_lines) > max_diff_lines:
            diff_content = '\n'.join(diff_lines[:max_diff_lines])
            diff_content += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
            diff_content += "\n... Use max_diff_lines parameter to see more ..."
            truncated = True
        else:
            diff_content = diff_result.stdout

    # Get commit messages for context
    commits_result = subprocess.run(
        ["git", "log", "--oneline", f"{base_branch}..HEAD"],
        capture_output=True,
        text=True,
        cwd=cwd
    )
    
    analysis = {
        "base_branch": base_branch,
        "files_changed": files_result.stdout,
        "statistics": stat_result.stdout,
        "commits": commits_result.stdout,
        "diff": diff_content if include_diff else "Diff not included (set include_diff=true to see full diff)",
        "truncated": truncated,
        "total_diff_lines": len(diff_lines) if include_diff else 0,
    }
    
    return json.dumps(analysis, indent=2)

def get_pr_templates() -> str:
    """List available PR templates with their content."""
    templates = [
        {
            "filename": filename,
            "type": template_type,
            "content": (TEMPLATES_DIR / filename).read_text()
        }
        for filename, template_type in DEFAULT_TEMPLATES.items()
    ]
    
    return json.dumps(templates, indent=2)

def summerize_change(git_changes:str): #04/07
    """Summerize the changes made in Git repo using GPT-4
    
    Args:
        git_changes: Chnages made in the PR
    """
    prompt = f"""
    You are a code summarization assistant. I will provide you with Git changes in a repository. Summarize the changes in clear and concise bullet points for a human reader. Focus on:

    Which files were added, modified, or deleted

    A high-level description of the code changes (based on the diff)

    Commit messages if available

    Lines changed (insertions/deletions)

    Git changes are {git_changes}
    """
    res = get_gpt_response(full_prompt=prompt)

    return res


def suggest_change_type(git_changes_summary:str): #04/07
    """Suggest change based on the git change summary.
    
    Args:
        git_changes_summary: summary of the git change
    """
    prompt = f"""
    You will be given summary of changes made in the Git. You need to choose a template for the summary from the below list of options:
    [bug, fix, feature, enhancement, docs, documentation, refactor, cleanup, test, testing, performance, optimization, security]
    Strictly choose one of the above options.

    git change summary is {git_changes_summary}"""

    res = get_gpt_response(full_prompt=prompt)

    return res

def suggest_template(changes_summary: str, change_type: str) -> str:
    """Let GPT analyze the changes and suggest the most appropriate PR template.
    
    Args:
        changes_summary: Analysis of what the changes do
        change_type: The type of change you've identified (bug, feature, docs, refactor, test, etc.)
    """
    
    # Get available templates
    templates_response = get_pr_templates()
    templates = json.loads(templates_response)
    
    # Find matching template
    template_file = TYPE_MAPPING.get(change_type.lower(), "feature.md")
    selected_template = next(
        (t for t in templates if t["filename"] == template_file),
        templates[0]  # Default to first template if no match
    )
    
    suggestion = {
        "recommended_template": selected_template,
        "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
        "template_content": selected_template["content"]
    }
    
    return json.dumps(suggestion, indent=2)

def fill_template(
    change_type: str,
    git_changes_summary: str,
    templates_dir: str = "templates") -> str:
    """
    Load a template file for the given change_type and fill it using an LLM.
    Args:
        change_type: one of ["bug", "fix", "feature", …] matching a file
                     templates/{change_type}.md
        git_changes_summary: the text summary to be injected into the template
        templates_dir: path to the folder containing all your .md templates
    Returns:
        The filled out template as returned by the LLM.
    """
    template_path = Path(templates_dir) / f"{change_type.lower()}.md" # build the path to the template
    if not template_path.is_file(): # Fallback, if not found
        template_path = Path(templates_dir) / "feature.md"
    template_content = template_path.read_text(encoding="utf-8").strip() # read the raw template
    # craft the prompt for the LLM
    prompt = f"""
    You are given a Markdown template and a Git changes summary.
    Your job is to fill in the template with the details from the summary.

    --- TEMPLATE START ---
    {template_content}
    --- TEMPLATE END ---

    Git changes summary:
    {git_changes_summary}

    Please output the fully‐populated Markdown."""

    # call your LLM wrapper
    filled_md = get_gpt_response(prompt)

    return filled_md

if __name__ =="__main__":
    all_change = analyze_file_changes()
    change_summary = summerize_change(all_change)
    change_type = suggest_change_type(change_summary)
    template = suggest_template(changes_summary=change_summary, change_type=change_type)
    filled_template = fill_template(change_type=change_type, git_changes_summary=change_summary)
    print(filled_template)
