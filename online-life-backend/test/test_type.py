from datetime import datetime, timedelta

timestamp = int(datetime.now().timestamp() * 1000000)
print(len(str(2000000000000000000 + timestamp)))
print(str(2000000000000000000 + timestamp))

bid_deadline = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
print(len(bid_deadline))
print(bid_deadline)
