# BitBucket Pull Request Copilot Agent

This repository contains a simple example of using the **OpenAI Copilot SDK** to review pull requests on a Bitbucket repository. The `pr_agent.py` script fetches the diff of a pull request, sends it to a Copilot model for analysis, and posts inline comments back to the PR.

## Usage

Create a Python virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
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

---

## Vendor Release Document Ingestion

A new module under `release_analysis/ingestion.py` provides basic document ingestion and parsing capabilities. It watches a folder for new PDF or Word documents, extracts their text, and segments the content into change entries using spaCy.

### Running the watcher

```bash
python -m release_analysis.ingestion /path/to/watch
```

Each time a new `.pdf` or `.docx` file is created in the specified folder, the script prints the detected changes to the console. Ensure the spaCy English model is installed via:

```bash
python -m spacy download en_core_web_sm
```

This forms the foundation for further automation such as classification, semantic mapping, and UI integration.

### Java Microservice

A Spring Boot service with equivalent folder watching logic exists under `java_ingestion_service`. Build it using Maven and supply a folder path when running the jar.
