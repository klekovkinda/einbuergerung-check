import csv
import os
import unittest

from lib.collect_statistics import add_record
from lib.status_check import CheckStatus


class TestAddRecord(unittest.TestCase):
    def setUp(self):
        self.test_csv = "test_output/test_file.csv"
        self.available_dates = ["2023-10-10", "2023-10-15"]

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        if os.path.exists(os.path.dirname(self.test_csv)):
            os.rmdir(os.path.dirname(self.test_csv))

    def test_add_record_with_dates(self):
        execution_time = "2023-10-01 12:00:00"
        add_record(self.test_csv, execution_time, CheckStatus.APPOINTMENTS_AVAILABLE, self.available_dates)

        with open(self.test_csv, mode="r") as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)

        self.assertEqual(rows[0], ["execution_time", "status", "appointmentdate"])
        self.assertEqual(rows[1], [execution_time, CheckStatus.APPOINTMENTS_AVAILABLE.value, "2023-10-10"])
        self.assertEqual(rows[2], [execution_time, CheckStatus.APPOINTMENTS_AVAILABLE.value, "2023-10-15"])

    def test_add_record_without_dates(self):
        execution_time = "2023-10-01 12:00:01"
        add_record(self.test_csv, execution_time, CheckStatus.NO_APPOINTMENTS, [])

        with open(self.test_csv, mode="r") as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)

        self.assertEqual(rows[0], ["execution_time", "status", "appointmentdate"])
        self.assertEqual(rows[1], [execution_time, CheckStatus.NO_APPOINTMENTS.value, "N/A"])


    def test_add_many_records(self):
        execution_time_0 = "2023-10-01 12:00:00"
        execution_time_1 = "2023-10-01 12:00:01"
        add_record(self.test_csv, execution_time_0, CheckStatus.NO_APPOINTMENTS, [])
        add_record(self.test_csv, execution_time_1, CheckStatus.NO_APPOINTMENTS, [])

        with open(self.test_csv, mode="r") as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)

        self.assertEqual(rows[0], ["execution_time", "status", "appointmentdate"])
        self.assertEqual(rows[1], [execution_time_0, CheckStatus.NO_APPOINTMENTS.value, "N/A"])
        self.assertEqual(rows[2], [execution_time_1, CheckStatus.NO_APPOINTMENTS.value, "N/A"])


if __name__ == "__main__":
    unittest.main()
