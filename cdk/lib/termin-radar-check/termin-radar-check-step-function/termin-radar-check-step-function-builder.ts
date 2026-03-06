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
    private readonly serviceParamUrlListAccess: string[];
    private readonly serviceParamPageAnalyzeAlgorithmListAccess: string[];

    constructor(private scope: any, private props: TerminRadarCheckStepFunctionBuilderProperties) {
        const account = Stack.of(scope).account;
        const region = Stack.of(scope).region;
        this.stateMachineName = `${this.props.domain}-check-step-function`;
        this.serviceParamUrlListAccess = props.serviceNames.map(serviceName => `arn:aws:ssm:${region}:${account}:parameter/${props.domain}/${serviceName}/url`);
        this.serviceParamPageAnalyzeAlgorithmListAccess = props.serviceNames.map(serviceName => `arn:aws:ssm:${region}:${account}:parameter/${props.domain}/${serviceName}/page-analyze-algorithm`);
    }

    public build(): IStateMachine {

        const getServiceParamURLTask = new tasks.CallAwsService(this.scope, 'GetServiceParamServiceUrl', {
            comment: 'Get service parameter service-url from SSM Parameter Store',
            iamResources: this.serviceParamUrlListAccess,
            iamAction: 'ssm:GetParameter',
            service: 'ssm',
            action: 'getParameter',
            parameters: {
                Name: `{% '/${this.props.domain}/' & $states.input.service_name  & '/url' %}`
            },
            outputs: "{% $merge([$states.input, { 'service_url': $states.result.Parameter.Value }]) %}",
            queryLanguage: sfn.QueryLanguage.JSONATA
        });

        const loadServicePageTask = new tasks.LambdaInvoke(this.scope, 'LoadServicePage', {
            lambdaFunction: this.props.loadServicePageLambdaFunction,
            outputs: "{% $merge([$states.input, $states.result.Payload]) %}",
            queryLanguage: sfn.QueryLanguage.JSONATA
        });

        const getServiceParamServicePageAnalyzeAlgorithmTask = new tasks.CallAwsService(this.scope, 'GetServiceParamServicePageAnalyzeAlgorithm', {
            comment: 'Get service parameter service-page-analyze-algorithm from SSM Parameter Store',
            iamResources: this.serviceParamPageAnalyzeAlgorithmListAccess,
            iamAction: 'ssm:GetParameter',
            service: 'ssm',
            action: 'getParameter',
            parameters: {
                Name: `{% '/${this.props.domain}/' & $states.input.service_name  & '/page-analyze-algorithm' %}`
            },
            outputs: "{% $merge([$states.input, { 'page_analyze_algorithm': $states.result.Parameter.Value }]) %}",
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
            definitionBody: sfn.DefinitionBody.fromChainable(sfn.Chain.start(getServiceParamURLTask.next(loadServicePageTask.next(getServiceParamServicePageAnalyzeAlgorithmTask)))),
            timeout: cdk.Duration.minutes(5),
            tracingEnabled: true,
            logs: {
                destination: terminRadarCheckStepFunctionLogGroup, includeExecutionData: true, level: sfn.LogLevel.ALL,
            },
        })
    }
}
