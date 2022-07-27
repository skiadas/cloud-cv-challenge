// Distribution backed by S3 bucket
// Populates bucket contents based on provided source
// Optional customization for domain
import { Duration } from "aws-cdk-lib";
import {
  Distribution,
  IDistribution,
  DistributionProps,
  IOrigin,
  HeadersFrameOption,
  HeadersReferrerPolicy,
  ResponseHeadersPolicy,
  ViewerProtocolPolicy,
} from "aws-cdk-lib/aws-cloudfront";

import { Construct } from "constructs";

import { CFFunction } from "./cf-functions";
import { ManagedBucket } from "./managed-bucket";
import { DistroWrapper } from "./wrappers/distro-wrapper";

import * as path from "path";

export interface S3BackedDistroProps {
  origin: IOrigin,
  wrappers: DistroWrapper[]
}

export class S3BackedDistro extends Construct {
  public readonly distribution: IDistribution;

  constructor(scope: Construct, id: string, props: S3BackedDistroProps) {
    super(scope, id);

    const logs = new ManagedBucket(this, "cloudfrontLogsBucket");

    const associations = new CFFunction(this, 'cf-function', {
      filePath: path.join(__dirname, "../cf_functions/redirectForSession.js")
    }).associations;

    // General distrProps that apply to both domain and non-domain
    let distrProps: DistributionProps = {
      defaultBehavior: {
        origin: props.origin,
        responseHeadersPolicy: headersPolicy(this),
        viewerProtocolPolicy: ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        functionAssociations: associations,
      },
      logBucket: logs.bucket,
      errorResponses: [errorPage(403), errorPage(404)],
    };

    for (const wrapper of props.wrappers) {
      distrProps = wrapper.alterProps(distrProps);
    }

    this.distribution = new Distribution(this, "cloudfrontDistro", distrProps);

    for (const wrapper of props.wrappers) {
      wrapper.finalizeDistro(this.distribution);
    }
  }
}


function errorPage(code: number) {
  return {
    httpStatus: code,
    responseHttpStatus: code,
    responsePagePath: `/${code}.html`,
    ttl: Duration.minutes(60)
  };
}

function headersPolicy(scope: Construct) {
  return new ResponseHeadersPolicy(scope, 'headersPolicy', {
    securityHeadersBehavior: {
      contentSecurityPolicy: {
        contentSecurityPolicy: "default-src 'none'; img-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'",
        override: true
      },
      contentTypeOptions: { override: true },
      frameOptions: {
        frameOption: HeadersFrameOption.SAMEORIGIN,
        override: true
      },
      referrerPolicy: {
        referrerPolicy: HeadersReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN,
        override: true
      },
      strictTransportSecurity: {
        accessControlMaxAge: Duration.minutes(10),
        includeSubdomains: true,
        override: true,
        preload: true
      },
      xssProtection: {
        protection: true,
        override: true,
        modeBlock: true
      }
    }
  });
}

