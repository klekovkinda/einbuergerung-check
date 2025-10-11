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
