import * as cdk from 'aws-cdk-lib';
import {Construct} from "constructs";

export const defaultTags = new Map<string, string>([
    ['klekovkinda:project', 'TerminRadar']
]);

export const addDefaultTags = (scope: Construct) => {
    defaultTags.forEach((value, key) => {
        cdk.Tags.of(scope).add(key, value);
    });
};

export const getPowertoolsLayer = (scope: Construct) => {
    return cdk.aws_lambda.LayerVersion.fromLayerVersionArn(scope, 'PowertoolsLayer', `arn:aws:lambda:${cdk.Stack.of(scope).region}:017000801446:layer:AWSLambdaPowertoolsPythonV3-python313-arm64:23`);
}
