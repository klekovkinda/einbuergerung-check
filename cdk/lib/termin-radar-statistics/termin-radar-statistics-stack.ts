import * as cdk from "aws-cdk-lib";
import {Construct} from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import path from "path";
import * as iam from "aws-cdk-lib/aws-iam";
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";
import {addDefaultTags} from "../utils";

export interface TerminRadarStatisticsStackProperties extends cdk.StackProps {
}

export class TerminRadarStatisticsStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: TerminRadarStatisticsStackProperties) {
        super(scope, id, props);

        const promotionMessageParameterName = '/TerminRadar/PromotionMessage';
        const telegramChatIdParameterName = '/TerminRadar/TelegramChatId';
        const telegramBotTokenParameterName = '/TerminRadar/TelegramBotToken';

        const regionPrefix = "eu";
        const bedRockModelId = 'amazon.nova-micro-v1:0';
        const inferenceProfileId = `${regionPrefix}.${bedRockModelId}`;

        const terminRadarStatisticsFunction = new lambda.Function(this, `${id}Lambda`, {
            functionName: 'TerminRadarStatisticsFunction',
            description: "Lambda function that extracts statistics from the termin-radar repository and sends them to a Telegram channel",
            runtime: lambda.Runtime.PYTHON_3_13,
            timeout: cdk.Duration.seconds(30),
            handler: 'index.handler',
            code: lambda.Code.fromAsset(path.join(__dirname, 'lambda'), {
                bundling: {
                    image: lambda.Runtime.PYTHON_3_13.bundlingImage,
                    command: ['bash', '-c', 'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'],
                },
            }),
            environment: {
                INFERENCE_PROFILE_ID: inferenceProfileId,
                SUPPORT_URL: "https://buymeacoffee.com/termin_radar",
                PAYPAL_SUPPORT_URL: "https://www.paypal.com/pool/9f1bWcE4aK?sr=wccr",
                PROMOTION_MESSAGE_PARAMETER_NAME: promotionMessageParameterName,
                TELEGRAM_CHAT_ID_PARAMETER_NAME: telegramChatIdParameterName,
                TELEGRAM_BOT_TOKEN_PARAMETER_NAME: telegramBotTokenParameterName
            },
        });

        //Add policy to read SSM parameters
        terminRadarStatisticsFunction.addToRolePolicy(new iam.PolicyStatement({
            actions: ['ssm:GetParameter'],
            resources: [
                `arn:aws:ssm:${this.region}:${this.account}:parameter${promotionMessageParameterName}`,
                `arn:aws:ssm:${this.region}:${this.account}:parameter${telegramChatIdParameterName}`,
                `arn:aws:ssm:${this.region}:${this.account}:parameter${telegramBotTokenParameterName}`]
        }));

        //Add policy to access DynamoDB tables [termin_statistic, user_statistic]
        terminRadarStatisticsFunction.addToRolePolicy(new iam.PolicyStatement({
            actions: ['dynamodb:Query'],
            resources: [
                `arn:aws:dynamodb:${this.region}:${this.account}:table/termin_statistic`,
                `arn:aws:dynamodb:${this.region}:${this.account}:table/user_statistic`]
        }));

        //Add policy to access Bedrock model
        terminRadarStatisticsFunction.addToRolePolicy(new iam.PolicyStatement({
            actions: ['bedrock:InvokeModel'],
            resources: [
                `arn:aws:bedrock:${this.region}:${this.account}:inference-profile/${inferenceProfileId}`,
                `arn:aws:bedrock:${regionPrefix}-*::foundation-model/${bedRockModelId}`
            ]
        }));

        new events.Rule(this, `${id}Rule`, {
            ruleName: `Trigger${terminRadarStatisticsFunction.functionName}Rule`,
            schedule: events.Schedule.cron({
                minute: '0',
                hour: '10'
            }),
            targets: [new targets.LambdaFunction(terminRadarStatisticsFunction)],
        });
        addDefaultTags(this);
    }
}
