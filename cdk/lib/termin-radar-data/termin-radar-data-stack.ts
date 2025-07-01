import * as cdk from "aws-cdk-lib";
import * as iam from "aws-cdk-lib/aws-iam";
import {Construct} from "constructs";

export interface TerminRadarDataStackProperties extends cdk.StackProps {
    repoOwner: string;
    repoName: string;
}

export class TerminRadarDataStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: TerminRadarDataStackProperties) {
        super(scope, id, props);

        const terminStatisticDynamoTable = new cdk.aws_dynamodb.Table(this, `${id}TerminStatisticDynamoTable`, {
            tableName: "termin_statistic",
            partitionKey: {
                name: "execution_date",
                type: cdk.aws_dynamodb.AttributeType.STRING
            },
            sortKey: {
                name: "hash",
                type: cdk.aws_dynamodb.AttributeType.STRING
            },
            billingMode: cdk.aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removalPolicy: cdk.RemovalPolicy.DESTROY
        });

        const userStatisticDynamoTable = new cdk.aws_dynamodb.Table(this, `${id}UserStatisticDynamoTable`, {
            tableName: "user_statistic",
            partitionKey: {
                name: "date",
                type: cdk.aws_dynamodb.AttributeType.STRING
            },
            sortKey: {
                name: "user",
                type: cdk.aws_dynamodb.AttributeType.STRING
            },
            billingMode: cdk.aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removalPolicy: cdk.RemovalPolicy.DESTROY
        });

        const oidcProvider = new iam.OpenIdConnectProvider(this, `${id}GitHubOIDCProvider`, {
            url: "https://token.actions.githubusercontent.com",
            clientIds: ["sts.amazonaws.com"],
        });

        const gitHubActionTerminRadarDataRole = new iam.Role(this, `${id}GitHubActionTerminRadarDataRole`, {
            roleName: "gitHubActionTerminRadarDataRole",
            assumedBy: new iam.WebIdentityPrincipal(oidcProvider.openIdConnectProviderArn, {
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": `repo:${props.repoOwner}/${props.repoName}:*`
                }
            }),
        });

        terminStatisticDynamoTable.grantReadWriteData(gitHubActionTerminRadarDataRole);
        userStatisticDynamoTable.grantReadWriteData(gitHubActionTerminRadarDataRole);
    }
}
