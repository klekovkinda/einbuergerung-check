import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import {Architecture, DockerImageCode, DockerImageFunction} from "aws-cdk-lib/aws-lambda";
import path from "path";
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";

export interface TerminRadarCheckStackProperties extends cdk.StackProps {
}

export class TerminRadarCheckStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: TerminRadarCheckStackProperties) {
        super(scope, id, props);
        const lambdaDir = path.join(__dirname, 'lambda');

        const terminRadarCheckFunction = new DockerImageFunction(this, `Lambda`, {
            functionName: 'TerminRadarCheckFunction',
            description: "Lambda function that load the page and analysis the content to check if there are new appointments available",
            code: DockerImageCode.fromImageAsset(lambdaDir),
            memorySize: 2048,
            timeout: cdk.Duration.seconds(60),
            architecture: Architecture.X86_64,
            environment: {
                LOG_LEVEL: "debug"
            }
        });

        new events.Rule(this, `TriggerRule`, {
            ruleName: `Trigger${terminRadarCheckFunction.functionName}Rule`, schedule: events.Schedule.cron({
                minute: '0', hour: '11'
            }), targets: [new targets.LambdaFunction(terminRadarCheckFunction, {
                event: events.RuleTargetInput.fromObject({
                    service_url: "https://service.berlin.de/terminvereinbarung/termin/all/351180/"
                })
            })],
        });
    };
}
