import unittest
from datetime import datetime, timedelta

import boto3
from moto import mock_aws

from read_yesterday_stats import read_yesterday_user_stats, read_yesterday_execution_stats


@mock_aws
class TestReadYesterdayStatistics(unittest.TestCase):
    def setUp(self):
        dynamodb = boto3.resource("dynamodb")
        dynamodb.create_table(TableName='termin_statistic',
                              BillingMode='PAY_PER_REQUEST',
                              KeySchema=[{'AttributeName': 'execution_date', 'KeyType': 'HASH'},
                                         {'AttributeName': 'execution_time_appointment_date', 'KeyType': 'RANGE'}],
                              AttributeDefinitions=[{'AttributeName': 'execution_date', 'AttributeType': 'S'},
                                                    {
                                                            'AttributeName': 'execution_time_appointment_date',
                                                            'AttributeType': 'S'}])
        dynamodb.create_table(TableName='user_statistic',
                              BillingMode='PAY_PER_REQUEST',
                              KeySchema=[{'AttributeName': 'date', 'KeyType': 'HASH'},
                                         {'AttributeName': 'user', 'KeyType': 'RANGE'}],
                              AttributeDefinitions=[{'AttributeName': 'date', 'AttributeType': 'S'},
                                                    {'AttributeName': 'user', 'AttributeType': 'S'}])

    def test_read_yesterday_user_stats(self):
        dynamodb = boto3.resource("dynamodb")
        user_table = dynamodb.Table("user_statistic")
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        day_before_yesterday = today - timedelta(days=2)

        user_table.put_item(Item={'date': today.strftime("%Y-%m-%d"), 'user': 'user4'})
        user_table.put_item(Item={'date': today.strftime("%Y-%m-%d"), 'user': 'user3'})
        user_table.put_item(Item={'date': yesterday.strftime("%Y-%m-%d"), 'user': 'user3'})
        user_table.put_item(Item={'date': yesterday.strftime("%Y-%m-%d"), 'user': 'user2'})
        user_table.put_item(Item={'date': day_before_yesterday.strftime("%Y-%m-%d"), 'user': 'user2'})
        user_table.put_item(Item={'date': day_before_yesterday.strftime("%Y-%m-%d"), 'user': 'user1'})

        new_users, missing_users = read_yesterday_user_stats()
        self.assertEqual(new_users, 1)
        self.assertEqual(missing_users, 1)

    def test_read_yesterday_execution_stats(self):
        dynamodb = boto3.resource("dynamodb")
        termin_table = dynamodb.Table("termin_statistic")
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = (datetime.now()).strftime('%Y-%m-%d')

        termin_table.put_item(Item={
            'execution_date': yesterday,
            'execution_time_appointment_date': f"{yesterday} 12:00:00 | 2024-06-10",
            'execution_time': f"{yesterday} 12:00:00",
            'status': 'Appointments Available',
            'appointment_date': '2024-06-10'
        })
        termin_table.put_item(Item={
            'execution_date': yesterday,
            'execution_time_appointment_date': f"{yesterday} 12:00:00 | 2024-06-11",
            'execution_time': f"{yesterday} 12:00:00",
            'status': 'Appointments Available',
            'appointment_date': '2024-06-11'
        })
        termin_table.put_item(Item={
                'execution_date': yesterday,
                'execution_time_appointment_date': f"{yesterday} 12:02:00 | N/A",
                'execution_time': f"{yesterday} 12:02:00",
                'status': 'No Appointments',
                'appointment_date': 'N/A'
        })
        termin_table.put_item(Item={
                'execution_date': today,
                'execution_time_appointment_date': f"{today} 12:04:00 | N/A",
                'execution_time': f"{today} 12:04:00",
                'status': 'No Appointments',
                'appointment_date': 'N/A'
        })

        start_at, finish_at, execution_times, successful_notifications, available_dates, failed_requests = read_yesterday_execution_stats()
        self.assertEqual(execution_times, 2)
        self.assertEqual(successful_notifications, 1)
        self.assertEqual(available_dates, 2)
        self.assertEqual(failed_requests, 0)


if __name__ == "__main__":
    unittest.main()
