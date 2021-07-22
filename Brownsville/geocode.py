from os import name
from typing import Dict, Iterable, Tuple
from numpy.lib.function_base import iterable
import yaml
import requests
import json

from yaml.tokens import Token

TOKEN = "AK8TJhhyXgTFJAej0DI7vQUNNigCkm8z"

class GeocodeClient:

    BASE_URL = "http://www.mapquestapi.com/geocoding/v1/address"

    def __init__(self, token:str) -> None:
        self.__token = token


    def get_lat_lng(self, street_address:str, city:str, state:str, zip_code:int) -> Tuple[float, float]:
        """
        Makes a geocode API call to fetch the coordinates of the specified address.

        Paramters:
        ----------
        street_address: `str`
            Street name to search the coordinates.
        city: `str`
            City name to search the coordinates.
        state: `str`
            State name to search the coordinates.
        zip_code: `int`
            Zip code to search the coordinates.
        """
        url = self.parse_query(
            key=self.__token,
            location=[street_address, city, state, zip_code]
        )

        response = requests.get(url)
        
        results = json.loads(response.content)["results"][0]["locations"][0]
        lat, lng = results["latLng"].values()

        return lat, lng

    def parse_query(self, **kwargs) -> str:
        """
        Parses the query arguments to construct a valid API call
        """
        q = []
        for key in kwargs:

            value = kwargs[key]
            
            if not isinstance(value, str) and isinstance(value, Iterable):
                value = [str(item).replace(' ', '+').title() for item in value]
                value = ",".join(value)

            q.append(f"{key}={value}")
        
        url = f"{GeocodeClient.BASE_URL}?" + "&".join(q)
        return url

if __name__ == "__main__":
    # print(get_lat_lng('1600 Pennsylvania Ave NW', 'washington', 'dc', '20500'))
    g = GeocodeClient(token=TOKEN)
    print(g.get_lat_lng('1 Remsen Avenue', 'brooklyn', 'ny', '11212'))