import csv
import os


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

def add_missing_users(csv_filename, users):
    folder_path = os.path.dirname(csv_filename)
    os.makedirs(folder_path, exist_ok=True)

    existing_users = set()

    if os.path.isfile(csv_filename):
        with open(csv_filename, mode="r", newline="") as csv_file:
            reader = csv.reader(csv_file)
            existing_users = {row[0] for row in reader}

    new_users = [user for user in users if user not in existing_users]

    with open(csv_filename, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        for user in new_users:
            writer.writerow([user])
