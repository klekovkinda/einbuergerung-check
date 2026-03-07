import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";
import {IBucket} from "aws-cdk-lib/aws-s3/lib/bucket";
import {pascalize} from "humps";
import {
    TerminRadarLoadServicePageLambdaFunctionBuilder
} from "./termin-radar-load-service-page-lambda-function/termin-radar-load-service-page-lambda-function-builder";
import {
    TerminRadarCheckStepFunctionBuilder
} from "./termin-radar-check-step-function/termin-radar-check-step-function-builder";
import {TerminRadarAlgorithmsBuilder} from "./termin-radar-algorithms/termin-radar-algorithms-builder";

export interface TerminRadarCheckStackProperties extends cdk.StackProps {
    domain: string,
    shortTermBucket: IBucket,
    terminRadarServiceProperties: {
        serviceName: string
        triggerCheckSchedule: events.Schedule
    }[]
}

export class TerminRadarCheckStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: TerminRadarCheckStackProperties) {
        super(scope, id, props);

        const serviceNames = props.terminRadarServiceProperties.map(serviceProperty => serviceProperty.serviceName)

        const terminRadarLoadServicePageLambdaFunction = new TerminRadarLoadServicePageLambdaFunctionBuilder(this, {
            domain: props.domain, shortTermBucket: props.shortTermBucket, serviceNames: serviceNames
        }).build()

        //Create algorithms
        const algorithmsFunctions = new TerminRadarAlgorithmsBuilder(this, props.domain, serviceNames, props.shortTermBucket).build();

        //Create check Step Function
        const terminRadarCheckStepFunction = new TerminRadarCheckStepFunctionBuilder(this, {
            domain: props.domain,
            serviceNames: serviceNames,
            loadServicePageLambdaFunction: terminRadarLoadServicePageLambdaFunction,
            algorithmsFunctions: algorithmsFunctions
        }).build()

        //create check triggers for each service
        props.terminRadarServiceProperties.forEach(serviceProperty => {
            new events.Rule(this, `TriggerCheck${pascalize(serviceProperty.serviceName)}Rule`, {
                ruleName: `${props.domain}-trigger-${serviceProperty.serviceName}-check-step-function-rule`,
                schedule: serviceProperty.triggerCheckSchedule,
                targets: [new targets.SfnStateMachine(terminRadarCheckStepFunction, {
                    input: events.RuleTargetInput.fromObject({
                        service_name: serviceProperty.serviceName,
                    })
                })],
            });
        });
    }
}
