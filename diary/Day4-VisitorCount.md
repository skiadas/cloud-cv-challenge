# Day 4 Visitor Count

In this session I will work on implementing a visitor count. I would like to actually record the IP addresses of the visitors, in addition to the counts, and maybe even record the "paths" that were accessed. Seems I'm going to need the following:

- Some (Python) Lambda function that reacts to Cloudfront hits and stores the relevant information. I'll need to figure out where I can grab those from.
- Another Python Lambda function that returns count info.
- Two (three?) tables to record the IP addresses and frequencies of the visits, and the frequencies of the different paths that are requested.
- API interfaces for these lambda function
- Some Javascript on my webpage to send a request for the counts.
- A SAM template to automate it all
- Integrating this all into the GitHub action that updates the site.

I'm going to start by learning about [SAM](https://docs.aws.amazon.com/serverless-application-model/index.html). So far it seems I'm going to need the following resources:

- [AWS::Serverless::Function](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-function.html) for the Lambda
- [AWS::Serverless::SimpleTable](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-simpletable.html) to make some DynamoDB tables
- Some sort of API. It seems I have a choice between [AWS::Serverless::Api](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-api.html) and [AWS::Serverless::HttpApi](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-httpapi.html). The Api appears to be "richer" and accordingly more expensive. It can be edge-optimized while HttpApi can't, and has more security and authorization options (e.g. WAF), API keys and per-client rate limiting, and also allows X-Ray tracing. Sounds like it will be worth it in terms of learning some of this stuff. Here's a more complete [Api-HttpApi comparison](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html).
  - It also appears that the function sets up the API itself, so I may not need anything extra.
- I should keep an eye out for uses of [Intrinsic Functions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html)
- There are some [predefined pseudo-parameters](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/pseudo-parameter-reference.html) I can refer to.
- I can [reference](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification-generated-resources.html) the corresponding CF resources that are created, although I am not sure yet if I need to.
- At some point I will need to figure out how to "protect" my API so that only my web-pages' javascript can call on it.

I think I will follow these steps, in terms of building the SAM:

1. Have a SAM application that builds a DynamoDb table.
2. Link that application to my main stack.
3. Add a SAM function that updates the table.
4. Hook that function up as a Lambda@Edge for my cloudfront distribution, to trigger when my distribution receives a request.
5. Add a SAM function that queries the table.
6. Set up an API for that querying function, probably under my resume domain under `/api/counters` or something like that. I will need to learn how to send some paths to one place and other paths to another place, so that I can keep serving the S3 bucket contents.
7. Add Javascript to my webpage that queries this API.
8. After this is working, I will work on creating more tables.

Let's get started.
