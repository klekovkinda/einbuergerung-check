import unittest
from datetime import datetime

import boto3
from moto import mock_aws

from lib.collect_statistics import add_ddb_termin_records, add_ddb_user_records
from lib.status_check import CheckStatus


@mock_aws
class TestCollectStatistics(unittest.TestCase):

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

    def test_add_ddb_termin_records_with_dates(self):
        execution_date_time = datetime(2024, 6, 1, 12, 0, 0)
        status = CheckStatus.APPOINTMENTS_AVAILABLE
        available_dates = ["2024-06-10", "2024-06-11"]

        add_ddb_termin_records(execution_date_time, status, available_dates)

        items = boto3.resource("dynamodb").Table('termin_statistic').scan()['Items']
        self.assertEqual(len(items), 2)

        self.assertIn({
                'appointment_date': '2024-06-10',
                'execution_date': '2024-06-01',
                'execution_time': '2024-06-01 12:00:00',
                'execution_time_appointment_date': '2024-06-01 12:00:00 | 2024-06-10',
                'status': 'Appointments Available'}, items)
        self.assertIn({
                'appointment_date': '2024-06-11',
                'execution_date': '2024-06-01',
                'execution_time': '2024-06-01 12:00:00',
                'execution_time_appointment_date': '2024-06-01 12:00:00 | 2024-06-11',
                'status': 'Appointments Available'}, items)

    def test_add_ddb_termin_records_no_dates(self):
        execution_date_time = datetime(2024, 6, 1, 12, 0, 0)
        status = CheckStatus.NO_APPOINTMENTS

        add_ddb_termin_records(execution_date_time, status, [])

        items = boto3.resource("dynamodb").Table('termin_statistic').scan()['Items']
        self.assertEqual(len(items), 1)
        self.assertIn({
                'appointment_date': 'N/A',
                'execution_date': '2024-06-01',
                'execution_time': '2024-06-01 12:00:00',
                'execution_time_appointment_date': '2024-06-01 12:00:00 | N/A',
                'status': 'No Appointments'}, items)

    def test_add_ddb_user_records(self):
        dt = datetime(2024, 6, 1, 12, 0, 0)
        users = ["alice", "bob"]

        add_ddb_user_records(dt, users)

        items = boto3.resource("dynamodb").Table('user_statistic').scan()['Items']
        self.assertIn({"date": "2024-06-01", "user": "alice"}, items)
        self.assertIn({"date": "2024-06-01", "user": "bob"}, items)


if __name__ == "__main__":
    unittest.main()
