# Cloud Development Kit

Reading up starting from [this page](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html).

- A CDK app can be in TypeScript, JS, Python, Java, C# or Go
- App defines **Stacks**, equivalent to the CF stacks
- Each stack consists of **Constructs** which define resources
- Constructs are represented as classes in the language
- The CDK Toolkit/CLI allows working with the apps, deploying etc

Constructs come in three variations:

- AWS Cloudformation-only (Level 1): Correspond directly to CF resource types. Names beginning with `Cfn`. Part of the `aws-cdk-lib` library.
- Curated (Level 2): Developed by the CDK team to address specific use cases and simplify infrastructure development. Encapsulate L1 resources, providing defaults etc.
- Patterns (Level 3): Declare multiple resources to create entire infrastructures.

[API reference](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-construct-library.html)

The [AWS Toolkit for VS Code](https://aws.amazon.com/visualstudiocode/) will prove quite handy I think.

[Assertion library](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.assertions-readme.html)
