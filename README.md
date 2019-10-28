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

s2 = Schedule.create_default_schedule() # custom schedule with 45min observations between 1:30 and 22:30
s2.hour_from = 1
s2.min_from = 30
s2.hour_to = 22
s2.min_to = 30
s2.interval = 60*45


r1 = number_expected([s1,s2],lower_boundary,upper_boundary)

print("between {} and {} we expect {} observations with the schedules {}".format(lower_boundary,upper_boundary,r1, [ str(s) for s in [s1,s2] ]  ))
```


In order to test the package run `python -m unittest discover -s tests`


The library can now fetch schedules directly from OSCAR
```python
from oscar_schedules import Schedule , number_expected, getSchedules
from datetime import timedelta, datetime
import logging
import os

#logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

mydate = datetime(2019, 3, 25,18) # the date and hour for which we calculate the number of expected

# +- 3h interval around the date
lower_boundary = mydate - timedelta(hours=3) 
upper_boundary = mydate + timedelta(hours=3)

print("checking number expected for interval {} to {}".format(lower_boundary,upper_boundary))

infos = getSchedules("0-20000-0-52787",[224,])

for obs_id,schedules in infos.items():
    e = number_expected(schedules,lower_boundary,upper_boundary)
    print("variable: {} expected: {} for schedules {}".format(obs_id,e,  ",".join([ str(s) for s in schedules ])  ))
```
