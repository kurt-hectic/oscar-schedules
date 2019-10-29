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
    
    logging.debug("got inernal id {} for {}".format(internal_id,wigos_id))
    
    url_obs = "https://oscar.wmo.int/surface/rest/api/stations/stationObservations/{}".format(internal_id)
    r = requests.get(url_obs).json()

    if not isinstance(variables,list):
        variables = [variables,]

    
    # get observation ids and filter by operational status and variable, if requested
    observation_ids = [ obs['id'] for obs in r if (  any(  prog_s["declaredStatusName"] == "Operational" for prog in obs["programs"] for prog_s in prog["stationProgramStatuses"] ) and (  len(variables) == 0 or obs['variableId'] in variables ) ) ]
      
    
    observations = {}
    
    for obs_id in observation_ids:
        url_depl = "https://oscar.wmo.int/surface/rest/api//stations/deployments/{}".format(obs_id)
        r = requests.get(url_depl).json()
        
        observations[obs_id] = [ json2schedule(dg) for depl in r for dg in depl["dataGenerations"] if ( "isInternationalExchange" in dg["reporting"] and dg["reporting"]["isInternationalExchange"] )  ]

    return observations


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
