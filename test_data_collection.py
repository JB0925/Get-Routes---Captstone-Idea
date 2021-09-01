from typing import Dict, List, Tuple
from unittest import TestCase

from decouple import config
import googlemaps

import get_routes as gr


KEY = config('HERE_API_KEY')
STATIONS_URL = 'https://transit.hereapi.com/v8/departures'
GEOCODE_URL = 'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={key}&searchtext={search}'
GMAPS = googlemaps.Client(key=config('GOOGLE_API_KEY'))


class GetRouteInfoTestCase(TestCase):
    def mock_addresses(self) -> Dict:
        return {
            "address1": {
            "city": "Culpeper",
            "state": "VA"
            },

            "address2": {
                "city": "Washington",
                "state": "DC",
                "street_address": "1600 Pennsylvania Ave"
            },

            "address3": {
                "city": "blahlalabah",
                "state": "xD",
                "street_address": "rtyue home blvd"
            }
        }
    

    def mock_coordinates(self) -> List[Tuple]:
        return [
            (38.4733, -77.9961),
            (38.897676, -77.036482)
        ]
    

    def mock_times(self) -> List[Tuple[str]]:
        return [
            ("2021-08-23T05:35:42", "2021-08-23 @05:35 AM"),
            ("2021-06-07T11:09:34", "2021-06-07 @11:09 AM")
        ]


    def test_create_search_strings(self):
        """
        Does the function for making nicely formatted search strings
        work as intended, given varying inputs?
        """
        addresses = self.mock_addresses()
        self.assertEqual(gr.create_search_string_for_station_search(**addresses["address1"]), "Culpeper VA")
        self.assertEqual(gr.create_search_string_for_station_search(**addresses["address2"]), "1600 Pennsylvania Ave Washington DC")
        self.assertEqual(gr.create_search_string_for_station_search(**addresses["address3"]), "rtyue home blvd blahlalabah xD")


    def test_prettify_time(self):
        """
        Does the function for making nicely formatted time strings work as expected?
        """
        for actual, expected in self.mock_times():
            self.assertEqual(gr.prettify_time(actual), expected)
    

    def test_get_lat_and_long(self):
        """
        Does the get_lat_and_lng method return the appropriate 
        type of data, given varying addresses?
        """
        addresses = self.mock_addresses()
        i = 0
        for a in addresses:
            search = gr.create_search_string_for_station_search(**addresses[a])
            if i == 2:
                self.assertEqual(gr.get_lat_and_long(search), None)
            else:
                self.assertEqual(type(gr.get_lat_and_long(search)), tuple)
            i += 1
    

    def test_get_routes_and_stations(self):
        """
        Does the method for getting raw station and route data work
        when given good data?
        """
        for lat, lng in self.mock_coordinates():
            self.assertEqual(type(gr._get_routes_and_stations(lat,lng)), list)
    
    
    def test_get_routes_and_stations_bad_coords(self):
        """Does the method that collects the raw data handle bad coordinates appropriately?"""
        self.assertEqual(gr._get_routes_and_stations(456.3222, 1004.9), None)
    

    def test_function_integrations(self):
        """
        Does the way that get_lat_and_lng, _get_routes_and_stations,
        and collect_route_data are set up work well together?
        """
        data = gr.get_route_data('Pittsburgh, PA')
        self.assertEqual(len(data), 5)
        self.assertIsNotNone(data[0][0][4])
    

    def test_longname_extraction(self):
        """
        Does the function for getting the most descriptive name work as intended?
        """
        dict1 = {
            'headsign': "my route",
            'name': 'something else'
        }

        dict2 = {
            'headsign': 'my route',
            'name': 'something else',
            'longName': 'something else'
        }

        dict3 = {
            'headsign': 'my route',
            'name': 'something else',
            'longName': 'the best choice'
        }

        res1 = gr.determine_long_form_route_name(dict1)
        res2 = gr.determine_long_form_route_name(dict2)
        res3 = gr.determine_long_form_route_name(dict3)
        self.assertEqual(res1, 'my route')
        self.assertEqual(res2, 'my route')
        self.assertEqual(res3, 'the best choice')
    

    def test_create_destination_coords(self):
        """
        Does the create_destination_coords method
        create reasonable destination coordinates,
        given the type of transit and distance between
        start and endpoints?
        """
        data = ['Grant St', 'bus', 'S13', 'Grant St Pittsburgh']
        origin_coords = {'latitude': 40.441414, 'longitude': -79.994708}
        address = 'Pittsburgh, PA'
        data2 = ['Boston', 'regionalTrain', 'Crescent', 'Boston South Station']
        address2 = 'Culpeper, VA'
        origin_coords2 = {'latitude': 38.156, 'longitude': -77.25}
        lat, lng = gr.create_correct_destination_coordinates(data, address, origin_coords)
        lat2, lng2 = gr.create_correct_destination_coordinates(data2, address2, origin_coords2)
        self.assertTrue(abs(origin_coords['latitude'] - lat) <= 1.5)
        self.assertTrue(abs(origin_coords['longitude'] - lng) <= 1.5)
        self.assertTrue(abs(origin_coords2['latitude'] - lat2) >= 1.5)
        self.assertTrue(abs(origin_coords2['longitude'] - lng2) >= 1.5)
    

    def test_get_station_data(self):
        """
        Does the "get_station_data" function return good data,
        given good arguments?
        """
        data = [
            {
                'place': {
                    'name': 'Culpeper Amtrak Station',
                    'location': {
                        'lat': 38.75,
                        'lng': -77.25
                    }
                }
            }
        ]

        actual = gr.get_station_data(data)
        expected = {
            0: [
                'Culpeper Amtrak Station',
                38.75,
                -77.25
            ]
        }

        self.assertEqual(actual, expected)


    def test_get_directions(self):
        """
        Does the regex appropriately parse and replace
        the directions returned from the Google API?
        """
        start_address = 'Culpeper, VA'
        station_address = 'Culpeper Amtrak Station'
        directions = GMAPS.directions(start_address, station_address)[0]['legs'][0]['steps']
        direction = directions[0]['html_instructions']
        self.assertIn('<b>', direction)
        expected_directions = gr.get_directions_to_station(start_address, station_address)
        self.assertNotIn('<b>', expected_directions)