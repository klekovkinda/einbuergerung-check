#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { LambdaCronStack } from '../lib/gh-trigger/lambda-cron-stack';

const app = new cdk.App();

new LambdaCronStack(app, 'LambdaCronStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

cdk.Tags.of(app).add('cdk:bootstrap', 's3://termin-radar-cdk-bucket');
