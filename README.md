# BitBucket Pull Request Copilot Agent

This project defines a simple agent using the Copilot SDK. The agent connects to Bitbucket, checks all open pull requests and uses Copilot to review their diffs. Any issues identified by Copilot are posted back to the pull request as individual comments and the pull request is returned to the author for further work.

## Setup

1. Install dependencies
   ```bash
   npm install
   ```
2. Create a `.env` file with your credentials:
   ```env
   BITBUCKET_USERNAME=your_username
   BITBUCKET_APP_PASSWORD=your_password
   BITBUCKET_WORKSPACE=your_workspace
   BITBUCKET_REPO_SLUG=your_repo
   COPILOT_API_KEY=your_copilot_key
   ```
3. Start the agent
   ```bash
   npm start
   ```
