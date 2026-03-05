import * as cdk from "aws-cdk-lib";
import * as ssm from 'aws-cdk-lib/aws-ssm';
import {Construct} from "constructs";

export interface TerminRadarInfrastructureStackProperties extends cdk.StackProps {
    prefix: string;
    terminRadarServiceProperties: {
        service_name: string; service_url: string; telegram_chat_id: string;
    }[]
}

export class TerminRadarInfrastructureStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: TerminRadarInfrastructureStackProperties) {
        super(scope, id, props);
        const keys: string[] = ["service_url", "telegram_chat_id"];

        props.terminRadarServiceProperties.forEach(serviceParameter => {
            keys.forEach(propertyKey => {
                new ssm.StringParameter(this, `${serviceParameter.service_name}-${propertyKey}`, {
                    parameterName: `/${props.prefix}/${serviceParameter.service_name}/${propertyKey}`,
                    stringValue: serviceParameter[propertyKey as keyof typeof serviceParameter]
                });
            })
        })
    }
}
