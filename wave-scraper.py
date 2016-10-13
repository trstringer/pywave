#!/usr/bin/env python3

import re
import sys
from bs4 import BeautifulSoup
import requests

class SwellData():
    def __init__(self, station_id):
        self.station_id = station_id

    def retrieve_station_data(self):
        req = requests.get('http://www.ndbc.noaa.gov/station_page.php?station={}'.format(self.station_id))

        if req.status_code != 200:
            print('Error fetching page! {}'.format(req.status_code))
            sys.exit(1)

        soup = BeautifulSoup(req.text, 'lxml')

        data_to_parse = [r'Swell Height', r'Swell Period', r'Swell Direction']
        for label in data_to_parse:
            print(label, end=' :: ')
            print(parse_table_data(soup, label))

    def parse_table_data(self, soup, label_pattern):
        pattern = re.compile(label_pattern)
        element = soup.find(text=pattern)

        if element is None:
            return None

        next_element = element.next

        if next_element is None:
            return None

        return str(re.sub(r'<(/)?td>', '', str(next_element))).strip()

        
def main(station_id):
    retrieve_station_data(station_id)

if __name__ == '__main__':
    main(sys.argv[1])

