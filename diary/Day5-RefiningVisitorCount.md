# Day 5 Refining the visitor count

In this section I will work on refining the visitor count mechanism. My plan is as follows:

- Add sessions. My visitor request edge lambda will simply 302 redirect to itself while adding a set-cookie entry to establish a session. If a session already exists then it updates it (2 hour max duration), creates a sqs event, and passes the request onwards.
- Table update: I will use a single table that records "visits" containing information about IP, path, and session. I will use a "visit" primary key that combines the session id, path, IP and timestamp, and I will also add three global secondary indexes for IP address, path and session, although I likely won't use the session one much at this point in time.
- I will make sure my function only records html and json file requests.
- I will then expose the table and the indexes through the api gateway.

I'm starting with the first item, creating and maintaining sessions. I found this [code sample](https://gist.github.com/davemaple/64e205f553121675c0ad1a29a7cb86bd) for how to do it using Node, and I'll be adjusting the code to do the same steps in my Python function. I found details on the [event structure here](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/functions-event-structure.html#functions-event-structure-query-header-cookie). I'm also taking advantage of the fact that Cloudfront now does the header and cookie processing for me.

In order to troubleshoot this further, I need a way to also deploy a cloudfront distribution in a test/development setting. In order to do that I need to separate the domain settings, so that I can create the distribution without an exposed domain. To do that I'll need to use some [conditional sections](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html).

Now that I have set this up, I can get back to troubleshooting my function without having to push a commit every time. The problem was the common problem with Python dictionaries and attempting a deep dive in the absence of a key along the way. I would like to have an elegant way of saying "try this path or else return None". But the built-in dictionaries don't do that in a way that I know.

After a lot of trial and error, and some console logging, I figured out how to get the initial redirect to work. A lot of my problems stemmed from the fact that cloudfront accepts two different kinds of "functions": the standard lambda@edge and some separate cloudfront-specific functions. The problem is that the two kinds of functions receive different event formats, and I was using the wrong documentation for a while.

In the long run I want to remove the visits code from lambda@edge, because it is particularly costly time-wise right now. In order to process the visit I have to send it over to my infrastructure, even if it is just a queue. I want to transition to a setup where the visits are reported via some javascript code calling an API when the page loads. Or else from processing cloudwatch logs although I'm not crazy about using the logs for that. The Javascript approach needs to know if the page was cached locally, and it looks like there's [an event for that](https://developer.mozilla.org/en-US/docs/Web/API/PageTransitionEvent). I might use that if I decide to distinguish between cached and not.

For the time being, I will do the following:

1. I will switch my session-setting function from lambda@edge to cloudfront functions.
2. I will add a cloudfront function to the response, to refresh the session.

Looking at this closer, I ran into an annoying property of CloudFormation, namely its very limited capacity for including content from other files. It expects me to include the function as a text string within the CF file, which is really not acceptable for me as I want to be able to test the function as a function locally. I will start by taking a look at the [Cloud Development Kit](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) and see if that can provide me with an alternative approach, to do all these things I want to do.

I'll work through the [AWS CDK Workshop](https://cdkworkshop.com/) project, to learn more about the CDK.

I found there a link to a [guide for testing in CDK](https://docs.aws.amazon.com/cdk/v2/guide/testing.html).

After going through the workshop, I am ready to move my templates over to CDK. I'll need to do the following:

1. I need to disable the existing workflow
2. I will bring down the current stack. On a live platform that would have been a different matter.
3. I will create a minimal app in CDK, then make a new workflow to deploy it.
4. Once that is working, I will then gradually create the needed CDK parts that match the elements in the existing templates. Along the way I will also move to using a single table to hold the visits.


