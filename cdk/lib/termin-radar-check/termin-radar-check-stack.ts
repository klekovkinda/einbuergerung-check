import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import {Architecture, DockerImageCode, DockerImageFunction} from "aws-cdk-lib/aws-lambda";
import path from "path";

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
            architecture: Architecture.X86_64
        });
    };

}
