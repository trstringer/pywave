import re
import sys
from bs4 import BeautifulSoup
import requests

class SwellData():
    def __init__(self, station_id, swell_height, swell_period, swell_direction):
        self.station_id = station_id
        self.swell_height = swell_height
        self.swell_period = swell_period
        self.swell_direction = swell_direction

    def __str__(self):
        return '{} ft @ {} s ({})'.format(
            self.swell_height, 
            self.swell_period, 
            self.swell_direction)

    @staticmethod
    def retrieve_station_data(station_id):
        req = requests.get('http://www.ndbc.noaa.gov/station_page.php?station={}'.format(station_id))

        if req.status_code != 200:
            print('Error fetching page! {}'.format(req.status_code))
            sys.exit(1)

        soup = BeautifulSoup(req.text, 'lxml')

        swell_data = SwellData(
            station_id,
            SwellData.parse_table_data(soup, r'Wave Height', True),
            SwellData.parse_table_data(soup, r'Swell Period', True),
            SwellData.parse_table_data(soup, r'Swell Direction', False))
        return swell_data
        
    @staticmethod
    def parse_table_data(soup, label_pattern, is_num):
        pattern = re.compile(label_pattern)
        element = soup.find(text=pattern)

        if element is None:
            return None

        next_element = element.next

        if next_element is None:
            return None

        element_data = str(re.sub(r'<(/)?td>', '', str(next_element))).strip()

        if is_num:
            return re.findall(r'\d+\.\d+', element_data)[0]
        else:
            return element_data

def main(station_id):
    swell_data = SwellData.retrieve_station_data(station_id)
    print(str(swell_data))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('You must specify the station ID as the first parameter')
        sys.exit(1)
    else:
        main(sys.argv[1])

