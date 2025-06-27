import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as path from 'path';
import * as iam from 'aws-cdk-lib/aws-iam';

export class LambdaCronStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const parameterName = '/TerminRadar/GitHubToken';

    const lambdaFunction = new lambda.Function(this, 'CronLambda', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, 'lambda'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_11.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }),
      environment: {
        GITHUB_TOKEN_PARAMETER_NAME: parameterName,
      },
    });

    lambdaFunction.addToRolePolicy(new iam.PolicyStatement({
      actions: ['ssm:GetParameter'],
      resources: [`arn:aws:ssm:${this.region}:${this.account}:parameter${parameterName}`],
    }));

    new events.Rule(this, 'CronRule', {
      schedule: events.Schedule.cron({ minute: '*/2', hour: '4-20' }),
      targets: [new targets.LambdaFunction(lambdaFunction)],
    });
  }
}
