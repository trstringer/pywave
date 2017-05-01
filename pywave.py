import argparse
import re
import sys
from bs4 import BeautifulSoup
import requests

def create_station_url(station_id):
    """Create the url for the station buoy data"""

    return 'http://www.ndbc.noaa.gov/station_page.php?station={}'.format(station_id)

def parse_metric(soup, search_regex, verbose=False):
    """Parse the wave height from the web page"""

    # import pdb; pdb.set_trace()
    search_labels = [
        _ for _ in soup.find_all('td')
        if re.search(r'<td>{}</td>'.format(search_regex), str(_))
        and len(str(_).split('\n')) == 1
    ]

    if len(search_labels) != 1:
        if verbose:
            print(
                'Unexpected length of matched "{}" : {}'
                .format(search_regex, len(search_labels))
            )
        return None

    return search_labels[0].find_next_sibling('td').text.strip()

def main():
    """Main code execution"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--station', help='station id')
    parser.add_argument('-v', '--verbose', help='show verbose output', action='store_true')
    args = parser.parse_args()

    if args.station:
        station_url = create_station_url(args.station)
        req = requests.get(station_url)
        soup = BeautifulSoup(req.text, 'lxml')
        print(
            '{} @ {} [{}]'.format(
                parse_metric(soup, r'Wave Height \(WVHT\):', verbose=True),
                parse_metric(soup, r'Dominant Wave Period \(DPD\):', verbose=True),
                parse_metric(soup, r'Mean Wave Direction \(MWD\):', verbose=True)
            ))

if __name__ == '__main__':
    main()
