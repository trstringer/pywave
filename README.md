# pywave

*NDBC Buoy Data Scraper*

## Installation and Configuration

1. Clone the repository: `$ git clone https://github.com/tstringer/pywave.git`
1. Navigate to the new dir: `$ cd pywave`
1. Modify permission on the install file: `$ chmod 755 ./install`
1. Kick off the installation: `$ ./install`

> :bulb: Note, this requires that `~/.local/bin` is an existing directory, and also requires python3

## Usage

```
$ pywave -s <WAVE_BUOY_STATION_ID> -w <WIND_BUOY_STATION_ID> -p
```

*Note: Get station IDs from http://www.ndbc.noaa.gov/*
