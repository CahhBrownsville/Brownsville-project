"""
TODO: 
    - Update documentation
    - Remove duplicate rows
"""

import json
import os
from typing import Any, List, Tuple, Union

import folium
import folium.plugins
import numpy as np
import pandas as pd
import yaml

from data_api import Client
from geocode import GeocodeClient


class InvalidColumnNameError(Exception):
    def __init__(self, msg: str = "Invalid column name passed") -> None:
        super().__init__(msg)


class Brownsville:
    def __init__(
        self, path: str = "./data/brownsville/", force_load: bool = False
    ) -> None:
        self.path = path

        # Create the directory where the dataset will be stored
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.config = self.__load_config()
        # print(self.config)
        self.geocode_client = GeocodeClient(self.config["geocode"]["app_token"])

        self.__load_dataset(force_load)
        self.__translate_ids()
        self.__parse_datatypes()
        self.__set_addresses()

        self.__get_spatial_information()

    @property
    def buildings(self) -> np.ndarray:
        """
        Returns an NumPy ndarray with the set of unique buildings in the dataset by building id.
        """
        return self.data["buildingid"].unique()

    def get_date_range(self, by: str = "status") -> Tuple[pd.Timestamp, pd.Timestamp]:
        """
        Return the date range for the complaint since the day it was marked as complete or
        since the day it was received.

        Parameters:
        -----------
        by: `str`
            Feature to get the data range by.
        """
        if by not in ("status", "received"):
            raise InvalidColumnNameError()

        by += "date"

        return self.data[by].min(), self.data[by].max()

    def records_by_season(self) -> Tuple[List, List]:
        """
        Return the number of complaints reported by season.
        """
        date_counts = self.records_by_date(period="month")

        seasons = ["Winter", "Spring", "Summer", "Autumn"]
        values = [
            date_counts.loc[["Jan", "Feb", "Mar"]].sum(),
            date_counts.loc[["Apr", "May", "Jun"]].sum(),
            date_counts.loc[["Jul", "Aug", "Sep"]].sum(),
            date_counts.loc[["Oct", "Nov", "Dec"]].sum(),
        ]
        print(f"{seasons[0]}: {values[0]}")
        print(f"{seasons[1]}: {values[1]}")
        print(f"{seasons[2]}: {values[2]}")
        print(f"{seasons[3]}: {values[3]}")

        return seasons, values

    def records_by_date(
        self, period: str = "month", step: int = 1, num_years: int = 0
    ) -> set:
        """
        Return the number of complaints reported on a monthly or yearly basis.

        Parameters:
        -----------
        period: `str`
            Type of time period to return the number of complaint reported.
        step: `int`
            Number of year intervals to separate the data. *Only works if period is `year`*
        num_years `int`
            Number of past years to query the data. *Only works if period is `year`*

        TODO: FIX TIME PERIODS
        """
        if period == "month":
            dates = self.data["statusdate"].dt.month.astype("Int64")
            date_counts = dates.value_counts()
            date_counts = date_counts.sort_index()

            date_counts.index = pd.Index(
                [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ]
            )

        if period == "year":
            dates = self.data["statusdate"].dt.year.astype("Int64")

            date_counts = dates.value_counts()
            date_counts = date_counts.sort_index()

            if num_years > len(date_counts):
                raise "The number of years must be less than the number of available years in the dataset"

            if num_years > step >= 0:
                date_counts = date_counts.sort_index(ascending=False)

                years = []

                for i in range(0, num_years, step):
                    start = i
                    end = start + step

                    if len(date_counts) > end:
                        end = len(date_counts) - 1

                    year_range = date_counts.iloc[i : i + step].sort_index()
                    years.append(year_range)

                return list(reversed(years))

        return date_counts

    def get_feature_occurrences_by_building(
        self,
        building_id: int,
        by: Union[List[str], str],
        find_all: bool = False,
        n: int = 10,
        warning: bool = False,
    ) -> pd.Series:
        """
        Returns a list of the most common features provided in the brownsville.csv dataset.

        Parameters:
        -----------
        building_id: `int`
            Building ID to filter the results.
        by: `[str] | str`
            Column name or list of column names to filter the building complaints records by.
        find_all: `bool`
            Flag indicating whether to return all results for the provided feaures. Default False.
        n: `int`
            Number of maximum records to be returned by building. Default 10.
        warning: `bool`
            Set to `True` to display warning messages. Default False.
        """

        # No maximum record limit is set and the find_all flag is set to false
        if n < 1 and not find_all:
            raise "n must greater than or equal to 1."

        # No column name(s) were provided
        if not by:
            raise "You must specify a feature name."

        # If column name is a string, convert to a list of strings for convenience
        if isinstance(by, str):
            by = [by]

        # Filter the feature by BuildingID
        df_filter = self.data["buildingid"] == building_id
        common_categories = self.data[df_filter][by].value_counts()

        if not find_all:
            # Limit the size of the common_categories series to n.
            # If n exceeds the size of common_categories, change n to be this szie.
            if n > len(common_categories):
                n = len(common_categories)
                if warning:
                    print("n exceeds number of categories. Changing n to", n)

            common_categories = common_categories[:n]
        return common_categories

    def get_feature_occurrences_by_key(
        self,
        keys: Union[List[str], str],
        values: List[Any],
        features: Union[List[str], str],
        find_all: bool = False,
        n: int = 10,
        warning: bool = False,
    ) -> pd.Series:
        """
        Returns a list of the most common features provided in the brownsville.csv dataset.

        Parameters:
        -----------
        keys: `List[str] | str`
            Building ID to filter the results.
        values: `List[Any]`
            Values to filter the keys by.
        features: `[str] | str`
            Column name or list of column names to filter the building complaints records by.
        find_all: `bool`
            Flag indicating whether to return all results for the provided feaures. Default False.
        n: `int`
            Number of maximum records to be returned by building. Default 10.
        warning: `bool`
            Set to `True` to display warning messages. Default False.
        """

        # No maximum record limit is set and the find_all flag is set to false
        if n < 1 and not find_all:
            raise "n must greater than or equal to 1."

        # No column name(s) were provided
        if not features:
            raise "You must specify a feature name."

        # If column name is a string, convert to a list of strings for convenience
        if isinstance(keys, str):
            keys = [keys]

        if isinstance(values, str):
            values = [values]

        if isinstance(features, str):
            features = [features]

        if len(keys) != len(values):
            raise "Keys and Values should have the same number of elements."

        # Filter the feature by BuildingID
        filters = None
        for key, value in zip(keys, values):
            if filters is None:
                filters = self.data[key] == value
            else:
                filters &= self.data[key] == value

        common_categories = self.data[filters][features].value_counts()

        if not find_all:
            # Limit the size of the common_categories series to n.
            # If n exceeds the size of common_categories, change n to be this szie.
            if n > len(common_categories):
                n = len(common_categories)
                if warning:
                    print("n exceeds number of categories. Changing n to", n)

            common_categories = common_categories[:n]
        return common_categories

    def save(self, filename: str = None, overwrite_file: bool = False) -> None:
        """
        Saves the current state of the dataset as a `.csv` file at the path specified during
        class instantiation.

        Parameters:
        -----------
        filename: `str`
            Name for the file being stored.
        force_save: `bool`
            Flag indicating whether the file should be overwritten or not.
        """
        if not filename:
            filename = self.path + "brownsville.csv"

        if os.path.exists(filename):
            if not overwrite_file:
                inp = input("File already exists. Type y/Y to overwrite: ")
                if inp.lower() != "y":
                    return

        self.data.to_csv(filename)

    def display_map(self, save_map: bool = False) -> folium.Map:
        """
        Returns a folium map with information about all the buildings. 

        Parameters:
        -----------
        save_map: `bool`
            Save the map to an `.html` file.
        """
        
        nyc_longitude, nyc_latitude = 40.68424658435642, -73.91630313916588

        nyc_map: folium.Map = folium.Map(
            location=[nyc_longitude, nyc_latitude],
            tooltip="Click for building information",
            tiles="OpenStreetMap",
            zoom_start=12,
        )

        columns = ["address", "latitude", "longitude"]
        unique_addresses = self.data[columns].groupby(columns).size()

        markerCluster = folium.plugins.MarkerCluster().add_to(nyc_map)

        # Add the markers to the map
        for address, latitude, longitude in unique_addresses.index:

            marker = folium.Marker(location=[latitude, longitude])
            popup = folium.Popup(address, parse_html=True)

            marker.add_to(markerCluster)
            popup.add_to(markerCluster)

        if save_map:
            filename = os.path.join(self.path, "brownsville.html")
            nyc_map.save(outfile=filename)

        return nyc_map

    def __get_spatial_information(self) -> None:
        """
        Uses the geocode custom API to fetch spatial information about 
        the building (latitude and longitude).
        """
        state = "NY"
        columns = ["address", "borough", "zip"]

        # Read the translation table from local storage if exists
        filename = self.path + "address_table.json"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                address_to_coord = json.load(f)
        else:
            unique_addresses = self.data[columns].groupby(columns).size()
            address_to_coord = {}
            for street, city, zip_code in unique_addresses.index:
                address = " ".join((street, city, str(zip_code)))
                coord = self.geocode_client.get_lat_lng(street, city, state, zip_code)
                address_to_coord[address] = coord

            with open(filename, "w") as f:
                address_to_coord = json.dump(address_to_coord, f)

        num_of_addresses = self.data.shape[0]
        latitudes = np.zeros(num_of_addresses)
        longitudes = np.zeros(num_of_addresses)

        for i, value in enumerate(self.data[columns].iterrows()):

            street, city, zip_code = value[1]
            address = " ".join((street, city, str(zip_code)))
            lat, lng = address_to_coord[address]
            # print(lat, lng)

            latitudes[i] = lat
            longitudes[i] = lng

        self.data["latitude"] = latitudes
        self.data["longitude"] = longitudes

    def __set_addresses(self) -> None:
        """
        Concatenates the house number and street name into a single columns.
        """
        self.data["address"] = self.data["housenumber"] + " " + self.data["streetname"]

    def __parse_datatypes(self) -> None:
        """
        Parses the dataset features to their appropiate datatypes.
        """
        self.data["unittypeid"] = self.data["unittypeid"].astype("Int64")
        self.data["spacetypeid"] = self.data["spacetypeid"].astype("Int64")
        self.data["typeid"] = self.data["typeid"].astype("Int64")
        self.data["majorcategoryid"] = self.data["majorcategoryid"].astype("Int64")
        self.data["minorcategoryid"] = self.data["minorcategoryid"].astype("Int64")
        self.data["codeid"] = self.data["codeid"].astype("Int64")
        self.data["receiveddate"] = self.data["receiveddate"].astype("datetime64")
        self.data["statusdate"] = self.data["statusdate"].astype("datetime64")

    def __load_dataset(self, force_load: bool = False) -> None:
        """
        Uses the Scoracte API custom client to create the Bronwsville dataset.
        """

        with Client(*self.config["sodapy"].values(), data_path=self.path) as c:

            update_due = (
                c.metadata_complaint_problems.cache_date
                < c.metadata_complaint_problems.updated_on
                or c.metadata_housing_maintenance.cache_date
                < c.metadata_housing_maintenance.updated_on
            )

            filepath = os.path.join(self.path, c.metadata_brownsville.filename)
            if not force_load and not update_due and os.path.exists(filepath):
                print("Loading cached dataset...")
                self.data = pd.read_csv(filepath, index_col=0)
            else:
                self.data = c.load_brownsville(fetch_all=True)

    def __translate_ids(self) -> None:
        """
        Translate the feature id (i.e., majorcategoryid) to their corresponding value.
        """
        with open("./brownsville_translations.yaml", "r") as f:
            translations = yaml.load(f, Loader=yaml.FullLoader)
            for key in translations:
                value = translations[key]
                self.data[key] = self.data[key + "id"].map(value)

    def __load_config(self) -> None:
        """
        Load the configuration file necessary for the API's 
        """
        try:
            # Load the configuration files with all the credentials for the Socrata API
            with open("./config.yaml", "r") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                # app_token, username, password = config["sodapy"].values()

                # if "sodapy" in config:
                #     app_token, username, password = config["sodapy"].values()
                #     return app_token, username, password

                return config
        except FileNotFoundError:
            print(
                "Configuration file not found. Loading client with default arguments."
            )
            return ()


# if __name__ == "__main__":
#     b = Brownsville()
#     by_address = b.get_feature_occurrences_by_key(
#         keys=["streetname", "apartment"],
#         values=["PACIFIC STREET", "1"],
#         features=["majorcategory"],
#         n=5,
#     )

#     print(by_address)
