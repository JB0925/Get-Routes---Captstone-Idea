import re
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

import requests # type: ignore
from dateutil.parser import parse # type: ignore
from decouple import config # type: ignore
import googlemaps # type: ignore

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


def get_lat_and_long(search: str) -> Optional[Tuple]:
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


def _get_routes_and_stations(latitude: float, longitude: float) -> Optional[List]:
    """
    Gets route information, including departure times
    and destinations for the given longitude and latitude
    coordinates.
    """
    if not latitude and not longitude:
        return None
    params = {"apikey": KEY, "in": f"{latitude},{longitude}"}
    response = requests.get(STATIONS_URL, params=params)
    return response.json().get('boards')


def prettify_time(time: str) -> str:
    """
    Takes a string timestamp and parses it into datetime.
    Then, does some checks to add a zero if the minutes are less
    than ten, and determines whether the time is AM or PM.
    """
    datetime_time = parse(time)
    parts_of_time = [datetime_time.minute, datetime_time.hour, datetime_time.month, datetime_time.day]
    
    for i in range(len(parts_of_time)):
        parts_of_time[i] = parts_of_time[i] if len(str(parts_of_time[i])) == 2 else f'0{parts_of_time[i]}'

    minute, hour, month, day = parts_of_time
    pretty_time = f'{datetime_time.year}-{month}-{day} @{hour}:{minute}'
    return f'{pretty_time} AM' if datetime_time.hour < 12 else f'{pretty_time} PM'


def determine_long_form_route_name(route: Dict) -> str:
    """
    Method used to abstract some of the complexity out
    of the function below, 'collect_route_information.
    returns a string that is used to store in a dictionary
    that will be sent client side. Gets the most descriptive
    name of the route, which will then be passed to
    get_lat_and_lng.
    """
    long_form_name = route.get('longName')
    headsign = route['headsign'].replace("To", "")
    if not long_form_name:
        return headsign
    
    long_form_name = long_form_name.replace("To", "")
    return headsign if long_form_name == route['name'] else long_form_name


def collect_route_information(data: Optional[List]) -> Optional[Dict]:
    """
    Takes in the pertinent route information such as
    departure time, destination, mode of transportation,
    and transportation website, if applicable. Returns
    a defaultdict with a list of the information above,
    with its key set to a number, as in 'Route #1', etc.
    """
    result = defaultdict(list)
    i = 0
    if data is None:
        return None

    try:
        for item in data:
            temp = []
            for route in item['departures']:
                route_ = route['transport']
                long_name = determine_long_form_route_name(route_)
                time = prettify_time(route['time'])
                website = route['agency'].get('website', 'None Provided')
                route_data = [time, route_['mode'], route_['name'], 
                                route_['headsign'], long_name, website]
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


def get_route_data(address: str) -> Optional[Dict]:
    """
    A wrapper to collect the data from the above functions,
    so that only one function is called to get route information.
    """
    try:
        lat, long = get_lat_and_long(address) # type: ignore
    except TypeError:
        return None
    
    route_data = _get_routes_and_stations(lat, long)
    return collect_route_information(route_data)


def create_destination_coordinates_fallback(data: List, address: str, origin_coords: Dict) -> Tuple:
    """
    A method to generate the correct coordinates (or a close estimation) for a destination
    based on factors such as transportation mode, etc. Accounts for situations in which addresses
    are formed and no coordinates are found by simply returning the origin coordinates. This
    is only to be used in case the API does not return coordinates for the given destination.
    """
    transit_types = ['bus', 'subway', 'ferry', 'lightRail']
    start_coords = (float(origin_coords['latitude']), float(origin_coords['longitude']))
    transit_method = data[1]
    destination_place_name = data[3]

    if transit_method in transit_types:
        destination_coords = get_lat_and_long(f'{destination_place_name} {address}') or start_coords
        if abs(destination_coords[0] - float(origin_coords['latitude'])) > 1.5:
            return start_coords
        else:
            return destination_coords
    
    train_coords = get_lat_and_long(destination_place_name)
    return train_coords if train_coords else start_coords


def get_directions_to_station(start_address: str, station_address: str) -> List[str]:
    """
    Method used to get directions from the address the user inputs
    to the station found via the HERE API.
    """
    directions = GMAPS.directions(start_address, station_address)[0]['legs'][0]['steps']
    pattern = r'(<b>)|(</b>)|(<div>)|(</div>)|(<div[\w\W]+>)|(<wbr/>)'
    return [re.sub(pattern, '', direction['html_instructions']) for direction in directions]


def get_destination_coordinates(address: str, start_coords: Dict) -> Optional[Dict]:
    """
    Gets the most accurate sets of destination coordinates, as the data comes straight
    from the API. If it cannot find, it we fall back on using Google's Geocoding
    API to get the destination coordinates. See above.
    """
    start_lat, start_lng = start_coords["latitude"], start_coords["longitude"]
    try:
        destination_lat2, destination_lng2 = get_lat_and_long(address) #type: ignore
    except Exception:
        # if we can't get coordinates with the full address, we return None
        # and use the fallback method
        return None

    route_url = 'https://transit.router.hereapi.com/v8/routes'
    params = {'apikey': KEY, 'origin': f'{start_lat},{start_lng}', 
              'destination': f'{destination_lat2},{destination_lng2}'}

    resp = requests.get(route_url, params=params).json()
    try:
        final_stop_coords = resp['routes'][0]['sections'][-1]['arrival']['place']['location']
    except IndexError:
        # if the above throws an error, we catch it, and move on to trying our fallback method
        return None

    return final_stop_coords["lat"], final_stop_coords["lng"] #type: ignore


def save_route_data_to_db(routes: List[List[str]], coords_dict: Dict, user: User, origin: OriginInfo) -> List[str]:
    """
    As the function name says, this method collects all the data, bundles it up, 
    and saves it all to the database. Returns a list of the route names, used in
    the Jinja template.
    """
    route_names = []

    for route in routes:
        route_names.append(route[2])
        address = f"{route[4]}, {origin.city_and_state}"

        # try to get the coordinates from the HERE api, but if they aren't available,
        # use the fallback method so that the app does not crash
        try:
            lat, lng = get_destination_coordinates(address, coords_dict)  # type: ignore
        
        except (TypeError, AttributeError):
            lat, lng = create_destination_coordinates_fallback(route, origin.city_and_state, coords_dict)
    
        new_search = Search(time=route[0], transportation_mode=route[1],
                                destination=route[4], website=route[5], user_id=user.id)
        new_route = RouteData(time=route[0], name=route[1], mode=route[2], headsign=route[3], 
                                long_name=route[4], website=route[5], latitude=str(lat), longitude=str(lng),
                                user_id=user.id)
        db.session.add(new_search)
        db.session.add(new_route)
    db.session.commit()
    
    return route_names