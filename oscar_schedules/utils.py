from oscar_schedules.schedule import Schedule


def oscar2schedule(row):

    status = row['OPERATING_STATUS_DECLARED_WMO306']
    try: 
        month_from = int(row['MONTH_SINCE_NU'])
        month_to = int(row['MONTH_TILL_NU'])
    except ValueError :
        month_from = 1
        month_to = 12
    try:
        week_from = int(row['WEEKDAY_SINCE_NU']) 
        week_to = int(row['WEEKDAY_TILL_NU'])
    except ValueError :
        week_from = 1
        week_to = 7
    try:
        hour_from = int(row['HOUR_SINCE_NU'])
        hour_to = int(row['HOUR_TILL_NU'])
    except ValueError :
        hour_from = 0
        hour_to = 23
    try:    
        min_from = int(row['MINUTE_SINCE_NU'])
        min_to = int(row['MINUTE_TILL_NU'])
    except ValueError :
        min_from = 0
        min_to = 59
    try:
        interval = int(row['TEMP_REP_INTERVAL_NU'])
        if interval == 0:
            raise ValueError
    except ValueError :
        interval = 60*60*6 #6h

    international = True

    s = Schedule(month_from,week_from,hour_from,min_from,month_to,week_to,hour_to,min_to,interval,international,status)
   
    
    return s