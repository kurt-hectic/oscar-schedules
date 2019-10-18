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
```

In order to test the package run `python -m unittest discover -s tests`