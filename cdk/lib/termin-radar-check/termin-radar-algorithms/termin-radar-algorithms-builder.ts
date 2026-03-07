import {IFunction} from "aws-cdk-lib/aws-lambda/lib/function-base";
import * as lambda from 'aws-cdk-lib/aws-lambda';
import {AssetCode} from 'aws-cdk-lib/aws-lambda';
import * as cdk from 'aws-cdk-lib';
import {Duration} from 'aws-cdk-lib';
import path from "path";
import {Construct} from "constructs";
import {IBucket} from "aws-cdk-lib/aws-s3/lib/bucket";

export class TerminRadarAlgorithmsBuilder {
    constructor(private scope: Construct, private domain: string, private serviceNames: string[], private shortTermBucket: IBucket) {
    }

    public build(): Map<string, IFunction> {
        const lambdaRuntime = lambda.Runtime.PYTHON_3_13;
        const lambdaArchitecture = lambda.Architecture.ARM_64;
        const powertoolsLayer = lambda.LayerVersion.fromLayerVersionArn(this.scope, 'PowertoolsLayer', `arn:aws:lambda:${process.env.CDK_DEFAULT_REGION}:017000801446:layer:AWSLambdaPowertoolsPythonV3-python313-arm64:23`,);
        const sourcePath = path.join(__dirname, 'lambda');
        const lambdaCode = this.createLambdaAsset(this.scope, sourcePath);

        //service.berlin.de algorithm lambda function
        const algorithmServiceBerlinDeLambdaFunctionName = `${this.domain}-algorithm-service-berlin-de-lambda-function`;

        const algorithmServiceBerlinDeLambdaFunction = new lambda.Function(this.scope, 'AlgorithmServiceBerlinDeLambdaFunction', {
            functionName: algorithmServiceBerlinDeLambdaFunctionName,
            description: 'Lambda function for TerminRadar algorithms to process data from service.berlin.de',
            runtime: lambdaRuntime,
            handler: 'index.service_berlin_de',
            code: lambdaCode,
            memorySize: 128,
            architecture: lambdaArchitecture,
            timeout: Duration.seconds(5),
            environment: {
                POWERTOOLS_SERVICE_NAME: `${this.domain}-algorithm-service-berlin-de-lambda-function`,
                POWERTOOLS_LOG_LEVEL: 'DEBUG',
            },
            tracing: lambda.Tracing.ACTIVE,
            layers: [powertoolsLayer]
        });

        const s3BucketResources = this.serviceNames.map(serviceName => `${this.shortTermBucket.bucketArn}/${serviceName}/*`);
        algorithmServiceBerlinDeLambdaFunction.addToRolePolicy(new cdk.aws_iam.PolicyStatement({
            actions: ['s3:GetObject'],
            resources: s3BucketResources
        }));

        const algorithmsMap = new Map<string, IFunction>();
        algorithmsMap.set("service.berlin.de", algorithmServiceBerlinDeLambdaFunction);
        return algorithmsMap;
    }

    private createLambdaAsset = (scope: Construct, source_path: string): AssetCode => {
        return lambda.Code.fromAsset(source_path, {
            exclude: ['*', '.*', `!*.py`], ignoreMode: cdk.IgnoreMode.GLOB,
        });
    };
}
