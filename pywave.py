"""PyWave main module"""

import argparse
from datetime import datetime
import json
import re
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

def parse_last_updated(soup):
    """Parse last updated time"""

    last_updated_caption = [
        str(caption)
        for caption
        in soup.find_all('caption')
        if "Conditions at" in str(caption)
    ][0]
    last_updated_matches = re.search(
        r'.*(\d{4}) GMT on (\d{2}\/\d{2}\/\d{4}).*',
        last_updated_caption
    ).groups()
    last_updated = datetime.strptime(
        f'{last_updated_matches[0]} {last_updated_matches[1]}',
        '%H%M %m/%d/%Y'
    )
    return last_updated

def is_stale(last_updated):
    """Determine whether or not the data is stale"""

    return (datetime.utcnow() - last_updated).seconds >= (2 * 60 * 60)

def wind_data(station_id):
    """Retrieve and parse wind data"""

    station_url = create_station_url(station_id)
    req = requests.get(station_url)
    soup = BeautifulSoup(req.text, 'lxml')

    last_updated = parse_last_updated(soup)
    data_is_stale = is_stale(last_updated)

    wind_direction = re.search(
        r'^(\w+) \( (\d+) deg true \)$',
        parse_metric(soup, r'Wind Direction \(WDIR\):', verbose=True)
    )
    wind_direction_angle = wind_direction.group(2)
    wind_direction_indicator = wind_direction.group(1)
    wind_speed = re.search(
        r'^(\d+.*) kts$',
        parse_metric(soup, r'Wind Speed \(WSPD\):', verbose=True)
    ).group(1)
    air_temperature = re.search(
        r'^(\d+\.\d+) .*$',
        parse_metric(soup, r'Air Temperature \(ATMP\):', verbose=True)
    ).group(1)
    return dict(
        stale=data_is_stale,
        speed=wind_speed,
        temperature=air_temperature,
        direction=dict(
            angle=wind_direction_angle,
            indicator=wind_direction_indicator
        )
    )

def wave_data(station_id):
    """Retrieve and parse wave data"""

    station_url = create_station_url(station_id)
    req = requests.get(station_url)
    soup = BeautifulSoup(req.text, 'lxml')

    last_updated = parse_last_updated(soup)
    data_is_stale = is_stale(last_updated)

    wave_height = re.search(
        r'^(\d+.*) ft$',
        parse_metric(soup, r'Wave Height \(WVHT\):', verbose=True)
    ).group(1)
    wave_period = re.search(
        r'^(\d+) sec$',
        parse_metric(soup, r'Dominant Wave Period \(DPD\):', verbose=True)
    ).group(1)
    wave_direction = re.search(
        r'^(\w+) \( (\d+) deg true \)$',
        parse_metric(soup, r'Mean Wave Direction \(MWD\):', verbose=True)
    )
    wave_direction_angle = wave_direction.group(2)
    wave_direction_indicator = wave_direction.group(1)
    water_temperature = re.search(
        r'^(\d+\.\d+) .*$',
        parse_metric(soup, r'Water Temperature \(WTMP\):', verbose=True)
    ).group(1)
    return dict(
        stale=data_is_stale,
        height=wave_height,
        period=wave_period,
        temperature=water_temperature,
        direction=dict(
            angle=wave_direction_angle,
            indicator=wave_direction_indicator
        )
    )

def pretty_display(total_data):
    """Output data in a nice single line"""

    wave_height_symbol = wave_height_indicator(total_data['wave']['height'])
    wave_period_symbol = wave_period_indicator(total_data['wave']['period'])
    wave_direction_symbol = direction_indicator(total_data['wave']['direction']['indicator'])
    wind_direction_symbol = direction_indicator(total_data['wind']['direction']['indicator'])

    wave_is_stale = "⚠️" if total_data['wave']['stale'] else ""
    wind_is_stale = "⚠️" if total_data['wind']['stale'] else ""

    output_string = f'{wave_is_stale} {wave_height_symbol} {total_data["wave"]["height"]}\''
    output_string += f' {wave_direction_symbol} {total_data["wave"]["direction"]["indicator"]}'
    output_string += f' @ {total_data["wave"]["period"]}s {wave_period_symbol}'
    output_string += f' {wind_is_stale} 💨 {total_data["wind"]["speed"]}kt {wind_direction_symbol}'
    output_string += f' {total_data["wind"]["direction"]["indicator"]}'

    print(output_string)

def wave_height_indicator(wave_height):
    """Convert wave height to an indicator"""

    wave_height = float(wave_height)
    if wave_height <= 1:
        return "💛💛💛💛"
    elif 1 < wave_height <= 3:
        return "💙💛💛💛"
    elif 3 < wave_height <= 5:
        return "💙💙💛💛"
    elif 5 < wave_height <= 8:
        return "💙💙💙💛"
    elif wave_height > 8:
        return "💙💙💙💙"

def direction_indicator(direction):
    """Convert direction to indicator"""

    if direction == "N":
        return "⬇️ ⬇️"
    elif direction == "NNE":
        return "⬇️ ↙️"
    elif direction == "NE":
        return "↙️ ↙️"
    elif direction == "ENE":
        return "⬅️ ↙️"
    elif direction == "E":
        return "⬅️ ⬅️"
    elif direction == "ESE":
        return "⬅️ ↖️"
    elif direction == "SE":
        return "↖️ ↖️"
    elif direction == "SSE":
        return "⬆️ ↖️"
    elif direction == "S":
        return "⬆️ ⬆️"
    elif direction == "SSW":
        return "⬆️ ↗️"
    elif direction == "SW":
        return "↗️ ↗️"
    elif direction == "WSW":
        return "➡️ ↗️"
    elif direction == "W":
        return "➡️ ➡️"
    elif direction == "WNW":
        return "➡️ ↘️"
    elif direction == "NW":
        return "↘️ ↘️"
    elif direction == "NNW":
        return "⬇️ ↘️"
    else:
        return "❓"

def wave_period_indicator(wave_period):
    """Convert wave period to an indicator"""

    wave_period = int(wave_period)
    if wave_period <= 6:
        return "🔴"
    elif 6 < wave_period <= 9:
        return "🟡"
    elif wave_period > 9:
        return "🟢"

def main():
    """Main code execution"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--wave-station', help='wave station id')
    parser.add_argument('-w', '--wind-station', help='wind station id')
    parser.add_argument('-v', '--verbose', help='show verbose output', action='store_true')
    parser.add_argument('-p', '--pretty', help='pretty output', action='store_true')
    args = parser.parse_args()

    if args.wave_station:
        wave_info = wave_data(station_id=args.wave_station)
    if args.wind_station:
        wind_info = wind_data(station_id=args.wind_station)

    total_data=dict(wave=wave_info, wind=wind_info)

    if args.pretty:
        pretty_display(total_data)
    else:
        print(json.dumps(total_data, indent=2))

if __name__ == '__main__':
    main()
