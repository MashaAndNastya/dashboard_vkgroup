from datetime import date, timedelta, datetime
import pandas as pd

start_time = int(datetime.strptime(str(date.today() - timedelta(days=7)), "%Y-%m-%d").timestamp())
start_time1 = 1149928032
end_time = str(int(datetime.strptime(str(date.today()), "%Y-%m-%d").timestamp()))
print(start_time, type(start_time))
print(start_time1, type(start_time1))
print(end_time, type(end_time))


# Convert the date to Unix timestamp
unix_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())
print(unix_timestamp)



