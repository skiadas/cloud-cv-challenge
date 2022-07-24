import * as cdk from "aws-cdk-lib";
import { Template, Match } from "aws-cdk-lib/assertions";
import { DistroStack } from '../lib/distro-stack';

describe("ProcessorStack", () => {
  test("synthesizes the way we expect", () => {
    const app = new cdk.App();
    const distro = new DistroStack(app, 'testDistro');
    const template = Template.fromStack(distro);

    template.hasResource("AWS::S3::Bucket", {
      Properties: {
        Tags: Match.arrayWith([{ Key: "project", Value: "skiadas-resume" }]),
    }
  });
  });
});
