# BitBucket Pull Request Copilot Agent

This repository contains a simple example of using the **OpenAI Copilot SDK** to review pull requests on a Bitbucket repository. The `pr_agent.py` script fetches the diff of a pull request, sends it to a Copilot model for analysis, and posts inline comments back to the PR.

## Usage

Create a Python virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install openai-copilot requests langchain-community
```

Set the following environment variables before running the agent:

- `BITBUCKET_WORKSPACE` – your Bitbucket workspace name
- `BITBUCKET_REPO` – repository slug
- `BITBUCKET_TOKEN` – access token with permissions to read diffs and post comments
- `PR_ID` – ID of the pull request to review

Run the reviewer:

```bash
python pr_agent.py
```

The agent will analyze the diff and add comments to the pull request with a recommended change and the rationale behind it, then post a summary asking the author to address the issues.
