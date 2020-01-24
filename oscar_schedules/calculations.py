import datetime
import math
import fractions
import copy
import logging
from .schedule import Schedule

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()


def lcm_mult(a):
    if len(a) < 2:
        raise Exception("pass at laest two")
    res = lcm(a[0],a[1])
    for i in range(2,len(a)):
        res = lcm(res,a[i])
    return res
        
        
def lcm(a, b):
    return abs(a*b) // fractions.gcd(a, b)
    

def generate_and_count(overlap_periods):
        logger.debug("gen_count: {}".format(overlap_periods))
        
        observations = []
        for op in overlap_periods:
            date_generated = [op['from'] + datetime.timedelta(seconds=x*op['interval']) for x in 
                              range(0, int(math.ceil((op['to']-op['from']).total_seconds() /  op['interval'] )))  ]
            observations += date_generated
            logger.debug("obs:{}".format(date_generated))
        
        
        return len( set(observations) )
        
        
        #raise Exception("non trivial overlapping schedules not yet implemented")
     
def pre_process_weird_schedules(schedules):
    """This method detects schedules where the from is higher than the to, which can sometimes happen 
    when the schedule goes into the next day. In this case we split the schedule into two parts.
    We also test if the from and to date are the same.
    """
    logger.debug("processed weird schedules. Input: {}".format( [ str(s) for s in schedules] ))
    
    ret = []
    change = False
    
    for s in schedules:
        
        same_same = False
        if s.hour_from == s.hour_to and s.min_from == s.min_to: # same start and end time.. convert the schedule into a 24h schedule. 
            
            # substract one minute from to schedule
            same_same  = True
            logger.debug("equal start/end {}".format(s))
            temp = datetime.datetime(1981,1,25,s.hour_from,s.min_from)
            new_to_time =  temp - datetime.timedelta(minutes=1)
            s.hour_to = new_to_time.hour # this means to < from, and will be detected as "weird" schedule
            s.min_to = new_to_time.minute
            s.diurnal_hour = s.hour_from
            s.diurnal_min = s.min_from
            logger.debug("equal start/end result: {}".format(s))
        
        if s.hour_from > s.hour_to or ( s.hour_from == s.hour_to and s.min_from > s.min_to  ): # if the schedule is weird
            same_same=True
            logger.debug("WEIRD: {}  ".format(s))
            
            if s.month_from + s.month_to != 13 or s.week_from + s.week_to != 8: # the schedule needs to be continous
                print("error: schedule invalid. {}".format(s))
                continue
                
            temp = datetime.datetime(1981,1,25,s.hour_from,s.min_from)
            temp2 = datetime.datetime(1981,1,25,s.hour_to,s.min_to)
            
            if temp2 + datetime.timedelta(minutes=1) == temp: # only one minute difference.. this means the diurnal time should be set
                s.diurnal_hour = s.hour_from
                s.diurnal_min = s.min_from
            
            # we split the schedule into two equivalent schedules having from < to                
            change = True
            
            s1 = copy.copy( s )
            s2 = copy.copy( s )
            
            s1.hour_to = 23
            s1.min_to = 59
            s1.ispartofweird = True
            
            s2.hour_from = 0
            s2.min_from = 0
            s2.isweird = True # the second of the weird schedules is marked, since we need to avoid double counting overlap periods
            
            logger.debug("new schedules {} and {}".format(s1,s2))
            
            # calculate difference
            d1 = datetime.datetime(1981,1,25,s1.hour_from,s1.min_from)
            d2 = datetime.datetime(1981,1,25,s1.hour_to,s1.min_to)
            
            d3 = datetime.datetime(1981,1,26,s2.hour_from,s2.min_from)
            d4 = datetime.datetime(1981,1,26,s2.hour_to,s2.min_to)

            difference = (d4-d1).total_seconds() + ( 60 if same_same else 0 ) # if we have a schedule with equal start and end need to add the missing minute
            logger.debug("weird schedule: difference between {} {} is: {} , interval: {} ".format(d1,d4,difference,s1.interval))
            
            # the reporting interval is larger or equal to the interval between the lower and upper endpoints of the new "weird" schedule
            if s1.interval >= difference : 
                ret.append(s1) # we append only one, because the reporting interval only fits once
            else : # the reporting interval potentially fits more than once
                logger.debug("the reporting interval potentially fits more than once")
                difference2 = (d2-d1).total_seconds() + 60
                remainder = s1.interval - (difference2 % s1.interval) #
                
                logger.debug("d1: {} d2: {}, interval:{} , diff: {} , remainder: {}".format(d1,d2,s1.interval,difference2,remainder))
            
                if (difference2 % s1.interval) != 0: # need to offset because schedules do not align nicely 
                    
                    if s1.diurnal_hour == 0 and s1.diurnal_min == 0:
                        offset_hour = int(math.floor(remainder / (60*60)))
                        offset_min = int((remainder % (60*60) ) / 60 )

                        logger.debug("weird schedule: remainder:{} offset h:{} min: {}".format(remainder,offset_hour,offset_min))
                        
                        s2.hour_from = s2.hour_from + offset_hour
                        s2.min_from = s2.min_from + offset_min
                    else:
                        logger.debug("weird schedules: we already have a diurnal offset")
                        pass

                ret.append(s1)
                ret.append(s2)

        else:
            ret.append( s )
     
    logger.debug("processed weird schedules. Result: {}".format( [ str(s) for s in ret] ))

    return ret
            
        


def number_expected(schedules,lower,upper):
    """Computes the number of expected observations in the specified interval for the schedules.
    
    schedules -- a list of schedules of type Schedule. If a single Schedule is passed it is converted into a list
    lower -- the lower boundary of the interval (included)
    upper -- the upper boundary of the interval (exluded)
    
    Observations resulting from multiple schedules are only counted once.
    """
    
    # some sanity checking of arguments
    if not type(lower) in (datetime.datetime, datetime.date) or not type(upper) in (datetime.datetime, datetime.date) :
        raise ValueError("upper and lower boundaries need to be datetimes {} {}".format(type(lower),type(upper)))
    
    if not isinstance(schedules, list):
        schedules = [schedules,]
        
    for s in schedules:
        if not isinstance(s,Schedule):
            raise ValueError("schedule {} not of type Schedule".format(s))
            
    if len(schedules)==0:
        raise ValueError("pass at least one schedule")

    tmp = [ "{diurnal_hour}:{diurnal_min}".format(**s.__dict__) for s in schedules ]
    if not len(tmp) == tmp.count(tmp[0]): # all diurnal times are the same
        raise ValueError("schedules with different diurnal basetimes are currently not supported") #TODO: use generate_and_count to handle this
    else:
        my_schedule=schedules[0]
        reference =  datetime.datetime(upper.year,upper.month,upper.day,my_schedule.diurnal_hour,my_schedule.diurnal_min)

    
    # all good, start calculations now
    logger.debug("computing nr exp (begin):  lower:{}, upper:{} , schedules: {} ".format(lower,upper,",".join( [ str(s) for s in schedules]  )))
    schedules = pre_process_weird_schedules(schedules) 
    logger.debug("computing nr exp (after weird):  lower:{}, upper:{} , schedules: {} ".format(lower,upper,",".join( [ str(s) for s in schedules]  )))
    ## FIXME:: need to update reference in case of "weird" schedules.. likely for both parts.. 
    ## reference would then become the diurnal basetime of the lower day (for both schedules)
    
    periods = []
    for s in schedules:
        my_reference = reference
        if s.isweird or s.ispartofweird:
            my_reference = datetime.datetime(year=lower.year,month=lower.month,day=lower.day,hour=s.diurnal_hour,minute=s.diurnal_min)
            
        if s.isweird: # for the 2nd schedule of a "weird" schedule, we only take into account the part of the period after 00:00 
            mylower = datetime.datetime( upper.year , upper.month, upper.day, 0,0 ) # 0:0h of the day of the upper boundary
            mylower = mylower if mylower >= lower else lower # take the maximum of the original lower boundary and 0:00 on the upper boundary day
            reference = reference - datetime.timedelta(days=1) # the reference point 
            periods += s.compute_overlap_periods(mylower,upper,my_reference)
        else :
            periods += s.compute_overlap_periods(lower,upper,my_reference)
    
    logger.debug("step 1: calculating overlap periods for: {}".format(periods))
    # check if periods overlap
    overlap = [False] * len(periods)
    for i in range(0,len(periods)):
        for j in range(i+1,len(periods)):
            if min(periods[i]['to'],periods[j]['to'])  >=  max(periods[j]['from'], periods[i]['from']):
                overlap[i] = True
                overlap[j] = True
                break
                
    logger.debug("overlap is: {}".format(overlap))        
    # calculate number observations 
    ret = 0
    i = 0
    overlap_periods = []
    for p in periods:
        if not overlap[i]:
            # we need ceil because the interval between from and to can be shorter than the reporting inteval
            # but it still counts as one observation
            r_temp = math.ceil((p['to'] - p['from']).total_seconds() / p['interval']) 
            ret += r_temp
            logger.debug("from: {from} to: {to} int: {interval}. res: {}".format(r_temp,**p))
                #print(ret)
        else:
            overlap_periods.append(p)
        i+=1
    
    if len(overlap_periods) > 0:
        
        if lower.date() == upper.date() :
            overlap_periods_wrapper = [ overlap_periods , ]
        else: #can consider periods on one day separately from the ones on the other day
            temp={}
            temp[lower.date()] = []
            temp[upper.date()] = []
            
            for op in overlap_periods:
                temp[op['from'].date()].append(op) #group by date
        
            overlap_periods_wrapper = [ temp[upper.date()] , temp[lower.date()] ]
        
        for overlap_periods in overlap_periods_wrapper:
            # observations in periods with overlap
            # first get "overlap-points"
            overlap_points = []
            for op in overlap_periods:
                overlap_points += [ op['from'] , op['to'] ]

            overlap_points = list(set(overlap_points)) # get unique set of overlap points
            if len(overlap_points) == 2 : #
                # depending on how many schedules we have we can use our equations or need to compute
                if len(overlap_periods) == 2:
                    logger.debug("step 2 with 2")
                    start_a = overlap_periods[0]['from']
                    end_a = overlap_periods[0]['to']
                    start_b = overlap_periods[1]['from']
                    end_b = overlap_periods[1]['to']
                    freq_a = overlap_periods[0]['interval'] 
                    freq_b = overlap_periods[1]['interval']

                    nr_a = math.ceil((end_a - start_a).total_seconds()  / freq_a)
                    nr_b = math.ceil((end_b - start_b).total_seconds() / freq_b)

                    nr_dupes = math.ceil((end_a - start_a).total_seconds() / lcm(freq_a,freq_b))
                    logger.debug("nr_a: {} , nr_b: {} , freq_a:{} , freq_b:{}".format(nr_a,nr_b,freq_a,freq_b))

                    ret += nr_a+nr_b-nr_dupes

                elif len(overlap_periods) == 3:
                    logger.debug("step 2 with 3")
                    start_a = overlap_periods[0]['from']
                    end_a = overlap_periods[0]['to']
                    start_b = overlap_periods[1]['from']
                    end_b = overlap_periods[1]['to']
                    start_c = overlap_periods[2]['from']
                    end_c = overlap_periods[2]['to']

                    freq_a = overlap_periods[0]['interval'] 
                    freq_b = overlap_periods[1]['interval']
                    freq_c = overlap_periods[2]['interval']

                    nr_a = math.ceil((end_a - start_a).total_seconds()  / freq_a)
                    nr_b = math.ceil((end_b - start_b).total_seconds() / freq_b)
                    nr_c = math.ceil((end_c - start_c).total_seconds() / freq_c)

                    nr_dupes_ab = math.ceil((end_a - start_a).total_seconds() / lcm(freq_a,freq_b))
                    nr_dupes_ac = math.ceil((end_a - start_a).total_seconds() / lcm(freq_a,freq_c))
                    nr_dupes_bc = math.ceil((end_a - start_a).total_seconds() / lcm(freq_b,freq_c))

                    nr_dupes_abc = math.ceil((end_a - start_a).total_seconds() / lcm_mult([freq_a,freq_b,freq_c]))

                    ret +=  (nr_a + nr_b + nr_c) - (nr_dupes_ab + nr_dupes_ac + nr_dupes_bc) + nr_dupes_abc

                else: # we generate points, de-duplicate them and count 
                    ret += generate_and_count(overlap_periods)

            else:
                # we generate points, de-duplicate them and count
                ret += generate_and_count(overlap_periods)
    
    ret = math.floor(ret)
    logger.debug("ret {}".format(ret))
    
    return ret
    
       