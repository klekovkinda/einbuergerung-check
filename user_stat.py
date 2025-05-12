from lib.collect_statistics import add_missing_users
from lib.get_channel_members import get_channel_members
from datetime import datetime

date_time_now = datetime.now()
csv_user_filename = f"output/statistics/user_{date_time_now.strftime('%Y%m%d')}.csv"
add_missing_users(csv_user_filename, get_channel_members("@einbuergerungtest_termin_radar"))
