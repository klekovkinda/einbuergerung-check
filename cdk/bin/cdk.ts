#!/usr/bin/env node
import {App} from 'aws-cdk-lib';
import {GhTriggerStack} from '../lib/gh-trigger/gh-trigger-stack';
import {TerminRadarDataStack} from '../lib/termin-radar-data/termin-radar-data-stack';
import {TerminRadarStatisticsStack} from "../lib/termin-radar-statistics/termin-radar-statistics-stack";
import {TerminRadarCheckStack} from "../lib/termin-radar-check/termin-radar-check-stack";
import {Schedule} from "aws-cdk-lib/aws-events/lib/schedule";
import * as events from "aws-cdk-lib/aws-events";
import {TerminRadarInfrastructureStack} from "../lib/termin-radar-infrastructure/termin-radar-infrastructure-stack";
import {pascalize} from "humps";

const app = new App();

export interface TerminRadarServiceProperty {
    serviceName: string;
    serviceUrl: string;
    servicePageAnalyzeAlgorithm: string;
    telegramChatId: string;
    triggerCheckSchedule: Schedule;
    triggerStatisticSchedule: Schedule;
}

const domain = "termin-radar";
const terminRadarServiceProperties: TerminRadarServiceProperty[] = [{
    serviceName: 'einbuergerungstest',
    serviceUrl: 'https://service.berlin.de/terminvereinbarung/termin/all/351180/',
    servicePageAnalyzeAlgorithm: 'service.berlin.de',
    telegramChatId: '@einbuergerungtest_termin_radar',
    triggerCheckSchedule: events.Schedule.cron({
        minute: '0', hour: '11'
    }),
    triggerStatisticSchedule: events.Schedule.cron({
        minute: '0', hour: '11'
    })
}]

const infrastructure = new TerminRadarInfrastructureStack(app, pascalize(`${domain}InfrastructureStack`), {
    domain: domain, terminRadarServiceProperties: terminRadarServiceProperties
});

new GhTriggerStack(app, 'GhTriggerStack', {
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION,
    },
});

new TerminRadarDataStack(app, 'TerminRadarDataStack', {
    //TODO: Replace with dynamic values
    repoOwner: "klekovkinda", repoName: "einbuergerung-check", env: {
        account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION,
    }
});

new TerminRadarStatisticsStack(app, 'TerminRadarStatisticsStack', {});

new TerminRadarCheckStack(app, pascalize(`${domain}CheckStack`), {
    domain: domain,
    terminRadarServiceProperties: terminRadarServiceProperties,
    shortTermBucket: infrastructure.shortTermBucket,
})

