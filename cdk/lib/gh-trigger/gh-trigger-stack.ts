import * as cdk from 'aws-cdk-lib';
import {Construct} from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as path from 'path';
import * as iam from 'aws-cdk-lib/aws-iam';
import {addDefaultTags, getPowertoolsLayer} from "../utils";
import {Architecture} from "aws-cdk-lib/aws-lambda";

export class GhTriggerStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const parameterName = '/TerminRadar/GitHubToken';

        const runAppointmentCheckGHWorkflowFunction = new lambda.Function(this, `${id}Lambda`, {
            functionName: 'RunAppointmentCheckGHWorkflowFunction',
            description: "Lambda function to trigger the GitHub workflow for checking available appointments",
            runtime: lambda.Runtime.PYTHON_3_13,
            architecture: Architecture.ARM_64,
            handler: 'index.handler',
            layers: [getPowertoolsLayer(this)],
            code: lambda.Code.fromAsset(path.join(__dirname, 'lambda'), {
                bundling: {
                    image: lambda.Runtime.PYTHON_3_13.bundlingImage,
                    command: ['bash',
                              '-c',
                              'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'],
                },
            }),
            environment: {
                GITHUB_TOKEN_PARAMETER_NAME: parameterName,
            },
        });

        runAppointmentCheckGHWorkflowFunction.addToRolePolicy(new iam.PolicyStatement({
            actions: ['ssm:GetParameter'],
            resources: [`arn:aws:ssm:${this.region}:${this.account}:parameter${parameterName}`],
        }));

        new events.Rule(this, `${id}Rule`, {
            ruleName: `Trigger${runAppointmentCheckGHWorkflowFunction.functionName}Rule`,
            schedule: events.Schedule.cron({
                minute: '*/5',
                hour: '4-20'
            }),
            targets: [new targets.LambdaFunction(runAppointmentCheckGHWorkflowFunction)],
        });
        addDefaultTags(this);
    }
}
