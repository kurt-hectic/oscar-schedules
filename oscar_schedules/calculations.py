import datetime
import math
import fractions
import copy
import logging

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
     
# here we detect schedules where the from is higher than the to, which can sometimes happen 
# when the schedule goes into the next day
# in this case we split the schedule into two parts
def pre_process_weird_schedules(schedules):
    ret = []
    
    change = False
    
    for s in schedules:
        
        if s.hour_from > s.hour_to or ( s.hour_from == s.hour_to and s.min_from > s.min_to  ): # if the schedule is weird
        
            logger.debug("WEIRD: {}  ".format(s))
            
            if s.month_from + s.month_to != 13 or s.week_from + s.week_to != 8: # the schedule needs to be continous
                print("error: schedule invalid. {}".format(s))
                continue
            
            # we split the schedule into two equivalent schedules having from < to                
            change = True
            
            s1 = copy.copy( s )
            s2 = copy.copy( s )
            
            s1.hour_to = 23
            s1.min_to = 59
            
            s2.hour_from = 0
            s2.min_from = 0
            
            # calculate difference
            d1 = datetime.datetime(1981,1,25,s1.hour_from,s1.min_from)
            d2 = datetime.datetime(1981,1,25,s1.hour_to,s1.min_to)
            
            d3 = datetime.datetime(1981,1,26,s2.hour_from,s2.min_from)
            d4 = datetime.datetime(1981,1,26,s2.hour_to,s2.min_to)

            difference = (d4-d1).total_seconds()
            logger.debug("weir schedule: difference between {} {} is: {}".format(d1,d4,difference))
            
            # the reporting interval is larger or equal to the interval between the lower and upper endpoints of the new "weird" schedule
            if s1.interval >= difference : 
                ret.append(s1) # we append only one, because the reporting interval only fits once
            else : # the reporting interval potentially fits more than once
            
                difference2 = (d2-d1).total_seconds() + 60
                remainder = s1.interval - (difference2 % s1.interval)  
                
                logger.debug("d1: {} d2: {}, interval:{} , diff: {}".format(d1,d2,s1.interval,difference2))
            
                if remainder != 0: # need to offset because schedules do not align nicely       
                    offset_hour = int(math.floor(remainder / (60*60)))
                    offset_min = int((remainder % (60*60) ) / 60 )

                    logger.debug("weird schedule: remainder:{} offset h:{} min: {}".format(remainder,offset_hour,offset_min))
                    
                    s2.hour_from = s2.hour_from + offset_hour
                    s2.min_from = s2.min_from + offset_min

                ret.append(s1)
                ret.append(s2)



        else:
            ret.append( s )
     
    if change:
        logger.debug("process weird schedules: {}".format( [ str(s) for s in ret] ))

    return ret
            
        


def number_expected(schedules,lower,upper):
    
    logger.debug("computing nr exp:  lower:{}, upper:{} , schedules: {} ".format(lower,upper,",".join( [ str(s) for s in schedules]  )))
    
    schedules = pre_process_weird_schedules(schedules) 
    
    logger.debug("computing nr exp:  lower:{}, upper:{} , schedules: {} ".format(lower,upper,",".join( [ str(s) for s in schedules]  )))
    
    
    periods = []
    for s in schedules:
        periods += s.compute_overlap_periods(lower,upper)
    
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
    
       