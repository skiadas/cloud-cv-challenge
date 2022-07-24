#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DistroStack } from '../lib/distro-stack';

const app = new cdk.App();
new DistroStack(app, 'skiadas-resume', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'us-east-1' },
});
