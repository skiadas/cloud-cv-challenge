import { Stack, StackProps, Tags } from 'aws-cdk-lib';
import { IDistribution } from 'aws-cdk-lib/aws-cloudfront';
import { IBucket } from 'aws-cdk-lib/aws-s3';
import { Source } from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';

import * as path from 'path';

import { S3BackedDistro } from './s3-distro';

// Stack that sets up the cloudfront distribution and related items
export class DistroStack extends Stack {
  public readonly bucket: IBucket;
  public readonly distribution: IDistribution;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);
    Tags.of(this).add("project", "skiadas-resume");

    const s3distro = new S3BackedDistro(this, "s3-plus-distro", {
      source: Source.asset(path.join(__dirname, "../../site")),
      hosting: {
        subdomain: 'resume',
        domain: 'harisskiadas.com'
      }
    });

    this.bucket = s3distro.bucket;
    this.distribution = s3distro.distribution;
  }
}
