# oscar_schedule package

This module can calculate the number of expected observations in a given time period based on one or more schedules. It is used by the WIGOS Data Quality Monitoring System to calculate the number of expected observations in NWP assimilation intervals.

Use this package like this:
```python
from oscar_schedules import Schedule , number_expected
from datetime import timedelta, datetime

mydate = datetime(2019, 3, 25,0) # the date and hour for which we calculate the number of expected

# +- 3h interval around the date
lower_boundary = mydate - timedelta(hours=3) 
upper_boundary = mydate + timedelta(hours=3)

s = Schedule.create_default_schedule() # create default schedule 7/24 around the year, 6 hourly observations

r = number_expected([s,],lower_boundary,upper_boundary)

print("between {} and {} we expect {} observations with the schedule {}".format(lower_boundary,upper_boundary,r,s))

s1 = Schedule.create_default_schedule() # custom schedule with 30min observations between 0:30 and 23:30
s1.hour_from = 0
s1.min_from = 30
s1.hour_to = 23
s1.min_to = 30
s1.interval = 60*30

r1 = number_expected([s1,],lower_boundary,upper_boundary)

print("between {} and {} we expect {} observations with the schedule {}".format(lower_boundary,upper_boundary,r1,s1))
```


In order to test the package run `python -m unittest discover -s tests`