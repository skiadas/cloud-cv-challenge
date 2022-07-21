# Day 5 Refining the visitor count

In this section I will work on refining the visitor count mechanism. My plan is as follows:

- Add sessions. My visitor request edge lambda will simply 302 redirect to itself while adding a set-cookie entry to establish a session. If a session already exists then it updates it (2 hour max duration), creates a sqs event, and passes the request onwards.
- Table update: I will use a single table that records "visits" containing information about IP, path, and session. I will use a "visit" primary key that combines the session id, path, IP and timestamp, and I will also add three global secondary indexes for IP address, path and session, although I likely won't use the session one much at this point in time.
- I will make sure my function only records html and json file requests.
- I will then expose the table and the indexes through the api gateway.

I'm starting with the first item, creating and maintaining sessions. I found this [code sample](https://gist.github.com/davemaple/64e205f553121675c0ad1a29a7cb86bd) for how to do it using Node, and I'll be adjusting the code to do the same steps in my Python function. I found details on the [event structure here](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/functions-event-structure.html#functions-event-structure-query-header-cookie). I'm also taking advantage of the fact that Cloudfront now does the header and cookie processing for me.

In order to troubleshoot this further, I need a way to also deploy a cloudfront distribution in a test/development setting. In order to do that I need to separate the domain settings, so that I can create the distribution without an exposed domain. To do that I'll need to use some [conditional sections](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html).
