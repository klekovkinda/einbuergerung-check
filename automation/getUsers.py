from typing import Any

import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource("dynamodb")


def get_users_for_date(date)-> set[str]:
    table = dynamodb.Table("user_statistic")
    date_ymd_str = date.strftime("%Y-%m-%d")
    response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("date").eq(date_ymd_str))
    return set([item.get('user') for item in response.get('Items', [])])

if __name__ == '__main__':
    today = datetime.now()
    today_users = get_users_for_date(today)
    yesterday_users = get_users_for_date(today - timedelta(days=1))
    day_before_yesterday_users = get_users_for_date(today - timedelta(days=2))
    yesterday_missing_users = yesterday_users - today_users
    yesterday_new_users = yesterday_users - day_before_yesterday_users
    print(yesterday_missing_users, yesterday_new_users)
