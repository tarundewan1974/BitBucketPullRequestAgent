require('dotenv').config();
const { Bitbucket } = require('bitbucket');
const { CopilotClient } = require('copilotkit');

const bitbucket = new Bitbucket({
  auth: {
    username: process.env.BITBUCKET_USERNAME,
    password: process.env.BITBUCKET_APP_PASSWORD,
  },
});

const copilot = new CopilotClient({ apiKey: process.env.COPILOT_API_KEY });

async function analyzeDiff(diff) {
  const prompt = `Review the following diff and identify issues:\n${diff}`;
  const result = await copilot.chat(prompt);
  return result.split('\n').filter(Boolean);
}

async function reviewPullRequests() {
  const workspace = process.env.BITBUCKET_WORKSPACE;
  const repoSlug = process.env.BITBUCKET_REPO_SLUG;
  const prs = await bitbucket.pullrequests.list({ workspace, repo_slug: repoSlug, state: 'OPEN' });
  for (const pr of prs.data.values) {
    const diffRes = await bitbucket.pullrequests.getDiff({ workspace, repo_slug: repoSlug, pull_request_id: pr.id });
    const issues = await analyzeDiff(diffRes.data);
    for (const issue of issues) {
      await bitbucket.pullrequests.createComment({
        workspace,
        repo_slug: repoSlug,
        pull_request_id: pr.id,
        _body: { content: { raw: issue } },
      });
    }
    await bitbucket.pullrequests.update({
      workspace,
      repo_slug: repoSlug,
      pull_request_id: pr.id,
      state: 'OPEN',
      title: pr.title,
      description: pr.description,
    });
  }
}

reviewPullRequests().catch(err => {
  console.error(err);
  process.exit(1);
});
