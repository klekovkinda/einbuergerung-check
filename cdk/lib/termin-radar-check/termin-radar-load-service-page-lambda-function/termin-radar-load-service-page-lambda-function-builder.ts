import * as cdk from "aws-cdk-lib";
import {aws_iam} from "aws-cdk-lib";
import {Construct} from "constructs";
import {IBucket} from "aws-cdk-lib/aws-s3/lib/bucket";
import {Architecture, DockerImageCode, DockerImageFunction} from "aws-cdk-lib/aws-lambda";
import path from "path";
import {IFunction} from "aws-cdk-lib/aws-lambda/lib/function-base";
import * as logs from "aws-cdk-lib/aws-logs";


export interface TerminRadarLoadServicePageLambdaFunctionBuilderProperties {
    domain: string,
    serviceNames: string[],
    shortTermBucket: IBucket
}

export class TerminRadarLoadServicePageLambdaFunctionBuilder {

    constructor(private scope: Construct, private props: TerminRadarLoadServicePageLambdaFunctionBuilderProperties) {
    }

    public build(): IFunction {
        const lambdaDir = path.join(__dirname, 'lambda');

        const lambdaName = `${this.props.domain}-load-service-page-lambda-function`

        const loadServicePageLambdaFunction = new DockerImageFunction(this.scope, 'LoadServicePageLambdaFunction', {
            functionName: lambdaName,
            description: "Lambda function that load the page and store content into S3 bucket",
            code: DockerImageCode.fromImageAsset(lambdaDir),
            memorySize: 1024,
            timeout: cdk.Duration.seconds(60),
            architecture: Architecture.X86_64,
            environment: {
                S3_SHORT_TERM_BUCKET_NAME: this.props.shortTermBucket.bucketName,
                POWERTOOLS_SERVICE_NAME: `${this.props.domain}-load-service-page-lambda-function`,
                POWERTOOLS_LOG_LEVEL: 'DEBUG'
            }
        });

        //Add policy to write to S3 bucket by service
        loadServicePageLambdaFunction.addToRolePolicy(new aws_iam.PolicyStatement({
            actions: ['s3:PutObject'],
            resources: this.props.serviceNames.map(serviceName => `${this.props.shortTermBucket.bucketArn}/${serviceName}/*`)
        }));

        return loadServicePageLambdaFunction;
    }
}
