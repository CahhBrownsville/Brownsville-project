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

    def __init__(self, token:str=None) -> None:
        if not token:
            token = TOKEN
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

    def get_zip(self, street_address:str, city:str, state:str) -> str:
        """
        Makes a geocode API call to fetch the zip code of the specified address.

        Paramters:
        ----------
        street_address: `str`
            Street name to search the coordinates.
        city: `str`
            City name to search the coordinates.
        state: `str`
            State name to search the coordinates.
        """
        try:
            url = self.parse_query(
                key=self.__token,
                location=[street_address, city, state]
            )

            response = requests.get(url)
            
            results = json.loads(response.content)["results"][0]["locations"][0]
            zip_code = results["postalCode"][:5]

            return zip_code
        except:
            print(street_address, city, state)

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