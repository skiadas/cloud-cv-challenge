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

Let's get started. My first attempt at building a DynamoDb table failed because I had not given the GitHub action role the required permissions. With that out of the way, and the application already linked to my main stack, the next order of business is writing a function that updates the table.

I want to use Python and boto3 for this, and to be able to test it locally. I start with locating an appropriate [cloudfront lambda@edge event template](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-event-structure.html). I'm going to put all the relevant code in an `app` folder, so I'll make a `tests` folder there. Looking at the template it appears the main thing I care about is the uri.

Now, I'm thinking I don't want this function to talk directly to the database, I want it to simply send the request to SQS, then have another function that processes that SQS message. I will start by creating this queue service, and then adding the two functions on its either side.

Creating the queue service was fairly easy, again once I gave my script the requisite permissions. I then created a lambda function, which is not doing much for now but it allowed me to work out the permissions for creating lambda functions.

The biggest challenge right now I feel will be the testing. I would love to have some local testing capabilities, but my functions fundamentally interact with the AWS ecosystem, and there's no reasonable way to duplicate all that locally. The suggestion from AWS appears to be to effectively do the testing on actual "live" cloud resources, with something they call [AWS Accelerate](https://aws.amazon.com/blogs/compute/accelerating-serverless-development-with-aws-sam-accelerate/?sc_icampaign=launch_sam-accelerate&sc_ichannel=ha&sc_icontent=awssm-9887_launch&sc_iplace=ribbon&trk=ha_awssm-9887_launch), currently in [public preview](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/accelerate-getting-started.html). As I understand it, this effectively sets up a quick way to update a stack as you iterate on your application, which is a good start point, it can be the beginning of a more automated process. I will try to set up a test infrastructure that roughly does the following:

- Starts the sam sync on a new test stack, that only contains my "counters" stuff.
- Run Python test files.
- Tear down the stack.

There will ultimately be three functions to test:

- A function that takes in a cloudfront visitor event and adds an event to a SQS queue. I will be able to provide it with custom visitor events, and I want to see if a message went to the queue.
- A function that processes messages from the queue and adds/updates entries in a dynamodb database. Sounds like I will need a separate database for these tests.
- A function that is triggered at an API and returns suitable counter info from the database. Again I will need to use the database.

I could probably mock some of these resources. And if my functions were doing any amount of serious work I would do so. But as it stands, it's all integration work and needs to be tested as a whole. So I will work on some integration testing by using a cloud-deployed test stack. I will avoid the cloudfront deployment part though.

### Debugging SAM applications

[Main article](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-test-and-debug.html)

We can invoke a lambda function locally via `sam local invoke "name" -e event.json`. I further need `--template ...` because my SAM yaml is in a different location. I eventually was able to get that working, but the main challenge I faced was that local invocations of functions don't inherit the environment variables specified in the SAM stack file, or rather don't process all intrinsic functions used there, most notably `GetAtt`, so I had to provide the queue name separately for the tests. A bit awkward unfortunately. But other than that, this got the function execution working. Right now it relies on a script, but I'll work on enabling more automation shortly. But first, following the directions on [the web page](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-invoke.html) I moved the environment variables to a JSON file.

The next page in the AWS documentation on testing involves the [API Gateway](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html). I will return to that when I work on the function that is exposed via a Gateway entry.

On the next page we look at how to integrate this into automated tests. The key insight is to run a local "Lambda endpoint" using `sam local start-lambda`. This creates a local endpoint that emulates how the AWS Lambda endpoint behaves. That endpoint can then be called from an automated test script. My first attempts at this produce too much noise at the console, but at least they successfully run the function.

Along the way I learned the useful `sam local generate-event s3 put` command for generating JSON event files.

One practical problem at the time is that the function I am trying to test isn't actually returning anything useful, in fact it is expected to return the request it was given. I suppose I can test for that. But what I really want to test is that it adds a message to the SQS queue.

I decided to use the [moto](http://docs.getmoto.org/en/latest/index.html) mocking library, and to set up pytest. That made me think about Python module dependencies, and I'm going to try using [poetry](https://python-poetry.org/docs/) for that. Not sure yet how it will all integrate yet, but one step at a time.

I spent a lot of time troubleshooting timeout issues related to the local endpoint and how my Python boto3 client was connecting. It turns out I had configured the client to exit too soon (1 second timeout was not enough to spin up containers).

The biggest problem I am encountering with AWS SAM Accelerate now is that I cannot mock services called from the lambda functions there, as they are running outside of my test harnesses. So the way I see it there are two tests I can write:

- Unit tests that mock services and call on functions directly. These can't use the lambda invoke approach unless I can run them in the same process somehow, and I don't see how.
- Integration tests that reply on a test SAM deployment and syncing to speed up development.

I suspect there won't be much real work for the unit tests once I remove the invoking from the process, but we'll see. It does force me to break my code up into smaller pieces. So right now I have a process that simply pushes a message to a queue. I could perhaps write a unit test for it, but it frankly isn't doing anything.

Now having my first unit test running locally, I would like to automate that part of the process and add it to the github workflow system. I am thinking this is a separate workflow, and upon its successful completion the "deploy" workflow kicks in. So I need to build a dependence between the two actions.

Ok I have now added steps to my workflow to run pytest using poetry. I will now add coverage reporting, using `pytest-cov`. I would like something better at some point, as for now it doesn't really tell me precisely which lines are not covered, but I'll generate the XML which has this information for now.

Having this one test in place in a mocked fashion, I will now prepare the other two functions and unit tests for them, before setting up a non-mocked integration test. We have two more functions:

A function that will process an SQS event and update corresponding database entries. It's supposed to store counts by ip, by url, and a total. In order to run the queries, I can choose between using [PartiQL](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ql-reference.html) or more [classic API calls](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.API.html). I'm going to use classic API for now, though PartiQL is certainly interesting.

I have to admit writing the table queries was somewhat awkward, syntax-wise. But I now have a basic test for the db-writing function. I'll expand it to work on 3 different tables first before moving on to the retrieval function.

Now that I have the db-writing stuff set up I also need one more function that for a given host and path input will return the corresponding counts as well as the total count. I will later link that up to an API.

I ran into problems with a cloudformation stack update when I changed the name of a table, or rather tried to reuse an existing table in a new place in the stack. I will try a new name to see if that magically fixes things.

Moving on to the function that will read from the database, I find myself replicating the work that I did in my dynamodb class. I knew this was coming, and it's time to deal with it. The problem is that I want to have two different kinds of tables: Those I *create*, for example in testing, and those I *access*, during production and from my app functions. I essentially need Python's version of multiple constructors, so starting to look into that, using [this tutorial as a start](https://realpython.com/python-multiple-constructors/).

Ok I have now separated the construction part into a more general constructor.

At this point my three functions are ready, and what I need to do is integrate their wrappers to the various services and also set up some more integrated testing. In terms of connections, I would need the following:

- My sqs-message-creating function needs to be bound to the cloudfront distribution incoming requests.
- My sqs-message-consuming function needs to be set up to in fact consume from the appropriate queue.
- My sqs-counts-reporting function needs to be hooked up to an api endpoint that I can use to read its responses. I'll need to take care how this will interact with my cloudfront cache.

The first of these is done via a [LambdaFunctionAssociation](https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_LambdaFunctionAssociation.html) entry.

The other two should be settable via the Events property of the corresponding functions.

The first function was actually harder than expected. I had to first figure out how to create a Version rather than just a function, which only occurs if I specify an AutoDeployAlias setting. Next I had to specify in the function that its generated role should be able to be assumed by the edgelambda and lambda services. Then I had to give the role assumed by the github actions the permissions to create a [service-linked role](https://aws.amazon.com/blogs/security/introducing-an-easier-way-to-delegate-permissions-to-aws-services-service-linked-roles/). But before all that I had to stop using environment variables and start using SSM parameters, as edgelambda functions are not allow to use environment variables (amongst [numerous other restrictions](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/edge-functions-restrictions.html#lambda-requirements-lambda-function-configuration)).

Now that I finally got my lambda function recognized, I have to now deal with the problem that my function is not properly getting set up. I thought that the [package step](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/package.html) would have taken care of that, but it is clearly not working properly. Turns out the problem was that I was specifying the path in the `Globals` section of the template, and `aws cloudformation package` does not handle that well. There is an [open issue](https://github.com/aws/aws-cli/issues/3376) regarding this. For now I will simply duplicate the CodeUri on each place.

Now I have my function properly running, and I am encountering a problem with its permissions, as I need it to access a parameter. I will need to modify its policy settings.

While working on this, my GitHub action was behaving unexpectedly, due to [this issue](https://github.com/actions/runner/issues/491). Namely I was expecting "skipped jobs" from previous steps to be considered as successful for the purposes of triggering the next step, but that's not the default behavior.

I'm still not happy with the end conditional. It should not have triggered on the last run, as my actual conditional checks should not have passed. But moving on for now, I am ready to implement the other two functions by binding them to a SQS event and an API respectively.

The second function is reasonably ready, but in the process I found out the challenges related to specifying the names of resources, as the script can no longer update/replace them in some cases (e.g. databases). So at the moment I have a table that will be recreated if something changes in it, and I need to figure out how to migrate its data.

But that's a problem for another day. For now I want to get the third function going, the one that has its own API endpoint and reports the counts. Reading about it more, it appears I may be able to set up an API that [directly interfaces](https://serverlessland.com/patterns/apigw-dynamodb) with [the dynamodb instance and avoids a lambda function call](https://aws.amazon.com/blogs/compute/using-amazon-api-gateway-as-a-proxy-for-dynamodb/). The samples provided use either the console or the standard cloudformation templates. I will try to set it up via [SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-api.html).

My first challenge is that I would like to be able to create a test stack, but right now my code depends on certain SSM parameters whose names are hard-coded in both the template and the functions. I'll need to make their names variable, depending on a parameter.

With that out of the way, I am going to work on setting up a SAM Api endpoint. I will be using the [OpenAPI standard somewhere along the way](https://oai.github.io/Documentation/start-here.html), so I am going to read up on that first. I will also set up a small test template instead of mucking about with the counters template.

Trying to figure this setup out I am finding a number of problems:

I have fundamentally two ways to set up the API:

- I can use a SAM API entry with a DefinitionURI link to a OpenAPI document. This document would spell out the different resources, methods, and also [integrations there](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions.html). In order for that to work I need to know the exact name of the tables I want to use, and I don't know that ahead of time as they are dynamically generated, and I have no way to inject parameters into the DefinitionURI entry.
- I can use the DefinitionBody entry instead and inline all the OpenAPI stuff there, but I find that a bit awkward. Still it might be the only way to have dynamically generated parts to it. Reading the DefinitionBody documentation, it suggests using an [Include transform](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/create-reusable-transform-function-snippets-and-add-to-your-template-with-aws-include-transform.html) to import an OpenAPI file into the template, and then that file may have other intrinsic functions in it.
- I would have liked to use a SAM Api entry but then specify all the resources and methods as separate cloudformation entries. But that doesn't seem quite possible at the moment unless the integrations are functions. This is because the SAM Api automatically creates a deployment. But this deployment will fail if methods don't exist. So we need to specify that the deployment depends on the method resources. These resources in turn depend on the API, so there is no way to accomplish that without separating the deployment and the api, in other words without using serverless api entry and instead creating our own direct api, deployment and stage entries. I was hoping to avoid that route. Although it is perhaps the most transparent.

At this point it might be good to take a pause and outline what I have done so far on this "day" that has become more like a week.

- I started with a lambda function that triggers whenever my cloud distribution is asked to serve a page (whether cashed or not). This function then sets up a SQS message. This SQS message is processed by another function which works with a dynamodb table to keep track of counts.
- Then I proceeded to reading that information, and I decided to use an API Gateway for that. The basics for this Gateway currently exist in a test api file and they use a serverless API resource with an OpenAPI specification file associated with it. Getting all that to work smoothly was anything but smooth. But the result is fairly nice: I am able to "translate" a request to my API into a request to the AWS DynamoDB API via an "integration" process, and as a result I don't need the overhead of using a Lambda function. In the long run I would like to effect the same to the original update but I am not sure that is possible.
