import csv
import glob

import boto3

TABLE_NAME = "termin_statistic"
CSV_GLOB = "output/statistics/stat_*.csv"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def parse_csv_and_insert(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        with table.batch_writer() as batch:
            for row in reader:
                execution_time = row["execution_time"]
                execution_date = execution_time.split(" ")[0]
                appointment_date = row["appointmentdate"]

                item = {"execution_date": execution_date,
                        "execution_time": execution_time,
                        "execution_time_appointment_date": f"{execution_time} | {appointment_date}",
                        "status": row["status"],
                        "appointment_date": appointment_date}
                #print(item)
                #batch.put_item(Item=item)


def main():
    csv_files = glob.glob(CSV_GLOB)
    print(f"Found {len(csv_files)} CSV files.")
    for csv_file in csv_files:
        print(f"Importing {csv_file}...")
        parse_csv_and_insert(csv_file)
    print("Import complete.")


if __name__ == "__main__":
    main()
