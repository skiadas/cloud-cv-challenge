# Cloud formation rest api gateway notes

I decided to start a dedicated page to understand the various Cloud Formation components of a rest api gateway setup, as there appear to be a number of moving pieces. Looking at the various Gateway components, I see the following extremely long list:

- [AWS::ApiGateway::Account](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-account.html) This is used to specify the IAM role that the Gateway will use to write to logs. I wonder if I'll need to specify it.
- [AWS::ApiGateway::ApiKey](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-apikey.html) is for creating a unique key to give to clients in order for them to access the service. I doubt I'll need this initially as I'll keep things open.
- [AWS::ApiGateway::Authorizer](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html) is there to create an authorization layer for methods that need it. I'll probably need to add for the post methods
- [AWS::ApiGateway::BasePathMapping](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-basepathmapping.html) Is used to relate a path to a specific stage (e.g. v1), at least that's what I think. It will probably become relevant when I link the api to my domain
- [AWS::ApiGateway::ClientCertificate](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-clientcertificate.html) is used to configure client-side SSL authentication. Not sure I'll need this right now.
- [AWS::ApiGateway::Deployment](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-deployment.html) "deploys a resource to a stage" so that it can be accessed over the internet. It looks like this is one of the parts automatically created by using [AWS::Serverless::Api](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification-generated-resources-api.html), along with the Stage element.
- [AWS::ApiGateway::DocumentationPart](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationpart.html) I'm not sure about yet
- [AWS::ApiGateway::DocumentationVersion](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-documentationversion.html) not sure either. Looks like I'll need to read [Representation of API documentation in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-documenting-api-content-representation.html) at some point
- [AWS::ApiGateway::DomainName](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-domainname.html) is used to specify a custom domain name. Looks like I'll get the same effect by specifying the DomainName property of the serverless API  resource.
- [AWS::ApiGateway::GatewayResponse](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification-generated-resources-api.html) Is about creating a response, which seems a bit weird to me to have as a resource. Maybe [The guide entry on responses might help](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-gatewayResponse-definition.html#api-gateway-gatewayResponse-definition).
- [AWS::ApiGateway::Method](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html) define methods, which specify what clients must send. Sounds like I might need to work with those for sure.
- [AWS::ApiGateway::Model](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-model.html) "defines the structure of a request or response payload for a method". Sounds like I might need a model for my responses.
- [AWS::ApiGateway::RequestValidator](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-requestvalidator.html) sets up basic validation rules for incoming requests. I'll need to [read about it here](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-method-request-validation.html).
- [AWS::ApiGateway::Resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-resource.html) will be needed in order to set up the basic resources.
- [AWS::ApiGateway::RestApi](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html) actually creates the basic API resource. I am using the Serverless one instead so won't need to set this directly.
- [AWS::ApiGateway::Stage](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-stage.html) will similarly be set for me.
- [AWS::ApiGateway::UsagePlan](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplan.html) is useful for setting limits and throttling usage.
- [AWS::ApiGateway::UsagePlanKey](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-usageplankey.html) associates a key with a usage plan.
- [AWS::ApiGateway::VpcLink](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-vpclink.html) is used to let the api access resources within a vpc. I won't be needing this at this stage.

So I will likely need Resource, Method, Model and maybe GatewayResponse, to start with. Looking at a [sample](https://serverlessland.com/patterns/apigw-dynamodb) for what I am trying to do, they seem to be using the following:

- MusicResource, a resource
- MusicMethodPost which is a method
- MusicArtistResource which is a resource
- MusicArtistMethodGet which is a method
- ApiDeployment, ApiKey, ApiUsagePlan, ApiUsagePlanKey, APIGatewayRole, Api

There are a number of [API Gateway tutorials](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-tutorials.html) available, I'm thinking I should go through some of them first. One of the problems is that I am trying to use OpenAPI, and that adds another layer of complexity. Basically it appears I have two options for creating the various components:

- Use an OpenAPI specification with all the integrations spelled out, and add it in the DocumentUri field.
- Create separate resources as described above, in a standard CloudFormation file.

The 2nd version sounds simpler to me for now, so I will follow that. It's tricky to combine the two it seems.

## Integrations with other APIs

When creating a custom integration to another API, a key element is the [x-amazon-apigateway-integration object](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions-integration.html). It essentially specifies:

- To what other API an incoming request will be sent to
- How the `requestParameters` of the incoming request need to be converted into the parameters for the integration API
- How the request body is to be used to produce the body for the integration request, based on a `requestTemplate`
- How the `integrationResponses` from the API are to be modified before returned as our response, using Velocity Template Language


