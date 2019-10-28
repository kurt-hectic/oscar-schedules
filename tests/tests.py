import datetime
from datetime import timedelta
#import oscar_schedules
from oscar_schedules import Schedule, number_expected

import unittest


class TestDefaultSchdule(unittest.TestCase):
    def test_schedule(self):
        """
        Test the schedule
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s = Schedule() # default schedule has 6h observations

        r = number_expected([s],lower_boundary,upper_boundary)

        self.assertEqual(r, 1 )
        
        
class TestThreeSchdules(unittest.TestCase):
    def test_schedule(self):
        """
        Test three overlapping schedules with 30min, 45min and 1h
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s1 = Schedule()
        s1.hour_from = 0
        s1.min_from = 30
        s1.hour_to = 23
        s1.min_to = 30
        s1.interval = 60*30

        s2 = Schedule()
        s2.hour_from = 0
        s2.min_from = 30
        s2.hour_to = 23
        s2.min_to = 30
        s2.interval = 60*60

        s3 = Schedule()
        s3.hour_from = 22
        s3.min_from = 0
        s3.hour_to = 23
        s3.min_to = 30
        s3.interval = 60*5


        r = number_expected([s1,s2,s3],lower_boundary,upper_boundary)

        self.assertEqual(r, 25 )
        
class TestTwoSchedules(unittest.TestCase):
    def test_schedule(self):
        """
        Test 30 min vs 45min overlap test
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s4 = Schedule()
        s4.interval = 60*30

        s5 = Schedule()
        s5.interval = 60*45

        r = number_expected([s4,s5],lower_boundary,upper_boundary)

        self.assertEqual(r, 16 )
        
        
        
class TestECMWFSchedules(unittest.TestCase):
    def test_schedule(self):
        """
        Test for the bug identified by ECMWF where the reporting interval does not fit the interval between upper and lower boundary
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s4 = Schedule()
        s4.interval = 60*30

        s5 = Schedule()
        s5.interval = 60*45

        r = number_expected([s4,s5],lower_boundary,upper_boundary)

        self.assertEqual(r, 16 )
        
        
class TestInvertedSchedules(unittest.TestCase):
    def test_schedule(self):
        """
        Test upper boundary higher than upper boundary
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s = Schedule()
        s.hour_from = 22
        s.min_from = 0
        s.hour_to = 21
        s.min_to = 59
        s.interval = 60*60

        r = number_expected([s,],lower_boundary,upper_boundary)

        self.assertEqual(r, 5 )
        
        
        
class TestIndianSchedules(unittest.TestCase):
    def test_schedule(self):
        """
        Test schedules of stations with same starting hour
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s = Schedule()
        s.hour_from = 3
        s.min_from = 0
        s.hour_to = 3
        s.min_to = 59
        s.interval = 60*60*6 

        r = number_expected([s,],lower_boundary,upper_boundary)

        self.assertEqual(r, 0 )
        
        
        
class TestChineseSchedules(unittest.TestCase):
    def test_schedule(self):
        """
        Test schedules of Chinese stations reported by Cristina (XINGREN , Kuqa )
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s = Schedule()
        s.hour_from = 0
        s.min_from = 0
        s.hour_to = 21
        s.min_to = 59
        s.interval = 60*60*3 

        r = number_expected([s,],lower_boundary,upper_boundary)

        self.assertEqual(r, 2 )
        
        
class TestChineseDuplicatedSchedules(unittest.TestCase):
    def test_schedule(self):
        """
        Test schedules of Chinese stations reported by Cristina (XINGREN , Kuqa ), where schedules are duplicated
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s1 = Schedule()
        s1.hour_from = 0
        s1.min_from = 0
        s1.hour_to = 21
        s1.min_to = 59
        s1.interval = 60*60*3 

        s2 = Schedule()
        s2.hour_from = 0
        s2.min_from = 0
        s2.hour_to = 21
        s2.min_to = 59
        s2.interval = 60*60*3 

        r = number_expected([s1,s2],lower_boundary,upper_boundary)

        self.assertEqual(r, 2 )
        
        
class TestChineseTriplicatedSchedules(unittest.TestCase):
    def test_schedule(self):
        """
        Test schedules of Chinese stations reported by Cristina (XINGREN , Kuqa ), where schedules are duplicated
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s1 = Schedule()
        s1.hour_from = 0
        s1.min_from = 0
        s1.hour_to = 21
        s1.min_to = 59
        s1.interval = 60*60*3 

        s2 = Schedule()
        s2.hour_from = 0
        s2.min_from = 0
        s2.hour_to = 21
        s2.min_to = 59
        s2.interval = 60*60*3 

        s3 = Schedule()
        s3.hour_from = 0
        s3.min_from = 0
        s3.hour_to = 21
        s3.min_to = 59
        s3.interval = 60*60*3 


        r = number_expected([s1,s2,s3],lower_boundary,upper_boundary)

        self.assertEqual(r, 2 )
        
        
class TestRadiosondeDefaultSchedules(unittest.TestCase):
    def test_schedule(self):
        """
        Test schedules for default Radiosonde schedules , where we have one observation at 0 and another at 12
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s1 = Schedule()
        s1.hour_from = 21
        s1.min_from = 0
        s1.hour_to = 3
        s1.min_to = 0
        s1.interval = 60*60*6 

        r = number_expected([s1,],lower_boundary,upper_boundary)
        
        self.assertEqual(r, 1 )
   
        hour = 12
        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s1 = Schedule()
        s1.hour_from = 9
        s1.min_from = 0
        s1.hour_to = 15
        s1.min_to = 0
        s1.interval = 60*60*6 

        r = number_expected([s1,],lower_boundary,upper_boundary)
        
        self.assertEqual(r, 1 )
   
class TestUnalignedWeirdSchedules(unittest.TestCase):
    def test_schedule(self):
        """
        Test "weird" schedules that is not aligned
        """

        year = 2019
        month = 3
        day = 25 
        hour = 0

        mydate = datetime.datetime(year, month, day,hour)

        lower_boundary = mydate - timedelta(hours=3)
        upper_boundary = mydate + timedelta(hours=3)

        s1 = Schedule()
        s1.hour_from = 22
        s1.min_from = 30
        s1.hour_to = 1
        s1.min_to = 30
        s1.interval = 60*60*1 

        r = number_expected([s1,],lower_boundary,upper_boundary)
        
        self.assertEqual(r, 3 )
        
        
        # add additional schedule that overlaps
        s2 = Schedule()
        s2.hour_from = 1
        s2.min_from = 0
        s2.hour_to = 6
        s2.min_to = 00
        s2.interval = 60*60*1 
        
        
        r = number_expected([s1,s2],lower_boundary,upper_boundary)
        
        self.assertEqual(r, 5 )
        
        
        # add additional schedule that overlaps
        s3 = Schedule()
        s3.hour_from = 0
        s3.min_from = 0
        s3.hour_to = 6
        s3.min_to = 00
        s3.interval = 60*30 

        r = number_expected([s1,s3],lower_boundary,upper_boundary)
        
        self.assertEqual(r, 8 )
        
        
        ####
        
        
        s1 = Schedule()
        s1.hour_from = 22
        s1.min_from = 15
        s1.hour_to = 1
        s1.min_to = 30
        s1.interval = 60*60*1 
        
        r = number_expected([s1,],lower_boundary,upper_boundary)
        
        self.assertEqual(r, 4 )
        
        
        