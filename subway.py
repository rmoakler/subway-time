from google.transit import gtfs_realtime_pb2
import requests
import time # imports module for Epoch/GMT time conversion
import os # imports package for dotenv
import json
import datetime


dir = '/home/moaklero/www/subway-time/'
# dir = '/Users/robert/Documents/Projects/subway-time/'

# Station codes: http://web.mta.info/developers/data/nyct/subway/Stations.csv
stations = {'R20N': {'name': 'Union Sq', 'times': {'N': [], 'Q': [], 'R': []}},
            'R20S': {'name': 'Union Sq', 'times': {'N': [], 'Q': [], 'R': []}},
            'R24N': {'name': 'City Hall', 'times': {'N': [], 'Q': [], 'R': []}},
            'R24S': {'name': 'City Hall', 'times': {'N': [], 'Q': [], 'R': []}},
            'R29N': {'name': 'Jay St.', 'times': {'N': [], 'Q': [], 'R': []}},
            'R29S': {'name': 'Jay St.', 'times': {'N': [], 'Q': [], 'R': []}},
            'R30N': {'name': 'DeKalb', 'times': {'N': [], 'Q': [], 'R': []}},
            'R30S': {'name': 'DeKalb', 'times': {'N': [], 'Q': [], 'R': []}},
            'R36N': {'name': '36th St.', 'times': {'N': [], 'Q': [], 'R': []}},
            'R36S': {'name': '36th St.', 'times': {'N': [], 'Q': [], 'R': []}},
            'R41N': {'name': '59th St.', 'times': {'N': [], 'Q': [], 'R': []}},
            'R41S': {'name': '59th St.', 'times': {'N': [], 'Q': [], 'R': []}},
            'R45N': {'name': '95th St.',  'times': {'N': [], 'Q': [], 'R': []}}}

key_file = open(dir + "mta.key", "r")
key = key_file.readline().rstrip('\n')

# Requests subway status data feed from City of New York MTA API
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('http://datamine.mta.info/mta_esi.php?key={}&feed_id=16'.format(key))
feed.ParseFromString(response.content)

# The MTA data feed uses the General Transit Feed Specification (GTFS) which
# is based upon Google's "protocol buffer" data format. While possible to
# manipulate this data natively in python, it is far easier to use the
# "pip install --upgrade gtfs-realtime-bindings" library which can be found on pypi
from protobuf_to_dict import protobuf_to_dict
subway_feed = protobuf_to_dict(feed) # subway_feed is a dictionary
realtime_data = subway_feed['entity'] # train_data is a list

# Because the data feed includes multiple arrival times for a given station
# a global list needs to be created to collect the various times
collected_times = []

for i, trains in enumerate(realtime_data): # trains are dictionaries
    if trains.get('trip_update', False):
        train_id = trains['id']
        unique_train_schedule = trains['trip_update'] # train_schedule is a dictionary with trip and stop_time_update
        if unique_train_schedule.get('stop_time_update', False):
            unique_arrival_times = unique_train_schedule['stop_time_update'] # arrival_times is a list of arrivals
            for scheduled_arrivals in unique_arrival_times: #arrivals are dictionaries with time data and stop_ids
                if scheduled_arrivals.get('stop_id', False) in stations.keys():
                    station_id = scheduled_arrivals['stop_id']
                    current_time = int(time.time())
                    time_until_train = int(((scheduled_arrivals['departure']['time'] - current_time) / 60))
                    if time_until_train >= 0 and time_until_train <= 30:
                        stations[station_id]['times'][train_id[-1]] += [time_until_train]

for station in stations:
    for train in stations[station]['times']:
        stations[station]['times'][train] = sorted(stations[station]['times'][train])

header = '{:>9}  {:<7}     {:<7}     {:<7}\n'.format('', ' N', ' Q', ' R')

def time_format(station, stations):
    times = '{:>9}  {:>2}, {:>2}, {:>2}  {:>2}, {:>2}, {:>2}  {:>2}, {:>2}, {:>2} \n'.format(
        stations[station]['name'],
        stations[station]['times']['N'][0] if len(stations[station]['times']['N']) > 0 else '-',
        stations[station]['times']['N'][1] if len(stations[station]['times']['N']) > 1 else '-',
        stations[station]['times']['N'][2] if len(stations[station]['times']['N']) > 2 else '-',
        stations[station]['times']['Q'][0] if len(stations[station]['times']['Q']) > 0 else '-',
        stations[station]['times']['Q'][1] if len(stations[station]['times']['Q']) > 1 else '-',
        stations[station]['times']['Q'][2] if len(stations[station]['times']['Q']) > 2 else '-',
        stations[station]['times']['R'][0] if len(stations[station]['times']['R']) > 0 else '-',
        stations[station]['times']['R'][1] if len(stations[station]['times']['R']) > 1 else '-',
        stations[station]['times']['R'][2] if len(stations[station]['times']['R']) > 2 else '-')
    return times


# file = open("/home/moaklero/www/subway.txt", "w")
file = open(dir + "subway.txt", "w")

file.write('Last updated: {}\n\n'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %-I:%M:%S%p')))


file.write('Going to work\n')
file.write(header)
file.write(time_format('R45N', stations))
file.write(time_format('R41N', stations))
file.write(time_format('R36N', stations))
file.write(time_format('R30N', stations))
file.write(time_format('R29N', stations))
file.write(time_format('R24N', stations))
file.write(time_format('R20N', stations))

file.write('\nGoing home\n')
file.write(header)
file.write(time_format('R20S', stations))
file.write(time_format('R29S', stations))
file.write(time_format('R24S', stations))
file.write(time_format('R30S', stations))
file.write(time_format('R36S', stations))
file.write(time_format('R41S', stations))

file.close()
