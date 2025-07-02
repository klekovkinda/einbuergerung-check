import boto3

dynamodb = boto3.resource('dynamodb')


def add_ddb_termin_records(execution_date_time, appointment_status, available_dates):
    table = dynamodb.Table("termin_statistic")
    if not available_dates:
        available_dates = ["N/A"]
    for available_date in available_dates:
        item = {
                'execution_date': execution_date_time.strftime('%Y-%m-%d'),
                'execution_time': execution_date_time.strftime('%Y-%m-%d %H:%M:%S'),
                "execution_time_appointment_date": f"{execution_date_time.strftime('%Y-%m-%d %H:%M:%S')} | {available_date}",
                'status': appointment_status.value,
                'appointment_date': available_date}
        table.put_item(Item=item)


def add_ddb_user_records(check_date_time, users):
    table = dynamodb.Table("user_statistic")
    today = check_date_time.strftime('%Y-%m-%d')
    with table.batch_writer() as batch:
        for user in users:
            item = {'date': today, 'user': user}
            batch.put_item(Item=item)
