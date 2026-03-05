import * as cdk from "aws-cdk-lib";
import {Duration, Stack} from "aws-cdk-lib";
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as s3 from 'aws-cdk-lib/aws-s3';
import {Construct} from "constructs";
import {IBucket} from "aws-cdk-lib/aws-s3/lib/bucket";

export interface TerminRadarInfrastructureStackProperties extends cdk.StackProps {
    prefix: string;
    terminRadarServiceProperties: {
        service_name: string; service_url: string; telegram_chat_id: string;
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
        const keys: string[] = ["service_url", "telegram_chat_id"];
        props.terminRadarServiceProperties.forEach(serviceParameter => {
            keys.forEach(propertyKey => {
                new ssm.StringParameter(this, `${serviceParameter.service_name}-${propertyKey}`, {
                    parameterName: `/${props.prefix}/${serviceParameter.service_name}/${propertyKey}`,
                    stringValue: serviceParameter[propertyKey as keyof typeof serviceParameter]
                });
            })
        })

        // Create S3 Bucket for short-term data of services
        this.shortTermBucket = new s3.Bucket(this, 'ShortTermBucket', {
            bucketName: `short-term-bucket-${account}-${region}`,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteObjects: true,
            lifecycleRules: [{
                id: 'ExpireObjectsAfter1Day',
                enabled: true,
                expiration: Duration.days(1),
                abortIncompleteMultipartUploadAfter: Duration.days(1),
            }]
        });

        // Create S3 Bucket for long-term data of services
        this.longTermBucket = new s3.Bucket(this, 'LongTermBucket', {
            bucketName: `long-term-bucket-${account}-${region}`,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteObjects: false,
        });
    }
}
