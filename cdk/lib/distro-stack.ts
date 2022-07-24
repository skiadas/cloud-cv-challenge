import { Stack, StackProps, Tags, RemovalPolicy } from 'aws-cdk-lib';
import { Distribution, IDistribution } from 'aws-cdk-lib/aws-cloudfront';
import { S3Origin } from 'aws-cdk-lib/aws-cloudfront-origins';
import { Bucket, BlockPublicAccess, IBucket } from 'aws-cdk-lib/aws-s3';
import { BucketDeployment, Source } from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';
import * as path from 'path';

// Stack that sets up the cloudfront distribution and related items
export class DistroStack extends Stack {
  public readonly bucket: IBucket;
  public readonly distribution: IDistribution;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);
    Tags.of(this).add("project", "skiadas-resume");

    const staticPages = new Bucket(this, "staticPagesBucket", {
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });
    // Used to upload the files
    const deployment = new BucketDeployment(this, 'filesDeployment', {
      sources: [Source.asset(path.join(__dirname, '../../site'))],
      destinationBucket: staticPages
    });

    this.bucket = deployment.deployedBucket;

    const distribution = new Distribution(this, 'cloudfrontDistro', {
      defaultBehavior: { origin: new S3Origin(staticPages) }
    });

    this.distribution = distribution;

  }
}
