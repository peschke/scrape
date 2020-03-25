#!/usr/bin/env python3

import json
import requests
from datetime import datetime, timedelta

# this url is what gives us plan p information
#https://www.irvinecompanyapartments.com/bin/tic/ica/floorplanpricingavailability?app=icaFloorplanPage&sp_s=planName&sp_x_1=appId&sp_q_1=ica&sp_x_2=entityType&sp_q_2=unit&upm_field_table=1&sp_x_3=communityIdAEM&sp_q_3=055e718e-d752-4d4c-997f-639492142356&sp_x_4=floorUnitTypeCode&sp_q_4=22CP&sp_x_9=upm.upm_startDate&sp_q_max_day_9=22&sp_q_max_month_9=05&sp_x_10=upm.upm_endDate&sp_q_min_day_10=23&sp_q_min_month_10=03&sp_q_min_year_10=2020&sp_q_max_year_9=2021
# it does it by this line: sp_x_3=communityIdAEM&sp_q_3=055e718e-d752-4d4c-997f-639492142356
# this is the GUID provided by the first query below. It looks like sp_x_# is the key, and sp_q_# is the value

def is_leap_year(year):
    if ((year % 4 == 0 and year % 100 != 0) or year % 400 == 0):
        return True
    else:
        return False

def main():
    # with the query below, I was given two results for Plan P, but the GUID's were the same. This is because Westview I and II.
    #result = requests.get('https://www.irvinecompanyapartments.com/snp?app=ica&count=999&sp_s=planName&sp_x_1=appId&sp_q_1=ica&sp_x_2=entityType&sp_q_2=floorplan&sp_x_3=propertyIdCRM&sp_q_exact_3=0x0000000000000350|0x000000000000034f')
    payload = {
        'app':          'ica',
        'count':        '999',
        'sp_s':         'planName',
        'sp_x_1':       'appId',
        'sp_q_1':       'ica',
        'sp_x_2':       'entityType',
        'sp_q_2':       'floorplan',
        'sp_x_3':       'propertyIdCRM',
        'sp_q_exact_3': '0x0000000000000350|0x000000000000034f'  # Westview II and I property IDs
    }

    result = requests.get('https://www.irvinecompanyapartments.com/snp', params=payload)
                          
    data = result.json()
    #print(json.dumps(data, indent=4))

    guid = {}

    for resultset in data['resultsets']:
        for result in resultset['results']:
            if result['planName'] == 'V':
                # these two results are used in the query below to get available apartments and prices
                guid[result['communityIdAEM']] = result['floorUnitTypeCode']

    #print(guid)

    # These URLs get cached. If you want to see it in a network capture again, clear the browser cache.

    # handicap plans look to have a bit different format: floorplanIdCRM vs floorUnitTypeCode
    #https://www.irvinecompanyapartments.com/bin/tic/ica/floorplanpricingavailability?app=icaFloorplanPage&sp_s=planName&sp_x_1=appId&sp_q_1=ica&sp_x_2=entityType&sp_q_2=unit&upm_field_table=1&sp_x_3=communityIdAEM&sp_q_3=055e718e-d752-4d4c-997f-639492142356&sp_x_4=floorplanIdCRM&sp_q_4=0x0000000000000BB9&sp_x_9=upm.upm_startDate&sp_q_max_day_9=23&sp_q_max_month_9=05&sp_x_10=upm.upm_endDate&sp_q_min_day_10=24&sp_q_min_month_10=03&sp_q_min_year_10=2020&sp_q_max_year_9=2021

    # URL used for the query below
    #https://www.irvinecompanyapartments.com/bin/tic/ica/floorplanpricingavailability?app=icaFloorplanPage&sp_s=planName&sp_x_1=appId&sp_q_1=ica&sp_x_2=entityType&sp_q_2=unit&upm_field_table=1&sp_x_3=communityIdAEM&sp_q_3=055e718e-d752-4d4c-997f-639492142356&sp_x_4=floorUnitTypeCode&sp_q_4=22CP&sp_x_9=upm.upm_startDate&sp_q_max_day_9=22&sp_q_max_month_9=05&sp_x_10=upm.upm_endDate&sp_q_min_day_10=23&sp_q_min_month_10=03&sp_q_min_year_10=2020&sp_q_max_year_9=2021

    # the website looks to add 425 days to the current date for the query (roughly 14 months)
    now = datetime.now()

    if is_leap_year(now.year):
        td = timedelta(days=425)
    else:
        td = timedelta(days=424)
 
    future = now + td

    for key in guid:
        payload = {
            'app':               'icaFloorplanPage',
            'sp_s':              'planName',
            'sp_x_1':            'appId',
            'sp_q_1':            'ica',
            'sp_x_2':            'entityType',
            'sp_q_2':            'unit',
            'upm_field_table':   '1',
            'sp_x_3':            'communityIdAEM',
            'sp_q_3':            key,
            'sp_x_4':            'floorUnitTypeCode',
            'sp_q_4':            guid[key],
            # the upm.upm_startDate and upm.upm_endDate are a bit confusing.
            # Their roles look swapped.
            'sp_x_9':            'upm.upm_startDate',
            'sp_q_max_year_9':   f'{future.year:04d}',
            'sp_q_max_month_9':  f'{future.month:02d}',
            'sp_q_max_day_9':    f'{future.day:02d}',
            'sp_x_10':           'upm.upm_endDate',
            'sp_q_min_year_10':  f'{now.year:04d}',
            'sp_q_min_month_10': f'{now.month:02d}',
            'sp_q_min_day_10':   f'{now.day:02d}'
        }

        result = requests.get('https://www.irvinecompanyapartments.com/bin/tic/ica/floorplanpricingavailability', params=payload)
        data = result.json()
        #print(json.dumps(data, indent=4))

        total = data['total']
        for result in data['results']:
            print(f"Apartment: {result['unitMarketingName']}")
            print(f"Price: {result['unitBestPrice']}")
            print(f"Floor: {result['floorLevel']}")
            print(f"Date Available: {result['unitBestDate']}")
            print()



if __name__ == '__main__':
    main()
