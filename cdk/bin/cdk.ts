#!/usr/bin/env node
import {App} from 'aws-cdk-lib';
import {GhTriggerStack} from '../lib/gh-trigger/gh-trigger-stack';
import {TerminRadarDataStack} from '../lib/termin-radar-data/termin-radar-data-stack';
import {TerminRadarStatisticsStack} from "../lib/termin-radar-statistics/termin-radar-statistics-stack";

const app = new App();

new GhTriggerStack(app, 'GhTriggerStack', {
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.CDK_DEFAULT_REGION,
    },
});

new TerminRadarDataStack(app, 'TerminRadarDataStack', {
    //TODO: Replace with dynamic values
    repoOwner: "klekovkinda",
    repoName: "einbuergerung-check",
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.CDK_DEFAULT_REGION,
    }
});

new TerminRadarStatisticsStack(app, 'TerminRadarStatisticsStack', {});

