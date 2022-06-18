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

I will also need to modify my github actions to carry out the cloudformation templte work.

It needs some parameters, I'll need to figure out where to place them: subdomain (`resume` for me), domain name, hosted zone id.

I started copying and understanding the templates. One thing I notice is that it involves a whole complicated lambda function to copy over the files. I would rather rely on the github action already established, so I will remove all the copying bits.

One uncertainty related to that would be how my github workflow knows the name of the bucket. I'll probably need to specify it in both places, via a GitHub environment variable perhaps. I also need to make sure the cloudformation templates are being acted on first. I will probably need to put them in the same workflow somehow.


