import re
from collections import defaultdict
from typing import List, Dict, Tuple

import requests
from dateutil.parser import parse
from decouple import config
import googlemaps

from models import db, Search, RouteData, OriginInfo, User


KEY = config('HERE_API_KEY')
STATIONS_URL = 'https://transit.hereapi.com/v8/departures'
GEOCODE_URL = 'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={key}&searchtext={search}'
GMAPS = googlemaps.Client(key=config('GOOGLE_API_KEY'))

def create_search_string_for_station_search(city: str, state: str, street_address: str = None) -> str:
    """
    Gathers form data and creates a concatenated address from it,
    depending on whether or not a street address was entered in.
    """
    if not street_address:
        return f'{city} {state}'
    return f'{street_address} {city} {state}'


def get_lat_and_long(search: str) -> Tuple:
    """
    Determines the longitude and latitude for a given address.
    Address can be as simple as a city and state, or a full
    building address, i.e. '425 W Spring St Chicago IL'.
    """
    search = "+".join([s.lower() for s in search.split()])
    
    try:
        geocoords = GMAPS.geocode(search)[0]['geometry']['location']
        return geocoords['lat'], geocoords['lng']

    except IndexError:
        return None


def _get_routes_and_stations(latitude: float, longitude: float) -> Dict:
    """
    Gets route information, including departure times
    and destinations for the given longitude and latitude
    coordinates.
    """
    if not latitude and not longitude:
        return
    params = {"apikey": KEY, "in": f"{latitude},{longitude}"}
    response = requests.get(STATIONS_URL, params=params)
    
    try:
        return response.json()['boards']
    except IndexError:
        return None


def prettify_time(time: str) -> str:
    """
    Takes a string timestamp and parses it into datetime.
    Then, does some checks to add a zero if the minutes are less
    than ten, and determines whether the time is AM or PM.
    """
    time = parse(time)
    minute = time.minute if len(str(time.minute)) == 2 else f'0{time.minute}'
    hour = time.hour if len(str(time.hour)) == 2 else f'0{time.hour}'
    month = time.month if len(str(time.month)) == 2 else f'0{time.month}'
    day = time.day if len(str(time.day)) == 2 else f'0{time.day}'

    if time.minute < 10:
        pretty_time = f'{time.year}-{month}-{day} @{hour}:{minute}'
    else:
        pretty_time = f'{time.year}-{month}-{day} @{hour}:{minute}'
    return f'{pretty_time} AM' if time.hour < 12 else f'{pretty_time} PM'


def determine_long_form_route_name(route: Dict) -> str:
    """
    Method used to abstract some of the complexity out
    of the function below, 'collect_route_information.
    returns a string that is used to store in a dictionary
    that will be sent client side.
    """
    long_form_name = route.get('longName')
    if not long_form_name:
        return route['headsign']
    
    if long_form_name == route['name']:
        return route['headsign']
    return long_form_name


def collect_route_information(data: List) -> Dict:
    """
    Takes in the pertinent route information such as
    departure time, destination, mode of transportation,
    and transportation website, if applicable. Returns
    a defaultdict with a list of the information above,
    with its key set to a number, as in 'Route #1', etc.
    """
    result = defaultdict(list)
    i = 0

    try:
        for item in data:
            temp = []
            for route in item['departures']:
                route_ = route['transport']
                long_name = determine_long_form_route_name(route_)
                time = prettify_time(route['time'])
                route_data = [time, route_['mode'], route_['name'], 
                                route_['headsign'], long_name, route['agency']['website']]
                temp.append(route_data)
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
    """
    A wrapper to collect the data from the above functions,
    so that only one function is called to get route information.
    """
    try:
        lat, long = get_lat_and_long(address)
    except TypeError:
        return None
    
    route_data = _get_routes_and_stations(lat, long)
    return collect_route_information(route_data)


def create_correct_destination_coordinates(data: List, address: str, origin_coords: Dict) -> Tuple:
    """
    A method to generate the correct coordinates (or a close estimation) for a destination
    based on factors such as transportation mode, etc. Accounts for situations in which addresses
    are formed and no coordinates are found by simply returning the origin coordinates.
    """
    transit_types = ['bus', 'subway', 'ferry', 'lightRail']
    start_coords = (float(origin_coords['latitude']), float(origin_coords['longitude']))
    if data[1] in transit_types:
        destination_coords = get_lat_and_long(f'{data[3]} {address}') or start_coords
        if abs(destination_coords[0] - float(origin_coords['latitude'])) > 1.5:
            return start_coords
        else:
            return destination_coords
    
    train_coords = get_lat_and_long(data[3])
    return train_coords if train_coords else start_coords


def get_directions_to_station(start_address: str, station_address: str) -> List[str]:
    """
    Method used to get directions from the address the user inputs
    to the station found via the HERE API.
    """
    directions = GMAPS.directions(start_address, station_address)[0]['legs'][0]['steps']
    pattern = r'(<b>)|(</b>)|(<div>)|(</div>)|(<div[\w\W]+>)|(<wbr/>)'
    return [re.sub(pattern, '', direction['html_instructions']) for direction in directions]


def save_route_data_to_db(routes: List, coords_dict: Dict, user: User, origin: OriginInfo) -> None:
    route_names = []

    for key in routes:
        route_names.append(key[2])
        lat, lng= create_correct_destination_coordinates(key, origin.city_and_state, coords_dict)
    
        new_search = Search(time=key[0], transportation_mode=key[1],
                                destination=key[4], website=key[5], user_id=user.id)
        new_route = RouteData(time=key[0], name=key[1], mode=key[2], headsign=key[3], 
                                long_name=key[4], website=key[5], latitude=str(lat), longitude=str(lng))
        db.session.add(new_search)
        db.session.add(new_route)
    db.session.commit()
    
    return route_names