import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import {IStateMachine} from "aws-cdk-lib/aws-stepfunctions/lib/state-machine";
import * as logs from "aws-cdk-lib/aws-logs";
import * as cdk from "aws-cdk-lib";
import {Stack} from "aws-cdk-lib";
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import {IFunction} from "aws-cdk-lib/aws-lambda/lib/function-base";


export interface TerminRadarCheckStepFunctionBuilderProperties {
    domain: string;
    serviceNames: string[];
    loadServicePageLambdaFunction: IFunction
}

export class TerminRadarCheckStepFunctionBuilder {
    private readonly stateMachineName: string;
    private readonly stateMachineParamListAccess: string[];

    constructor(private scope: any, private props: TerminRadarCheckStepFunctionBuilderProperties) {
        const account = Stack.of(scope).account;
        const region = Stack.of(scope).region;
        this.stateMachineName = `${this.props.domain}-check-step-function`;
        this.stateMachineParamListAccess = props.serviceNames.map(serviceName => `arn:aws:ssm:${region}:${account}:parameter/${props.domain}/${serviceName}/service-url`);
    }

    public build(): IStateMachine {

        const getServiceParamsTask = new tasks.CallAwsService(this.scope, 'GetServiceParamURL', {
            comment: 'Get service parameter url from SSM Parameter Store',
            iamResources: this.stateMachineParamListAccess,
            iamAction: 'ssm:GetParameter',
            service: 'ssm',
            action: 'getParameter',
            parameters: {
                Name: `{% '/${this.props.domain}/' & $states.input.service_name  & '/service-url' %}`
            },
            outputs: "{% $merge([$states.input, { 'service_url': $states.result.Parameter.Value }]) %}",
            queryLanguage: sfn.QueryLanguage.JSONATA
        });

        const loadServicePageTask = new tasks.LambdaInvoke(this.scope, 'LoadServicePage', {
            lambdaFunction: this.props.loadServicePageLambdaFunction,
            outputs: "{% $merge([$states.input, $states.result.Payload]) %}",
            queryLanguage: sfn.QueryLanguage.JSONATA
        });

        //TODO add step to get param page_parser so we can call different parser for different service if needed in the future

        const terminRadarCheckStepFunctionLogGroup = new logs.LogGroup(this.scope, 'TerminRadarCheckStepFunctionLogGroup', {
            logGroupName: `/aws/stateMachine/${this.stateMachineName}`,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            retention: logs.RetentionDays.FIVE_DAYS,
        });

        return new sfn.StateMachine(this.scope, 'CheckStepFunction', {
            stateMachineName: `${this.props.domain}-check-step-function`,
            definitionBody: sfn.DefinitionBody.fromChainable(sfn.Chain.start(getServiceParamsTask.next(loadServicePageTask))),
            timeout: cdk.Duration.minutes(5),
            tracingEnabled: true,
            logs: {
                destination: terminRadarCheckStepFunctionLogGroup, includeExecutionData: true, level: sfn.LogLevel.ALL,
            },
        })
    }
}
