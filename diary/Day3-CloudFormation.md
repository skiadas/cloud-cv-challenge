# Day 3: Using CloudFormation

Today's goal would be to convert the cloudfront distribution setup into a cloudformation template. Trying to follow [this project](https://github.com/aws-samples/amazon-cloudfront-secure-static-site) and replicating it.

Things I will need to achieve with my cloudformation template:

- Create certificate
- Create origin-access-identity
- Create bucket and logs bucket
- Create cloudfront distribution
- Create and attach response header policy
- update route 53 DNS records
- upload to bucket
- ??

I will also need to modify my github actions to carry out the cloudformation template work.

It needs some parameters, I'll need to figure out where to place them: subdomain (`resume` for me), domain name, hosted zone id.

I started copying and understanding the templates. One thing I notice is that it involves a whole complicated lambda function to copy over the files. I would rather rely on the github action already established, so I will remove all the copying bits.

One uncertainty related to that would be how my github workflow knows the name of the bucket. I'll probably need to specify it in both places, via a GitHub environment variable perhaps. I also need to make sure the cloudformation templates are being acted on first. I will probably need to put them in the same workflow somehow.

In order to automatically push the stack I first tried to use a github action provided by AWS. Unfortunately that action can only handle a single template and not its dependencies. I therefore had to follow the directions to first "package" the stack to an S3 bucket and then deploy using that packaging.

One problem I encountered was misnaming a YAML property and also placing it at the wrong level. I'll look for two solutions: An automated step I can add to a github action as well as a VS Code plugin.

I incorporated the cf linter at both levels. Then I spent a lot of time troubleshooting my stack which kept failing to create the certificate. It turns out I forgot to put a $ in front of a parameter. This took quite a long time to identify and fix. One of the challenges was that the certificate stack was being deleted as part of rollback-on-failure. Temporarily disabling that allowed me to get better error messages. I feel there should be a better way however, troubleshooting cloud formation errors feels a bit too random right now.

Now we've got something working. What remains:

- Arrange the tasks in the workflow so that they only run when appropriate: stack-changing tasks only run when the cloud formation templates have changed, while the syncing job only runs when the site folder has changed. DONE!
- Create better error-handling pages (access denied, 404 etc). Pages added.

However now I need to invalidate the cache whenever the site updates. The problem is how to get hold of the ids of the distributions that need to be invalidated. My plan for this right now is as follows:

1. Add the cloudfront distribution id to the CF stack that builds the distribution.
2. Export that id.
3. Query the stack from the command line for its exports.
4. Learn how to use JMES queries to extract the appropriate value.
