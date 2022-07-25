// Distribution backed by S3 bucket
// Populates bucket contents based on provided source
// Optional customization for domain
import { RemovalPolicy } from "aws-cdk-lib";
import { DnsValidatedCertificate } from "aws-cdk-lib/aws-certificatemanager";
import { Distribution, IDistribution } from "aws-cdk-lib/aws-cloudfront";
import { S3Origin } from "aws-cdk-lib/aws-cloudfront-origins";
import { ARecord, HostedZone, RecordTarget } from "aws-cdk-lib/aws-route53";
import { CloudFrontTarget } from "aws-cdk-lib/aws-route53-targets";
import { Bucket, BlockPublicAccess, IBucket } from "aws-cdk-lib/aws-s3";
import { BucketDeployment, ISource, Source } from "aws-cdk-lib/aws-s3-deployment";
import { Construct } from "constructs";

export interface S3BackedDistroProps {
  source: ISource,
  hosting?: { domain: string, subdomain: string }
}

export class S3BackedDistro extends Construct {
  public readonly bucket: IBucket;
  public readonly distribution: IDistribution;

  constructor(scope: Construct, id: string, props: S3BackedDistroProps) {
    super(scope, id);

    const staticPages = new Bucket(this, "staticPagesBucket", {
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });
    // Used to upload the files
    const deployment = new BucketDeployment(this, "filesDeployment", {
      sources: [props.source],
      destinationBucket: staticPages,
    });

    this.bucket = deployment.deployedBucket;

    if ("hosting" in props) {
      this.distribution = new Distribution(this, "cloudfrontDistro", {
        defaultBehavior: { origin: new S3Origin(staticPages) },
      });
      return;
    }
    // Customization below revolves around having a domain. We need:
    // 1. A hosted zone entity
    // 2. A certificate
    // 3. More elements in distribution constructor
    // 4. A route 53 alias record that references the distribution
    const hosting = props.hosting!;
    const fullDomainName = `${hosting.subdomain}.${hosting.domain}`;

    const hostedZone = HostedZone.fromLookup(this, "zone", {
      domainName: hosting.domain,
    });

    const cert = new DnsValidatedCertificate(this, "acmCertificate", {
      hostedZone: hostedZone,
      domainName: fullDomainName,
      cleanupRoute53Records: true,
      region: "us-east-1",
    });

    const distribution = new Distribution(this, "cloudfrontDistro", {
      defaultBehavior: { origin: new S3Origin(staticPages) },
      domainNames: [fullDomainName],
      certificate: cert,
    });

    this.distribution = distribution;

    new ARecord(this, "AliasRecord", {
      zone: hostedZone,
      recordName: fullDomainName,
      target: RecordTarget.fromAlias(new CloudFrontTarget(distribution)),
    });
  }
}
