from collections import defaultdict
from typing import List, Dict, Tuple

import requests
from dateutil.parser import parse
from decouple import config


KEY = config('HERE_API_KEY')
STATIONS_URL = 'https://transit.hereapi.com/v8/departures'
GEOCODE_URL = 'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={key}&searchtext={search}'


def create_search_string(city: str, state: str, street_address: str = None) -> str:
    if not street_address:
        return f'{city} {state}'
    return f'{street_address} {city} {state}'


def get_lat_and_long(search: str) -> Tuple:
    """Determines the longitude and latitude for a given address.
       Address can be as simple as a city and state, or a full
       building address, i.e. '425 W Spring St Chicago IL'."""
    search = "+".join([s.lower() for s in search.split()])
    try:
        response = requests.get(GEOCODE_URL.format(key=KEY, search=search))
        coords = response.json()['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]
        return coords["Latitude"], coords['Longitude']
    except IndexError:
        return None


def _get_routes_and_stations(latitude: str, longitude: str) -> Dict:
    """Gets route information, including departure times
       and destinations for the given longitude and latitude
       coordinates."""
    if not latitude and not longitude:
        return
    params = {"apikey": KEY, "in": f"{latitude},{longitude}"}
    response = requests.get(STATIONS_URL, params=params)
    try:
        return response.json()['boards']
    except IndexError:
        return None


def prettify_time(time: str) -> str:
    """Takes a string timestamp and parses it into datetime.
       Then, does some checks to add a zero if the minutes are less
       than ten, and determines whether the time is AM or PM."""
    time = parse(time)
    minute = time.minute if len(str(time.minute)) == 2 else f'0{time.minute}'
    hour = time.hour if len(str(time.hour)) == 2 else f'0{time.hour}'

    if time.minute < 10:
        pretty_time = f'{time.year}-{time.month}-{time.day} @{hour}:{minute}'
    else:
        pretty_time = f'{time.year}-{time.month}-{time.day} @{hour}:{minute}'
    return f'{pretty_time} AM' if time.hour < 12 else f'{pretty_time} PM'


def collect_route_information(data: List) -> Dict:
    """Takes in the pertinent route information such as
       departure time, destination, mode of transportation,
       and transportation website, if applicable. Returns
       a defaultdict with a list of the information above,
       with its key set to a number, as in 'Route #1', etc."""
    result = defaultdict(list)
    i = 0

    try:
        for item in data:
            for route in item['departures']:
                route_ = route['transport']
                long_name = route_.get('longName')
                if long_name:
                    if long_name == route_['name']:
                        long_name = route_['headsign']
                
                if not long_name:
                    long_name = route_['headsign']
                temp = []
                time = prettify_time(route['time'])
                route_data = [time, route_['mode'], route_['name'], 
                                route_['headsign'], long_name, route['agency']['website']]
                temp.extend(route_data)
                result[i].append(temp)
            i += 1
        return result
    except TypeError:
        return None


def get_station_data(data: List) -> Dict:
    """Gets station data from available route data."""
    stations = {}
    i = 0
    for item in data:
        temp = []
        temp.append(item['place']['name'])
        temp.append(item['place']['location']['lat'])
        temp.append(item['place']['location']['lng'])
        stations[i] = temp
        i += 1
    return stations


def get_route_data(address: str) -> Dict:
    """A wrapper to collect the data from the above functions,
       so that only one function is called to get route information."""
    try:
        lat, long = get_lat_and_long(address)
    except TypeError:
        return None
    
    route_data = _get_routes_and_stations(lat, long)
    return collect_route_information(route_data)