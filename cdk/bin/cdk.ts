#!/usr/bin/env node
import {App} from 'aws-cdk-lib';
import {GhTriggerStack} from '../lib/gh-trigger/gh-trigger-stack';
import {TerminRadarDataStack} from '../lib/termin-radar-data/termin-radar-data-stack';
import {TerminRadarStatisticsStack} from "../lib/termin-radar-statistics/termin-radar-statistics-stack";
import {TerminRadarCheckStack} from "../lib/termin-radar-check/termin-radar-check-stack";
import {Schedule} from "aws-cdk-lib/aws-events/lib/schedule";
import * as events from "aws-cdk-lib/aws-events";
import {TerminRadarPropertyStack} from "../lib/termin-radar-property/termin-radar-property-stack";

const app = new App();

export interface TerminRadarServiceProperty {
    service_name: string;
    service_url: string;
    telegram_chat_id: string;
    trigger_check_schedule: Schedule;
    trigger_statistic_schedule: Schedule;
}

const propertyPrefix = "TerminRadar";
const terminRadarServiceProperties: TerminRadarServiceProperty[] = [{
    service_name: 'EinbuergerungtestTerminRadar',
    service_url: 'https://service.berlin.de/terminvereinbarung/termin/all/351180/',
    telegram_chat_id: '@einbuergerungtest_termin_radar',
    trigger_check_schedule: events.Schedule.cron({
        minute: '0', hour: '11'
    }),
    trigger_statistic_schedule: events.Schedule.cron({
        minute: '0', hour: '11'
    })
}]

new GhTriggerStack(app, 'GhTriggerStack', {
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION,
    },
});

new TerminRadarPropertyStack(app, 'TerminRadarPropertyStack', {
    prefix: propertyPrefix, terminRadarServiceProperties: terminRadarServiceProperties
});

new TerminRadarDataStack(app, 'TerminRadarDataStack', {
    //TODO: Replace with dynamic values
    repoOwner: "klekovkinda", repoName: "einbuergerung-check", env: {
        account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION,
    }
});

new TerminRadarStatisticsStack(app, 'TerminRadarStatisticsStack', {});

new TerminRadarCheckStack(app, 'TerminRadarCheckStack', {
    propertyPrefix:propertyPrefix,
    terminRadarServiceProperties: terminRadarServiceProperties
})

