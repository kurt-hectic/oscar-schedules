from datetime import timedelta
import datetime
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()



class Schedule:
    
    def compute_overlap_period_day(self,lower,upper,mydate):
        # check if candidate schedule is possible on the date
        if mydate.month < self.month_from or mydate.month > self.month_to:
            return None
        if mydate.weekday()+1 < self.week_from or mydate.weekday()+1 > self.week_to:
            return None

        # check if candidate schedule overlaps with period 
        cand_lower = datetime.datetime(mydate.year,mydate.month,mydate.day, self.hour_from, self.min_from )
        cand_upper = datetime.datetime(mydate.year,mydate.month,mydate.day, self.hour_to, self.min_to )

        max_lower = max( cand_lower, lower )
        min_upper = min( cand_upper, upper )

        if max_lower <= min_upper: # overlap 
            return {'from' : max_lower , 'to' : min_upper , 'interval' : self.interval }
        else:
            return None
    
    def compute_overlap_periods(self,lower,upper):
        logger.debug("computing overlap between schedule and period: l:{}, u:{}, month from:{} month to:{} ".format(lower,upper,self.month_from,self.month_to))
        
        # compute candidate schedules
        schedules = []
        if not self.international or self.status != 1 : # not international or not operational
            return schedules
        
        if lower.date() == upper.date() : # period is on same day
            mydate = lower.date()
            
            s = self.compute_overlap_period_day(lower,upper,mydate)
            if s:             
                schedules.append( s )
            
        else: # critical period as it overlaps two days
            
            left_period = self.compute_overlap_period_day(lower,upper,lower.date())
            right_period = self.compute_overlap_period_day(lower,upper,upper.date())
            
            if left_period and right_period : # check if valid in both periods. If yes, construct a single period
                if left_period['to'] + datetime.timedelta(minutes=1) == right_period['from']: #continuous
                    s = {'from'  : left_period['from']  , 'to' : right_period['to'] , 'interval' : right_period['interval'] }
                    schedules.append(  s   )
                else: # not continous, need both with gap
                    schedules += [ left_period, right_period ]                    
            elif left_period : # but not right
                schedules.append( left_period )
            elif right_period : # but not left
                schedules.append( right_period )
        
        logger.debug("result: {}".format(schedules))
        
        return schedules
    
    
    
    def create_default_schedule():
        
        s = Schedule()
        
        s.month_from = 1
        s.month_to = 12
        s.week_from = 1
        s.week_to = 7
        s.hour_from = 0
        s.hour_to = 23
        s.min_from = 0
        s.min_to = 59
        s.interval = 60*60*6 #6 hourly
        s.international = True
        s.status = 1
        
        return s
    
    def __str__(self):
        return "from {month_from}/{week_from} {hour_from}:{min_from}  to: {month_to}/{week_to} {hour_to}:{min_to} interval: {interval}".format(**self.__dict__)
    
    
    def __init__(self,row=None):
        
        if row:
            self.status = int(row['OPERATING_STATUS_DECLARED_ID'])
            try: 
                self.month_from = int(row['MONTH_SINCE_NU'])
                self.month_to = int(row['MONTH_TILL_NU'])
            except ValueError :
                self.month_from = 1
                self.month_to = 12
            try:
                self.week_from = int(row['WEEKDAY_SINCE_NU']) 
                self.week_to = int(row['WEEKDAY_TILL_NU'])
            except ValueError :
                self.week_from = 1
                self.week_to = 7
            try:
                self.hour_from = int(row['HOUR_SINCE_NU'])
                self.hour_to = int(row['HOUR_TILL_NU'])
            except ValueError :
                self.hour_from = 0
                self.hour_to = 23
            try:    
                self.min_from = int(row['MINUTE_SINCE_NU'])
                self.min_to = int(row['MINUTE_TILL_NU'])
            except ValueError :
                self.min_from = 0
                self.min_to = 59
            try:
                self.interval = int(row['TEMP_REP_INTERVAL_NU'])
            except ValueError :
                self.interval = 60*60*6 #6h

            self.international = True
 