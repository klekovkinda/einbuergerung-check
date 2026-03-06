import * as cdk from "aws-cdk-lib";
import {Duration, Stack} from "aws-cdk-lib";
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as s3 from 'aws-cdk-lib/aws-s3';
import {Construct} from "constructs";
import {IBucket} from "aws-cdk-lib/aws-s3/lib/bucket";
import {camelize, pascalize} from "humps";

export interface TerminRadarInfrastructureStackProperties extends cdk.StackProps {
    domain: string;
    terminRadarServiceProperties: {
        serviceName: string; serviceUrl: string; telegramChatId: string;
    }[]
}

export class TerminRadarInfrastructureStack extends cdk.Stack {
    public readonly shortTermBucket: IBucket;
    public readonly longTermBucket: IBucket;

    constructor(scope: Construct, id: string, props: TerminRadarInfrastructureStackProperties) {
        super(scope, id, props);

        const account = Stack.of(this).account;
        const region = Stack.of(this).region;

        // Create SSM parameters for each service
        const keys: string[] = ["service-url", "telegram-chat-id"];
        props.terminRadarServiceProperties.forEach(serviceParameter => {
            keys.forEach(propertyKey => {
                new ssm.StringParameter(this, pascalize(`${serviceParameter.serviceName}-property-${propertyKey}`), {
                    parameterName: `/${props.domain}/${serviceParameter.serviceName}/${propertyKey}`,
                    stringValue: serviceParameter[camelize(propertyKey) as keyof typeof serviceParameter]
                });
            })
        })

        // Create S3 Bucket for short-term data of services
        this.shortTermBucket = new s3.Bucket(this, 'ShortTermBucket', {
            bucketName: `${props.domain}-short-term-bucket-${account}-${region}`,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteObjects: true,
            lifecycleRules: [{
                id: 'expire-objects-after-1-day',
                enabled: true,
                expiration: Duration.days(1),
                abortIncompleteMultipartUploadAfter: Duration.days(1),
            }]
        });

        // Create S3 Bucket for long-term data of services
        this.longTermBucket = new s3.Bucket(this, 'LongTermBucket', {
            bucketName: `${props.domain}-long-term-bucket-${account}-${region}`,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteObjects: false,
        });
    }
}
