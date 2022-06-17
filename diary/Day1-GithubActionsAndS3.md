# Day 1: GitHub Actions and S3

My goal for the first day was to set up an S3 bucket that is automatically synced via a GitHub action when the repository is updated. The first steps were easy enough:

- Create an S3 bucket
- Read up on workflows and GitHub actions
- Create a workflow that simply checks out the repository

Now comes the big part: How to update the S3 bucket based on the checked out repository. I learned a few things at this point:

- The default runners for GitHub actions already include the AWS CLI, which means that we can do the syncing with something like `aws s3 sync --delete ...`. The `--delete` part makes sure it is a true sync, so it would remove any files from S3 that are no longer present/needed.
- In order to execute this command though, we need appropriate credentials. One way to do that is to add the account credentials to GitHub secrets. But this is clearly not the right solution for this, all we need is to be able to assume a temporary role.
- In order to achieve this, I had to first add GitHub as an identity provider in AWS. This would allow the GitHub action to try to assume a role.
- I had to then associate a suitable role to that identity provider, and restrict the trust relationship so that only actions from my particular repository could assume this role.
- Then I set the role to have standard S3 access to my bucket.

One last thing remained, that got me into some debugging trouble for a while. I wanted to make sure the role that would be assumed was not hard-coded into the workflow YAML file. So I decided to put it in a secret. Unfortunately I missed some details about how to use secrets in workflows. There are at least two kinds of secrets:

- Repository level secrets. These can be directly used in a workflow.
- Environment level secrets. These can only be used if the workflow includes the environment in an `environment: ` key. I thought it would be enough that the environment was active on all "branches" but that is not so, environments need to be explicitly included in order to be used.

And after that, I now have my action set up and updating my bucket. Tomorrow, I'll set up the bucket to be a public website, and hopefully set up HTTPS along the way.

Lastly, I want to only activate the s3 update if the `site` folder has changed. I see that I can do that by specifying a path in the `push` trigger.
