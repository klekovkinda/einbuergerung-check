import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import {IStateMachine} from "aws-cdk-lib/aws-stepfunctions/lib/state-machine";
import * as logs from "aws-cdk-lib/aws-logs";
import * as cdk from "aws-cdk-lib";
import {Stack} from "aws-cdk-lib";
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import {IFunction} from "aws-cdk-lib/aws-lambda/lib/function-base";
import {pascalize} from "humps";


export interface TerminRadarCheckStepFunctionBuilderProperties {
    domain: string;
    serviceNames: string[];
    loadServicePageLambdaFunction: IFunction;
    algorithmsFunctions: Map<string, IFunction>;
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
            stateName: 'GetServiceParamServiceUrl',
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
            stateName: 'LoadServicePage',
            comment: 'Call Lambda function to load service page and store content into S3 bucket',
            lambdaFunction: this.props.loadServicePageLambdaFunction,
            outputs: "{% $merge([$states.input, $states.result.Payload]) %}",
            queryLanguage: sfn.QueryLanguage.JSONATA
        });

        const getServiceParamServicePageAnalyzeAlgorithmTask = new tasks.CallAwsService(this.scope, 'GetServiceParamServicePageAnalyzeAlgorithm', {
            stateName: "GetServiceParamServicePageAnalyzeAlgorithm",
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

        const algorithmNotSupported = new sfn.Fail(this.scope, 'AlgorithmNotSupported', {
            error: "AlgorithmNotSupported",
            cause: "The page analyze algorithm is not supported or failed to get from SSM Parameter Store"
        });

        const choiceServicePageAnalyzeAlgorithm = new sfn.Choice(this.scope, 'ChoiceServicePageAnalyzeAlgorithm', {
            comment: 'Coose page analyze algorithm based on service parameter',
            stateName: 'ChoiceServicePageAnalyzeAlgorithm',
            queryLanguage: sfn.QueryLanguage.JSONATA
        })
            .otherwise(algorithmNotSupported);

        for (const algorithm of this.props.algorithmsFunctions.keys()) {
            const algorithmLambdaFunction = this.props.algorithmsFunctions.get(algorithm)!;
            const algorithmTask = new tasks.LambdaInvoke(this.scope, pascalize(algorithmLambdaFunction.functionName), {
                stateName: pascalize(algorithmLambdaFunction.functionName),
                comment: 'Call Lambda function to load service page and store content into S3 bucket',
                lambdaFunction: algorithmLambdaFunction,
                outputs: "{% $merge([$states.input, $states.result.Payload]) %}",
                queryLanguage: sfn.QueryLanguage.JSONATA
            });
            choiceServicePageAnalyzeAlgorithm.when(sfn.Condition.jsonata(`{% $states.input.page_analyze_algorithm in "${algorithm}" %}`), algorithmTask)
        }


        const terminRadarCheckStepFunctionLogGroup = new logs.LogGroup(this.scope, pascalize(`${this.props.domain}CheckStepFunctionLogGroup`), {
            logGroupName: `/aws/stateMachine/${this.stateMachineName}`,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            retention: logs.RetentionDays.FIVE_DAYS,
        });

        return new sfn.StateMachine(this.scope, 'CheckStepFunction', {
            stateMachineName: `${this.props.domain}-check-step-function`,
            definitionBody: sfn.DefinitionBody.fromChainable(sfn.Chain.start(getServiceParamURLTask.next(loadServicePageTask.next(getServiceParamServicePageAnalyzeAlgorithmTask.next(choiceServicePageAnalyzeAlgorithm))))),
            timeout: cdk.Duration.minutes(5),
            tracingEnabled: true,
            logs: {
                destination: terminRadarCheckStepFunctionLogGroup, includeExecutionData: true, level: sfn.LogLevel.ALL,
            },
        })
    }
}
