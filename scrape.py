#!/usr/bin/env python3

import json
import requests
from datetime import datetime, timedelta


class IrvineApartments:
    def __init__(self, community_name=None, property_name=None, plan_name=None):
        self.apartment_ids = 'apartment_ids.json'
        self.api_floorplan_url = 'https://www.irvinecompanyapartments.com/snp'
        self.api_floorplan_pricing_url = 'https://www.irvinecompanyapartments.com/bin/tic/ica/floorplanpricingavailability'
        self.community_name = community_name
        self.plan_name = plan_name
        self.property_name = property_name

        self.id_string = self._gen_id_string(community_name=self.community_name, property_name=self.property_name)
        self.guid = self._get_floorplan_guids(plan_name=self.plan_name)
        self.available_apartments = self._get_floorplan_pricing()

    def _gen_id_string(self, community_name=None, property_name=None):
        try:
            with open(self.apartment_ids) as f:
                apartments = json.loads(f.read())
        except Exception as e:
            print(e, file=stderr)
            exit(1)

        id_string = []

        for community in apartments:
            for property in apartments[community]:
                if community_name and community_name == community:
                    if property_name and property_name == property:
                        id_string.append(apartments[community][property])
                    else:
                        id_string.append(apartments[community][property])
                else:
                    id_string.append(apartments[community][property])

        return id_string

    def _get_floorplan_guids(self, plan_name=None):
        payload = {
            'app':          'ica',
            'count':        '999',
            'sp_s':         'planName',
            'sp_x_1':       'appId',
            'sp_q_1':       'ica',
            'sp_x_2':       'entityType',
            'sp_q_2':       'floorplan',
            'sp_x_3':       'propertyIdCRM',
            'sp_q_exact_3': '|'.join(self.id_string)
        }

        try:
            result = requests.get(self.api_floorplan_url, params=payload)
        except Exception as e:
            print(e, file=stderr)
            exit(1)
        
        data = result.json()
        guid = {}

        for resultset in data['resultsets']:
            for result in resultset['results']:
                if plan_name and result['planName'] == plan_name:
                    guid[result['communityIdAEM']] = result['floorUnitTypeCode']
                elif plan_name is None:
                    guid[result['communityIdAEM']] = result['floorUnitTypeCode']

        return guid

    def _get_floorplan_pricing(self):
        now = datetime.now()

        # the website expects 424 days (425 if leap year) added to the current date (roughly 14 months)
        if self._is_leap_year(now.year):
            td = timedelta(days=425)
        else:
            td = timedelta(days=424)

        future = now + td

        for key in self.guid:
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
                'sp_q_4':            self.guid[key],
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

            result = requests.get(self.api_floorplan_pricing_url, params=payload)
            data = result.json()

            total = data['total']
            if total != 0:
                print(f'Total: {total}')

            for result in data['results']:
                print(f"Apartment: {result['unitMarketingName']}")
                print(f"Price: {result['unitBestPrice']}")
                print(f"Floor: {result['floorLevel']}")
                print(f"Date Available: {result['unitBestDate']}")
                print()

    def _is_leap_year(self, year):
        if ((year % 4 == 0 and year % 100 != 0) or year % 400 == 0):
            return True
        else:
            return False


def main():
    print('Westview Plan P')
    test = IrvineApartments(community_name='Westview', plan_name='P')
    #print(test.available_apartments)

    print('Los Olivos Plan J')
    test = IrvineApartments(community_name='Los Olivos', plan_name='J')
    #print(test.available_apartments)

    print('Los Olivos Plan W')
    test = IrvineApartments(community_name='Los Olivos', plan_name='W')
    #print(test.available_apartments)


if __name__ == '__main__':
    main()
