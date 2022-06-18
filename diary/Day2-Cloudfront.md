# Day 2: Deploying via Cloudfront

Today I will get my site public. Later I'll automate the deployed infrastructure.

Basing this on [Amazon's tutorial](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/getting-started-secure-static-website-cloudformation-template.html) and their [provided code](https://github.com/aws-samples/amazon-cloudfront-secure-static-site).

Cloudfront is Amazon's CDN, allowing us to offer our static content fast from AWS Edge locations. CloudFormation will let us automate the process of provisioning and configuring the required resources. We'll also use a [Lambda@Edge function to add secure headers](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-response-headers-policies.html#understanding-response-headers-policies-security). I'll need to understand this more. Update: turns out that we can directly add response headers now, no need for a lambda function.

Reading: [Mozilla web security guidelines](https://infosec.mozilla.org/guidelines/web_security)

First part was to set up a cloudfront distribution. That was OK, and I have my site on a cloudfront url. Now I need to set it up to use my own domain.

The first step in that is to request a certificate from the AWS certificate manager. Then I had to provide my domain name and certificate to the cloudfront distribution. I also had to create some new records in route 53, I thought that cloudfront would have taken care of that. I also had to wait for a few minutes, but finally it is all set!

In order for my bucket to not be publicly available, I created an access identity user that cloudfront could use to obtain access.

Lastly, I created a new response header policy and added it to the distribution. I wanted add CSP so the managed policies weren't sufficient.

Next up, I'll transfer this setup to use cloudformation templates.
