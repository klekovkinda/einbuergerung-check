import csv
import os
from enum import Enum
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')


class UserStatus(Enum):
    NEW = "new"
    OLD = "old"


def add_ddb_termin_records(table, execution_date_time, appointment_status, available_dates):
    table = dynamodb.Table(table)
    try:
        for available_date in available_dates:
            item = {'execution_date': execution_date_time.strftime('%Y-%m-%d'),
                    'execution_time': execution_date_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "execution_time_appointment_date": f"{execution_date_time.strftime('%Y-%m-%d %H:%M:%S')} | {available_date}",
                    'status': appointment_status.value,
                    'appointment_date': available_date}
            table.put_item(Item=item)
        if not available_dates:
            item = {'execution_date': execution_date_time.strftime('%Y-%m-%d'),
                    'execution_time': execution_date_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "execution_time_appointment_date": f"{execution_date_time.strftime('%Y-%m-%d %H:%M:%S')} | N/A",
                    'status': appointment_status.value,
                    'appointment_date': "N/A"}
            table.put_item(Item=item)
    except ClientError as e:
        print(f"Error adding record to DynamoDB: {e.response['Error']['Message']}")


def add_record(csv_filename, execution_time, appointment_status, available_dates):
    folder_path = os.path.dirname(csv_filename)
    os.makedirs(folder_path, exist_ok=True)
    csv_header = ["execution_time", "status", "appointmentdate"]

    csv_rows = []

    for available_date in available_dates:
        csv_row = [execution_time, appointment_status.value, available_date]
        csv_rows.append(csv_row)
    if not available_dates:
        csv_row = [execution_time, appointment_status.value, available_dates or "N/A"]
        csv_rows.append(csv_row)

    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(csv_header)
        for row in csv_rows:
            writer.writerow(row)


def add_ddb_user_records(table, check_date_time, users):
    table = dynamodb.Table(table)
    today = check_date_time.strftime('%Y-%m-%d')
    with table.batch_writer() as batch:
        for user in users:
            item = {'date': today, 'user': user}
            batch.put_item(Item=item)


def add_missing_users(csv_filename, users):
    folder_path = os.path.dirname(csv_filename)
    os.makedirs(folder_path, exist_ok=True)

    existing_users = set()

    if os.path.isfile(csv_filename):
        with open(csv_filename, mode="r", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            existing_users = {row["user"] for row in reader}

    new_users = [user for user in users if user not in existing_users]

    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(["user", "status"])  # Write header
            for user in new_users:
                writer.writerow([user, UserStatus.OLD.value])
        else:
            for user in new_users:
                writer.writerow([user, UserStatus.NEW.value])
