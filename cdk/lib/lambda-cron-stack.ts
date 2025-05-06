import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as path from 'path';

export class LambdaCronStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const githubTokenSecret = secretsmanager.Secret.fromSecretNameV2(this, 'TerminRadarGitHubTokenSecret', 'GITHUB_TOKEN');

    const lambdaFunction = new lambda.Function(this, 'CronLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, 'lambda'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_9.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }),
      environment: {
        GITHUB_TOKEN_SECRET_ARN: githubTokenSecret.secretArn,
      },
    });

    // Grant the Lambda function permissions to read the secret
    githubTokenSecret.grantRead(lambdaFunction);

    new events.Rule(this, 'CronRule', {
      schedule: events.Schedule.cron({ minute: '*', hour: '4-21' }),
      targets: [new targets.LambdaFunction(lambdaFunction)],
    });
  }
}
