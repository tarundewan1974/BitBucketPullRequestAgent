import os
import json
import requests
from openai_copilot.agent import CopilotLLM


class BitbucketClient:
    """Simple Bitbucket API client."""

    def __init__(self, workspace: str, repo_slug: str, token: str):
        self.base_url = "https://api.bitbucket.org/2.0"
        self.workspace = workspace
        self.repo_slug = repo_slug
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_pr_diff(self, pr_id: int) -> str:
        url = (
            f"{self.base_url}/repositories/{self.workspace}/{self.repo_slug}/pullrequests/{pr_id}/diff"
        )
        response = self.session.get(url)
        response.raise_for_status()
        return response.text

    def post_pr_comment(self, pr_id: int, text: str, path: str | None = None, line: int | None = None) -> None:
        url = (
            f"{self.base_url}/repositories/{self.workspace}/{self.repo_slug}/pullrequests/{pr_id}/comments"
        )
        payload = {"content": {"raw": text}}
        if path and line:
            payload["inline"] = {"path": path, "to": line}
        response = self.session.post(url, json=payload)
        response.raise_for_status()


class CopilotPRReviewer:
    """Use CopilotLLM to review PR diffs and comment on issues."""

    def __init__(self, bitbucket: BitbucketClient):
        self.bb = bitbucket
        self.llm = CopilotLLM(verbose=False, model="gpt-4")

    def analyze_diff(self, diff: str) -> list[dict]:
        """Send diff to CopilotLLM and parse JSON response."""
        instructions = (
            "You are an expert code reviewer. Review the following diff and output a JSON list "
            "with objects describing issues. Each object must contain 'file', 'line', and 'comment'.\n" + diff
        )
        result = self.llm.run(instructions)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return []

    def review_pr(self, pr_id: int) -> None:
        diff = self.bb.get_pr_diff(pr_id)
        issues = self.analyze_diff(diff)
        for issue in issues:
            self.bb.post_pr_comment(
                pr_id,
                issue.get("comment", "Issue found"),
                path=issue.get("file"),
                line=issue.get("line"),
            )
        # Mark PR as needing work by adding a general comment
        self.bb.post_pr_comment(pr_id, "Automated review complete: please address the comments.")


def main() -> None:
    workspace = os.environ.get("BITBUCKET_WORKSPACE")
    repo = os.environ.get("BITBUCKET_REPO")
    token = os.environ.get("BITBUCKET_TOKEN")
    pr_id = os.environ.get("PR_ID")
    if not all([workspace, repo, token, pr_id]):
        raise SystemExit("BITBUCKET_WORKSPACE, BITBUCKET_REPO, BITBUCKET_TOKEN and PR_ID are required")
    bb = BitbucketClient(workspace, repo, token)
    reviewer = CopilotPRReviewer(bb)
    reviewer.review_pr(int(pr_id))


if __name__ == "__main__":
    main()
