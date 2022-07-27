
import { DnsValidatedCertificate } from "aws-cdk-lib/aws-certificatemanager";
import { DistributionProps, IDistribution } from "aws-cdk-lib/aws-cloudfront";
import { ARecord, HostedZone, IHostedZone, RecordTarget } from "aws-cdk-lib/aws-route53";
import { CloudFrontTarget } from "aws-cdk-lib/aws-route53-targets";
import { Construct } from "constructs";
import { DistroWrapper } from "./distro-wrapper";

export interface DomainWrapperProps {
  domain: string;
  subdomain: string;
}

export class DomainWrapper extends Construct implements DistroWrapper {
  private id: string;
  private domain: string;
  private subdomain: string;
  private hostedZone: IHostedZone;
  private cert: DnsValidatedCertificate;

  constructor(scope: Construct, id: string, props: DomainWrapperProps) {
    super(scope, id);
    this.id = id;
    this.domain = props.domain;
    this.subdomain = props.subdomain;

    this.hostedZone = HostedZone.fromLookup(this, this.id + "zone", {
      domainName: this.domain,
    });
    this.cert = new DnsValidatedCertificate(this, "acmCertificate", {
      hostedZone: this.hostedZone,
      domainName: this.fullDomainName(),
      cleanupRoute53Records: true,
      region: "us-east-1",
    });
  }

  alterProps(props: DistributionProps) {
    return {
      ...props,
      certificate: this.cert,
      domainNames: [this.fullDomainName()],
    };
  }

  finalizeDistro(distro: IDistribution) {
    new ARecord(this, "AliasRecord", {
      zone: this.hostedZone,
      recordName: this.fullDomainName(),
      target: RecordTarget.fromAlias(new CloudFrontTarget(distro)),
    });
  }

  private fullDomainName(): string {
    return `${this.subdomain}.${this.domain}`;
  }
}
