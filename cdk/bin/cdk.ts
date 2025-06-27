#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { GhTriggerStack } from '../lib/gh-trigger/gh-trigger-stack';

const app = new cdk.App();

new GhTriggerStack(app, 'GhTriggerStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

cdk.Tags.of(app).add('cdk:bootstrap', 's3://termin-radar-cdk-bucket');
