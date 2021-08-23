from typing import Dict, List, Tuple
from unittest import TestCase

from decouple import config
import googlemaps

import get_routes as gr


KEY = config('HERE_API_KEY')
STATIONS_URL = 'https://transit.hereapi.com/v8/departures'
GEOCODE_URL = 'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={key}&searchtext={search}'
GMAPS = googlemaps.Client(key=config('API_KEY'))


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
        addresses = self.mock_addresses()
        self.assertEqual(gr.create_search_string_for_station_search(**addresses["address1"]), "Culpeper VA")
        self.assertEqual(gr.create_search_string_for_station_search(**addresses["address2"]), "1600 Pennsylvania Ave Washington DC")
        self.assertEqual(gr.create_search_string_for_station_search(**addresses["address3"]), "rtyue home blvd blahlalabah xD")


    def test_prettify_time(self):
        for actual, expected in self.mock_times():
            self.assertEqual(gr.prettify_time(actual), expected)
    

    def test_get_lat_and_long(self):
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
        i = 0
        for lat, lng in self.mock_coordinates():
            self.assertEqual(type(gr._get_routes_and_stations(lat,lng)), list)