from lib.utils import get_dynamodb_table


def add_ddb_termin_records(execution_date_time, appointment_status, available_dates):
    table = get_dynamodb_table("termin_statistic")
    if not available_dates:
        available_dates = ["N/A"]
    with table.batch_writer() as batch:
        for available_date in available_dates:
            item = {
                    'execution_date': execution_date_time.strftime('%Y-%m-%d'),
                    'execution_time': execution_date_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "execution_time_appointment_date": f"{execution_date_time.strftime('%Y-%m-%d %H:%M:%S')} | {available_date}",
                    'status': appointment_status.value,
                    'appointment_date': available_date}
            batch.put_item(Item=item)


def add_ddb_user_records(check_date_time, users):
    table = get_dynamodb_table("user_statistic")
    today = check_date_time.strftime('%Y-%m-%d')
    with table.batch_writer() as batch:
        for user in users:
            item = {'date': today, 'user': user}
            batch.put_item(Item=item)
