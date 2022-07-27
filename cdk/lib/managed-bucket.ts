// A bucket that gets auto-deleted, and is possibly populated
// via a bucket deployment from some folder contents

import { RemovalPolicy } from "aws-cdk-lib";
import { BlockPublicAccess, Bucket, IBucket } from "aws-cdk-lib/aws-s3";
import { BucketDeployment, ISource } from "aws-cdk-lib/aws-s3-deployment";
import { Construct } from "constructs";

export class ManagedBucket extends Construct {
  public readonly bucket: IBucket;
  public deployedBucket?: IBucket;
  private id: string;

  constructor(scope: Construct, id: string) {
    super(scope, id);
    this.id = id;
    this.bucket = new Bucket(scope, id + '-bucket', {
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });
  }

  deployFrom(source: ISource) {
    const deployment = new BucketDeployment(this, this.id + "-deployment", {
      sources: [source],
      destinationBucket: this.bucket,
    });
    this.deployedBucket = deployment.deployedBucket;
    return this;
  }
}
