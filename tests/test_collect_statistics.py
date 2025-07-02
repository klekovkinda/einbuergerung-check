import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from lib.collect_statistics import add_ddb_termin_records, add_ddb_user_records
from lib.status_check import CheckStatus


class TestCollectStatistics(unittest.TestCase):
    @patch("lib.collect_statistics.dynamodb")
    def test_add_ddb_termin_records_with_dates(self, mock_dynamodb):
        mock_table = MagicMock()
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value.__enter__.return_value = mock_batch_writer
        mock_dynamodb.Table.return_value = mock_table

        execution_date_time = datetime(2024, 6, 1, 12, 0, 0)
        status = CheckStatus.APPOINTMENTS_AVAILABLE
        available_dates = ["2024-06-10", "2024-06-11"]

        add_ddb_termin_records(execution_date_time, status, available_dates)

        self.assertEqual(mock_batch_writer.put_item.call_count, 2)
        items = [call[1]["Item"] for call in mock_batch_writer.put_item.call_args_list]
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

    @patch("lib.collect_statistics.dynamodb")
    def test_add_ddb_termin_records_no_dates(self, mock_dynamodb):
        mock_table = MagicMock()
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value.__enter__.return_value = mock_batch_writer
        mock_dynamodb.Table.return_value = mock_table

        execution_date_time = datetime(2024, 6, 1, 12, 0, 0)
        status = CheckStatus.NO_APPOINTMENTS

        add_ddb_termin_records(execution_date_time, status, [])

        mock_batch_writer.put_item.assert_called_once()
        items = [call[1]["Item"] for call in mock_batch_writer.put_item.call_args_list]
        self.assertIn({
                'appointment_date': 'N/A',
                'execution_date': '2024-06-01',
                'execution_time': '2024-06-01 12:00:00',
                'execution_time_appointment_date': '2024-06-01 12:00:00 | N/A',
                'status': 'No Appointments'}, items)

    @patch("lib.collect_statistics.dynamodb")
    def test_add_ddb_user_records(self, mock_dynamodb):
        mock_table = MagicMock()
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value.__enter__.return_value = mock_batch_writer
        mock_dynamodb.Table.return_value = mock_table
        dt = datetime(2024, 6, 1, 12, 0, 0)
        users = ["alice", "bob"]

        add_ddb_user_records(dt, users)

        self.assertEqual(mock_batch_writer.put_item.call_count, 2)
        items = [call[1]["Item"] for call in mock_batch_writer.put_item.call_args_list]
        self.assertIn({"date": "2024-06-01", "user": "alice"}, items)
        self.assertIn({"date": "2024-06-01", "user": "bob"}, items)


if __name__ == "__main__":
    unittest.main()
