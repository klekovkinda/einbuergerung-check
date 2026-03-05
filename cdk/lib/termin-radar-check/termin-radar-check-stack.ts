import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import {Architecture, DockerImageCode, DockerImageFunction} from "aws-cdk-lib/aws-lambda";
import path from "path";
import * as events from "aws-cdk-lib/aws-events";
import * as iam from "aws-cdk-lib/aws-iam";
import * as targets from "aws-cdk-lib/aws-events-targets";

export interface TerminRadarCheckStackProperties extends cdk.StackProps {
    propertyPrefix: string,
    terminRadarServiceProperties: {
        service_name: string
        trigger_check_schedule: events.Schedule
    }[]
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
                PROPERTY_PREFIX: props.propertyPrefix,
                POWERTOOLS_SERVICE_NAME: 'TerminRadarCheckFunction',
                LOG_LEVEL: "debug"
            }
        });

        //Add policy to read SSM parameters
        props.terminRadarServiceProperties.forEach(serviceProperty => {
            `${props.propertyPrefix}/${serviceProperty.service_name}/*`
            terminRadarCheckFunction.addToRolePolicy(new iam.PolicyStatement({
                actions: ['ssm:GetParameter'],
                resources: [`arn:aws:ssm:${this.region}:${this.account}:parameter/${props.propertyPrefix}/${serviceProperty.service_name}/*`]
            }));
        })

        props.terminRadarServiceProperties.forEach(serviceProperty => {
            new events.Rule(this, `Check${serviceProperty.service_name}Rule`, {
                ruleName: `TriggerCheck${serviceProperty.service_name}Rule`,
                schedule: serviceProperty.trigger_check_schedule,
                targets: [new targets.LambdaFunction(terminRadarCheckFunction, {
                    event: events.RuleTargetInput.fromObject({
                        service_name: serviceProperty.service_name,
                    })
                })],
            });
        });
    }
}
