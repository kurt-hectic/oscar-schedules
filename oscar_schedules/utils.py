import requests
import logging

from .schedule import Schedule

def getSchedules(wigos_id,variables=[]):

    url = "https://oscar.wmo.int/surface/rest/api/search/station?wigosId={}".format(wigos_id)
    r = requests.get(url).json()
    
    if len(r) == 0 :
        msg = "Station {} not found".format(wigos_id)
        logging.error(msg)
        raise ValueError(msg)
    
    if len(r) != 1  :
        msg = "{} not unique.. got {} results".format(wigos_id,len(r))
        logging.error(msg)
        raise ValueError(msg)

    internal_id = r[0]['id']
    name = r[0]['name']
    
    logging.debug("got inernal id {} for {}".format(internal_id,wigos_id))
    
    url_obs = "https://oscar.wmo.int/surface/rest/api/stations/stationObservations/{}".format(internal_id)
    r = requests.get(url_obs).json()

    if not isinstance(variables,list):
        variables = [variables,]

    
    # get observation ids and filter by operational status and variable, if requested
    observation_ids = []
    for obs in r:
        logging.debug("checking {}".format(obs))
        if not any(  prog_s["declaredStatusName"] == "Operational" for prog in obs["programs"] for prog_s in prog["stationProgramStatuses"] ):
            logging.debug("filtering out step 1")
            continue
        if  len(variables) > 0 and not obs['variableId'] in variables :
            logging.debug("filtering out step 2 {} {}".format(obs['variableId'],variables))
            continue
            
        temp = {'id' : obs['id'] , 'name' : obs['variableName'] , 'var_id' : obs['variableId']  }
        logging.debug("adding {}".format(temp))
        observation_ids.append( temp )
        
    
    logging.debug("extracted obs {}".format(observation_ids))
      
    
    observations = {}
    
    for obs in observation_ids:
        url_depl = "https://oscar.wmo.int/surface/rest/api//stations/deployments/{}".format(obs["id"])
        r = requests.get(url_depl).json()
        
        schedules = [ json2schedule(dg) for depl in r for dg in depl["dataGenerations"] if ( "isInternationalExchange" in dg["reporting"] and dg["reporting"]["isInternationalExchange"] )  ]

        observations[obs["var_id"]] = { 'variableName' :  obs['name'] , 'schedules' : schedules }
        
    infos = {'name':name,'observations':observations}

    return infos


def json2schedule(dg):

    schedule = dg["schedule"]
    reporting = dg["reporting"]

    s = Schedule(
        schedule["monthSince"],
        schedule["weekdaySince"],
        schedule["hourSince"],
        schedule["minuteSince"],
        schedule["monthTill"],
        schedule["weekdayTill"],
        schedule["hourTill"],
        schedule["minuteTill"],
        reporting["temporalReportingIntervalDB"],
        reporting["isInternationalExchange"], # always true, since we filter
        "operational" # always operational, since we filter

    )
    
    return s

def oscar2schedule(row):

    try:
        month_from = int(row['MONTH_SINCE_NU'])
        month_to = int(row['MONTH_TILL_NU'])
    except ValueError:
        month_from = 1
        month_to = 12
    try:
        week_from = int(row['WEEKDAY_SINCE_NU'])
        week_to = int(row['WEEKDAY_TILL_NU'])
    except ValueError:
        week_from = 1
        week_to = 7
    try:
        hour_from = int(row['HOUR_SINCE_NU'])
        hour_to = int(row['HOUR_TILL_NU'])
    except ValueError:
        hour_from = 0
        hour_to = 23
    try:
        min_from = int(row['MINUTE_SINCE_NU'])
        min_to = int(row['MINUTE_TILL_NU'])
    except ValueError:
        min_from = 0
        min_to = 59
    interval = int(row["TEMP_REP_INTERVAL_NU"])
    if interval == 0:
        raise ValueError("temporal reporting interval cannot be 0")

    international = int(row["INTERNATIONAL_EXCHANGE_YN"]) == 1
    status = row["OPERATING_STATUS_DECLARED_WMO306"]

    s = Schedule(
        month_from,
        week_from,
        hour_from,
        min_from,
        month_to,
        week_to,
        hour_to,
        min_to,
        interval,
        international,
        status,
    )

    return s
