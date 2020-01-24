import datetime
import logging
import calendar

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()


class Schedule:

    STATUS_OP = "operational"

    def compute_overlap_period_day(self, lower, upper, mydate):
        #logger.debug("compute overlap: lower: {} upper:{} and {} on {} ".format(lower,upper,self,mydate))
        # check if candidate schedule is possible on the date
        if mydate.month < self.month_from or mydate.month > self.month_to:
            return None
        if mydate.weekday() + 1 < self.week_from or mydate.weekday() + 1 > self.week_to:
            return None

        # check if candidate schedule overlaps with period
        cand_lower = datetime.datetime(
            mydate.year, mydate.month, mydate.day, self.hour_from, self.min_from
        )
        cand_upper = datetime.datetime(
            mydate.year, mydate.month, mydate.day, self.hour_to, self.min_to
        )

        max_lower = max(cand_lower, lower)
        min_upper = min(cand_upper, upper)

        if max_lower <= min_upper:  # overlap
            return {"from": max_lower, "to": min_upper, "interval": self.interval}
        else:
            return None

    def compute_overlap_periods(self, lower, upper, reference=None):
        """Compute the overlap between a schedule and the interval in question.
        If the interval spans two days (0h synoptic interval), it can result in multiple schedules being returned for one schedule
        """
        
        logger.debug(
            "computing overlap between schedule {} and period: l:{}, u:{}, month from:{} month to:{}, reference: {} ".format(
                self, lower, upper, self.month_from, self.month_to, reference
            )
        )
        
        if not reference: #if no reference data is provided use the lower boundary
            reference = lower 

        # compute candidate schedules
        schedules = []
        if (
            not self.international or self.status != Schedule.STATUS_OP
        ):  # not international or not operational
            logger.debug("no overlap, schedule not operational ")
            return schedules
            
        if self.interval > 60*60*6 : # reporting interval is greater than 6h
            if reference > upper:
                reference = (reference - datetime.timedelta(days=1))
                
            r = Schedule.checkInterval(lower,upper,reference,self.interval)
            if not r: # no overlap possible according to base reference and interval
                logger.debug("no overlap possible because of base reference and interval")
                return []
            [interval_nr,offset] = r
            logger.debug("offset is {}".format(offset))
            if offset.total_seconds() != 60*60*3:
                lower = lower + offset
                
        if lower.date() == upper.date():  # period is on same day
            mydate = lower.date()

            s = self.compute_overlap_period_day(lower, upper, mydate)
            if s:
                schedules.append(s)

        else:  # critical period as it overlaps two days

            left_period = self.compute_overlap_period_day(lower, upper, lower.date())
            right_period = self.compute_overlap_period_day(lower, upper, upper.date())

            if left_period and right_period:  # check if valid in both periods. If yes, construct a single period
                if left_period["to"] + datetime.timedelta(minutes=1) == right_period["from"]:  # continuous
                    s = {"from": left_period["from"], "to": right_period["to"],"interval": right_period["interval"]}
                    schedules.append(s)
                else:  # not continous, need both with gap
                    schedules += [left_period, right_period]
            elif left_period:  # but not right
                schedules.append(left_period)
            elif right_period:  # but not left
                schedules.append(right_period)

        logger.debug("result: {}".format(schedules))

        return schedules
        
    def checkInterval(lower,upper,reference,interval):
        """Check if given the base reference time and the interval, an overlap can happen in the interval"""

        logging.debug("checkInterval: low:{} and up:{}, reference: {}, interval: {}".format(lower,upper,reference,interval))

        
        low = (lower - reference) 
        up = (upper - reference)
           
        logging.debug("low {} , up: {} ".format(low,up))

        if low.total_seconds() == 0: # lower boundary and reference are identical (ocurrs with weird schedules) 
            return [0,datetime.timedelta(seconds=0)]
        
        for r in range(0,60*60*24,interval):
            p = reference + datetime.timedelta(seconds=r)
            logger.debug("xx: {}".format(p))
            if lower<=p and p<upper:
                offset = p-lower
                return [r,offset]
        
        return False


    def create_default_schedule():

        return Schedule()

    def __str__(self):
    
        temp = {
            'month_from' : calendar.month_abbr[self.month_from],
            'month_to' : calendar.month_abbr[self.month_to],
            'week_from' : calendar.day_abbr[self.week_from-1],
            'week_to' : calendar.day_abbr[self.week_to-1],
            'hour_from' : self.hour_from,
            'hour_to' : self.hour_to,
            'min_from' : self.min_from,
            'min_to' : self.min_to,
            'interval' : str(datetime.timedelta(seconds=self.interval)),
            'diurnal_h' : self.diurnal_hour,
            'diurnal_m': self.diurnal_min
            
        }
    
        return "{month_from}-{month_to}/{week_from}-{week_to}/{hour_from}:{min_from}-{hour_to}:{min_to} [{interval}] <{diurnal_h}:{diurnal_m}> ".format(
            **temp
        )

    def __init__(
        self,
        month_from=1,
        week_from=1,
        hour_from=0,
        min_from=0,
        month_to=12,
        week_to=7,
        hour_to=23,
        min_to=59,
        interval=60 * 60 * 3,
        international=1,
        status=STATUS_OP,
        diurnal_hour = 0,
        diurnal_min = 0
    ):

        if not interval or int(interval) == 0:
            raise ValueError("interval cannot be 0 and must be a number")

        self.month_from = int(month_from)
        self.week_from = int(week_from)
        self.hour_from = int(hour_from)
        self.min_from = int(min_from)

        self.month_to = int(month_to)
        self.week_to = int(week_to)
        self.hour_to = int(hour_to)
        self.min_to = int(min_to)

        self.international = international
        self.status = status
        self.interval = interval
        
        self.isweird = False
        self.ispartofweird = False
        
        self.diurnal_hour=diurnal_hour
        self.diurnal_min=diurnal_min
        
        if 60*60*24 % self.interval != 0:
            raise ValueError("interval needs to fit evenly into day")
