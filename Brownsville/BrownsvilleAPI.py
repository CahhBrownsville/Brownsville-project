import json
import os
from datetime import date
from typing import Any, List, Tuple, Union

import folium
import folium.plugins
import numpy as np
import pandas as pd
import yaml
from branca.element import CssLink, JavascriptLink

from .data_api import Client
from .geocode import GeocodeClient
from .vendors.GroupedLayerControl import grouped_layer_control as glc


class InvalidColumnNameError(Exception):
    def __init__(self, msg: str = "Invalid column name passed") -> None:
        super().__init__(msg)


class Brownsville:
    def __init__(
        self, path: str = "./data/brownsville/", force_load: bool = False,
        update_map: bool = True, verbose=True,
    ) -> None:
        self.path = path
        self.verbose = verbose

        # Create the directory where the dataset will be stored
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.config = self.__load_config()
        self.geocode_client = GeocodeClient(
            self.config["geocode"]["app_token"])

        self.__load_dataset(force_load)
        self.__set_addresses()
        self.__fill_zip_codes()
        self.__get_spatial_information()
        self.__get_BBL()

        self.__load_pluto()

        self.__parse_datatypes()
        self.__fill_na()
        self.__translate_ids()
        self.__filter_no_complaints()

        self.__filter_descriptions()

        self._map = None
        if update_map:
            self._map = self.__update_map()

        self.save(overwrite_file=True)

    @property
    def buildings(self) -> np.ndarray:
        """
        Returns an NumPy ndarray with the set of unique buildings in the dataset.
        """
        return self.data["buildingid"].unique()

    @property
    def addresses(self) -> np.ndarray:
        """
        Returns an NumPy ndarray with the set of unique addresses in the dataset.
        """
        return self.data["address"].unique()

    @property
    def complaints(self) -> pd.Series:
        """
        Returns a Pandas DataFrame with building_id's and their respective
        number of complaints reported.
        """

        return self.data["buildingid"].value_counts()

    def get_record_by_building_id(self, building_id: int) -> pd.DataFrame:
        """
        Get the building information corresponding to the first occurence of the passed building id.

        Parameters:
        -----------
        building_id: `int`
            ID used as key to search the dataframe. 
        """
        if not building_id:
            raise IndexError("A building id  must be passed.") 

        index = self.data["buildingid"].values.searchsorted(building_id)
        return self.data.iloc[index]

    def get_records_by_address(self, address:str, copy:bool=False) -> pd.Series:
        """
        Get the building information corresponding to the first occurence of the passed address.

        Parameters:
        -----------
        address: `str`
            Address used as key to search the dataframe. 
        """
        records = self.data[self.data["address"] == address]
        if copy:
            return records.copy()

        return records

    def complaint_to_residential_unit_ratio(self, building_id: int) -> float:
        """
        Returns a number representing the ratio between the compaints reported from a building
        to the number residential units in said building.

        Parameters:
        -----------
        building_id: `int`
            Building ID to calculate the complaints to residential units ratio.
        """

        num_of_complaints = self.complaint_number(building_id)
        residential_units = self.get_residential_units(building_id)

        if residential_units == 0:
            return -1

        return round(num_of_complaints / residential_units, 3)

    def get_residential_units(self, building_id: int) -> int:
        """
        Returns an integer representing the number of residential units by building id or address.

        Parameters:
        -----------
        building_id: `int`
            ID used as key to search the dataframe.
        """

        row = self.get_record_by_building_id(building_id)

        return row["unitsres"]

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

    def get_building_age(self, building_id:int) -> int:
        """
        Returns an integer representing the age of the building, provided its building id. 

        Parameters:
        -----------
        building_id: `int`
            ID used as key to search the dataframe.
        """
        return date.today().year - self.get_record_by_building_id(building_id)["yearbuilt"]

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

        if self.verbose:
            for i in range(len(seasons)):
                print(f"{seasons[i]}: {values[i]}")

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

                    year_range = date_counts.iloc[i: i + step].sort_index()
                    years.append(year_range)

                    return list(reversed(years))

        return date_counts

    def complaint_number(self, building_id: int) -> int:
        """
        Get the number of complaints reported for the specified building.

        Parameters:
        -----------
        building_id: `int`
            ID of the building in the dataset.
        """

        return (self.data["buildingid"] == building_id).sum()

    def get_common_complaint_categories(self, building_id: int) -> int:
        """
        Get the most common major and minor complaint category

        Parameters:
        -----------
        building_id: `int`
            ID of the building in the dataset.
        """
        common_complaints = self.get_feature_occurrences_by_building(
            building_id, by=["majorcategory", "minorcategory"], find_all=True
        )
        if len(common_complaints) == 0:
            return ("n/a", "")

        return common_complaints.index[0]

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
            filename = os.path.join(self.path, "brownsville.csv")

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
        if self._map:
            return self._map

        nyc_longitude, nyc_latitude = 40.68424658435642, -73.91630313916588

        nyc_map: folium.Map = folium.Map(
            location=[nyc_longitude, nyc_latitude],
            tooltip="Click for building information",
            tiles="OpenStreetMap",
            zoom_start=12,
        )

        columns = ["buildingid", "address", "latitude", "longitude"]
        unique_addresses = self.data[columns].groupby(columns).size()

        two_year_filter = (self.data["statusdate"].dt.year == max(
            self.data["statusdate"].dt.year) - 2)
        data_two_years = self.data[two_year_filter][columns]
        unique_addresses_two_years = data_two_years.groupby(columns).size()

        five_year_filter = (self.data["statusdate"].dt.year == max(
            self.data["statusdate"].dt.year) - 5)
        data_five_years = self.data[five_year_filter][columns]
        unique_addresses_five_years = data_five_years.groupby(columns).size()

        # Import the map marker style
        nyc_map.get_root().header.add_child(CssLink("./static/style/foliumStyle.css"))
        nyc_map.get_root().header.add_child(JavascriptLink(
            "./static/js/leaflet.groupedlayercontrol.min.js"))

        feature_group_1 = self.__create_marker_feature_group(
            name="Address Locations",
            data=unique_addresses,
            folium_map=nyc_map
        )
        feature_group_2 = self.__create_marker_feature_group(
            name="Address locations (two years)",
            data=unique_addresses_two_years,
            folium_map=nyc_map
        )
        feature_group_3 = self.__create_marker_feature_group(
            name="Address locations (five years)",
            data=unique_addresses_five_years,
            folium_map=nyc_map
        )

        feature_group_4 = self.__create_heatmap_feature_group(
            name="Brownsville heatmap",
            folium_map=nyc_map
        )
        feature_group_5 = self.__create_heatmap_feature_group(
            name="Brownsville heatmap (two years)",
            folium_map=nyc_map,
            n=2
        )
        feature_group_6 = self.__create_heatmap_feature_group(
            name="Brownsville heatmap (five years)",
            folium_map=nyc_map,
            n=5
        )

        glc.GroupedLayerControl({}, {
            "Address locations": {
                "All years":  feature_group_1,
                "Two years":  feature_group_2,
                "Five years": feature_group_3},
            "Heatmap": {
                "All years": feature_group_4,
                "Two years": feature_group_5,
                "Five years": feature_group_6
            }},
            ["Address locations", "Heatmap"]
        ).add_to(nyc_map)

        # Save the map to an HTML file
        if save_map:
            filename = os.path.join(os.getcwd(), "brownsville.html")

            # filename = os.path.join(path)
            nyc_map.save(outfile=filename)

        return nyc_map

    def __create_heatmap_feature_group(
        self, name: str, folium_map: folium.Map, n: int = None
    ) -> folium.FeatureGroup:
        """
        Returns a feature group with a heat map of the locations in the provided pandas DataFrame.

        Parameters:
        -----------
        name: `str`
            Name of the of feature group.
        folium_map: `folium.Map`
            Folium map where the heatmap feature group will be added.
        n: `int`
            Number of years to look extract from the provided dataframe.
        """

        data = self.data
        if n:
            n_year_filter = (data["statusdate"].dt.year ==
                             max(data["statusdate"].dt.year) - n)
            data = data[n_year_filter]

        # Get the coordinates for each building
        lats = data["latitude"].values
        lons = data["longitude"].values

        # Calculate and 0-1 normalize heatmap weights
        complaints_per_building = data["buildingid"].value_counts()
        def weight_f(b_id): return complaints_per_building[b_id]
        weights = data["buildingid"].apply(weight_f).values
        weights = (weights - min(weights)) / (max(weights) - min(weights))

        feature_group = folium.FeatureGroup(name=name, show=True)
        folium.plugins.HeatMap(
            data=list(zip(lats, lons, weights)),
            name=name,
            min_opacity=0.3,
            max_opacity=0.7,
        ).add_to(feature_group)
        feature_group.add_to(folium_map)

        return feature_group

    def __create_marker_feature_group(
        self, name: str, data: pd.DataFrame, folium_map: folium.Map
    ) -> folium.FeatureGroup:
        """
        Returns a feature group with a marker cluster of the locations in the provided pandas DataFrame.

        Parameters:
        -----------
        name: `str`
            Name of the of feature group.
        data: `folium.Map`
            Folium map where the heatmap feature group will be added.
        n: `int`
            Number of years to look extract from the provided dataframe.
        """

        feature_group = folium.FeatureGroup(name=name, show=True)
        self.__create_marker_cluster(
            data,
            name=name
        ).add_to(feature_group)
        feature_group.add_to(folium_map)

        return feature_group

    def __create_marker_cluster(
        self, data: pd.DataFrame, name: str = "name not specified"
    ) -> folium.plugins.MarkerCluster:
        """
        Accepts a Folium map in which custom leaflet marker cluster are added.

        Parameters:
        -----------
        data: `pd.DataFrame`
            Pandas DataFrame used as reference for the marker clusters.
        name: `str`
            Name of the marker cluster
        """
        
        NA = "N/A"

        # load the icon creation function
        icon_create_function = ""
        with open("./static/js/iconCreateFunction.js", "r") as f:
            icon_create_function = f.read()

        # Create and add the marker cluster to the folium map
        marker_cluster = folium.plugins.MarkerCluster(
            name=name, icon_create_function=icon_create_function
        )

        for building_id, address, latitude, longitude in data.index:

            building_info = self.get_record_by_building_id(building_id)

            number_of_reports = self.complaint_number(building_id)
            major_category, minor_category = self.get_common_complaint_categories(
                building_id
            )

            complaint = f"{major_category.title()} - {minor_category.title()}"
            complaint_to_runits = self.complaint_to_residential_unit_ratio(building_id)
            if complaint_to_runits == -1:
                complaint_to_runits = NA

            residential_units = building_info['unitsres']
            if residential_units == 0:
                residential_units = NA

            owner = building_info['ownername']
            if pd.isna(building_info['ownername']):
                owner = "UNKNOWN"
            
            age_info = f"{building_info['yearbuilt']} ({self.get_building_age(building_id)} years old)"
            if building_info["yearbuilt"] == 0:
                age_info = "UNKNOWN"
            
            alterations = building_info["yearalter1"]
            iframe = folium.IFrame(
                html=f"""
                    <div id='custom-popup'>
                        <b>{address}</b>
                        <br>
                        <br>
                        <b>Building ID:</b> {building_id}
                        <br>
                        <b>Owner:</b> {owner}
                        <br>
                        <b>Owner type:</b> {building_info['ownertypelong']}
                        <br>
                        <b>Year built:</b> {age_info}
                        <br>
                        <b>Latitude:</b> {latitude}
                        <br>
                        <b>Longitude:</b> {longitude}
                        <br>
                        <b>Number of residential units:</b> {residential_units}
                        <br>
                        <b>Number of complaints:</b> {number_of_reports}
                        <br>
                        <b>Complaint to residential units ratio:</b> {complaint_to_runits}
                        <br>
                        <b>Most frequent complaint:</b> {complaint}
                    </div>

                    <style>
                        html * {{
                            font-size: 1em !important;
                            color: #000 !important;
                            font-family: Arial !important;
                        }}

                        #custom-popup {{
                            min-width: 450px;
                            min-height: 450px;
                        }}
                    </style>
                """
            )

            popup = folium.Popup(iframe, min_width=500,
                                 max_width=500, parse_html=True)
            
            marker = folium.Marker(
                location=[latitude, longitude],
                popup=address,
                icon_create_function=icon_create_function,
                tooltip=f"{number_of_reports} reports",
                reports=float(number_of_reports),
            )

            popup.add_to(marker)
            marker.add_to(marker_cluster)

        return marker_cluster

    def __update_map(self) -> folium.Map:
        """
        Helper function to update map when instantiating the class.
        """
        return self.display_map(save_map=True)

    def __filter_no_complaints(self) -> None:
        """
        Remove buildings from the dataset that do not have a major or minor
        complaint category defined.
        """
        no_complaints_filter = (self.data["majorcategoryid"].isna()) & (
            self.data["minorcategoryid"].isna()
        )
        self.data = self.data[~(no_complaints_filter)]

    def __get_spatial_information(self) -> None:
        """
        Uses the geocode custom API to fetch spatial information about
        the building (latitude and longitude).
        """
        state = "NY"
        columns = ["address", "borough", "zip"]

        # Read the translation table from local storage if exists
        filename = os.path.join(self.path, "address_table.json")
        if os.path.exists(filename):
            with open(filename, "r") as f:
                address_to_coord = json.load(f)
        else:

            unique_addresses = self.data[columns].groupby(columns).size()
            address_to_coord = {}
            for street, city, zip_code in unique_addresses.index:
                if pd.isnull(zip_code):
                    zip_code == self.geocode_client.get_zip(
                        street, city, state)
                address = " ".join((street, city, str(zip_code)))

                coord = self.geocode_client.get_lat_lng(
                    street, city, state, zip_code)
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

            latitudes[i] = lat
            longitudes[i] = lng

        self.data["latitude"] = latitudes
        self.data["longitude"] = longitudes

    def __fill_zip_codes(self) -> None:

        columns = ["address", "borough", "zip"]

        def get_zip(address): return self.geocode_client.get_zip(
            address[0], address[1], "NY")

        self.data["zip"] = self.data["zip"].astype("Int64")
        zip_filter = self.data["zip"].isna()
        missing_zip = self.data[columns][zip_filter].copy()
        zip_codes = missing_zip.apply(get_zip, axis=1).values

        for index, zip_code in zip(self.data["zip"][zip_filter].index, zip_codes):
            self.data["zip"].iloc[index] = zip_code

    def __set_addresses(self) -> None:
        """
        Concatenates the house number and street name into a single columns.
        """
        self.data["address"] = self.data["housenumber"] + \
            " " + self.data["streetname"]

    def __parse_datatypes(self) -> None:
        """
        Parses the dataset features to their appropiate datatypes.
        """
        convert_dict = {
            "unittypeid": "Int64",
            "spacetypeid": "Int64",
            "typeid": "Int64",
            "majorcategoryid": "Int64",
            "minorcategoryid": "Int64",
            "codeid": "Int64",
            "unitsres": "Int64",
            "unitstotal": "Int64",
            "numbldgs": "Int64",
            "yearbuilt": "Int64",
            "yearalter1": "Int64",
            "yearalter2": "Int64",
            "receiveddate": "datetime64",
            "statusdate": "datetime64"
        }

        try:
            self.data = self.data.astype(convert_dict)
        except:
            print("Conversion error")

    def __load_dataset(
        self, force_load: bool = False
    ) -> bool:
        """
        Uses the Scoracte API custom client to create the Bronwsville dataset.
        """

        with Client(*self.config["sodapy"].values(), data_path=self.path, timeout=40) as c:

            update_due = (
                c.metadata_complaint_problems.cache_date
                < c.metadata_complaint_problems.updated_on
            ) or (
                c.metadata_housing_maintenance.cache_date
                < c.metadata_housing_maintenance.updated_on
            )

            filepath = os.path.join(self.path, c.metadata_brownsville.filename)
            if not force_load and not update_due and os.path.exists(filepath):
                if self.verbose:
                    print("Loading cached dataset...")
                self.data = pd.read_csv(filepath, index_col=0)

                self.fetch_remote = False
            else:
                self.data = c.load_brownsville(
                    fetch_all=True, verbose=self.verbose)
                self.fetch_remote = True

            self.data.sort_values(by='buildingid', inplace=True)
            self.data.reset_index()

    def __translate_ids(self) -> None:
        """
        Translate the feature id (i.e., majorcategoryid) to their corresponding value.
        """
        with open("./brownsville_translations.yaml", "r") as f:
            translations = yaml.load(f, Loader=yaml.FullLoader)
            for key in translations:
                value = translations[key]
                self.data[key] = self.data[key + "id"].map(value)

    def __filter_descriptions(self) -> None:
        """
        Parses the dataset's status description to a shorter version. 
        """
        descriptions = {
            "The Department of Housing Preservation and Development inspected the following conditions. No violations were issued. The complaint has been closed.": "Inspected; no violations issued",
            "The Department of Housing Preservation and Development inspected the following conditions. Violations were issued. Information about specific violations is available at www.nyc.gov/hpd.": "Inspected; violations issued",
            "The Department of Housing Preservation and Development was not able to gain access to inspect the following conditions. The complaint has been closed. If the condition still exists, please file a new complaint.": "Unable to gain access",
            "More than one complaint was received for this building-wide condition.This complaint status is for the initial complaint. The Department of Housing Preservation and Development contacted an occupant of the apartment and verified that the following conditions were corrected. The complaint has been closed. If the condition still exists, please file a new complaint.": "Multiple complaints; tenant confirmed resolved",
            "More than one complaint was received for this building-wide condition.This complaint status is for the initial complaint. The Department of Housing Preservation and Development contacted a tenant in the building and verified that the following conditions were corrected. The complaint has been closed. If the condition still exists, please file a new complaint.": "Multiple complaints; tenant confirmed resolved",
            "The Department of Housing Preservation and Development responded to a complaint of no heat or hot water and was advised by a tenant in the building that heat and hot water had been restored. If the condition still exists, please file a new complaint.": "Single complaint; tenant confirmed resolved",
            "The Department of Housing Preservation and Development was not able to gain access to your apartment or others in the building to inspect for a lack of heat or hot water. The complaint has been closed. If the condition still exists, please file a new complaint.": "Unable to gain access",
            "The Department of Housing Preservation and Development contacted an occupant of the apartment and verified that the following conditions were corrected. The complaint has been closed. If the condition still exists, please file a new complaint.": "Inspected; no violations issued",
            "The Department of Housing Preservation and Development inspected the following conditions. Violations were previously issued for these conditions. Information about specific violations is available at www.nyc.gov/hpd.": "Inspected; violations previously issued",
            "The Department of Housing Preservation and Development was unable to access the rooms where the following conditions were reported. No violations were issued. The complaint has been closed.": "Unable to gain access",
            "The Department of Housing Preservation and Development contacted a tenant in the building and verified that the following conditions were corrected. The complaint has been closed. If the condition still exists, please file a new complaint.": "Single complaint; tenant confirmed resolved",
            "The Department of Housing Preservation and Development was not able to gain access to your apartment to inspect for a lack of heat or hot water. However, HPD was able to verify that heat or hot water was inadequate by inspecting another apartment and a violation was issued. Information about specific violations is available at www.nyc.gov/hpd.": "Unable to gain access; violation issued",
            "The following complaint conditions are still open. HPD may attempt to contact you to verify the correction of the condition or may conduct an inspection.": "Complaint remains open",
            "The Department of Housing Preservation and Development was not able to gain access to inspect the conditions. If the conditions still exist and an inspection is required, please contact the borough office with your complaint number at": "Unable to gain access",
            "The Department of Housing Preservation and Development responded to a complaint of no heat or hot water. Heat was not required at the time of the inspection. No violations were issued. If the condition still exists, please file a new complaint.": "Inspected; no violations issued",
            "More than one complaint was received for this building-wide condition. This complaint status is for the initial complaint.The Department of Housing Preservation and Development contacted an occupant of the apartment and verified that the following conditions were corrected. The complaint has been closed. If the condition still exists, please file a new complaint.": "Multiple complaints; tenant confirmed resolved",
            "More than one complaint was received for this building-wide condition. This complaint status is for the initial complaint.The Department of Housing Preservation and Development contacted a tenant in the building and verified that the following conditions were corrected. The complaint has been closed. If the condition still exists, please file a new complaint.": "Multiple complaints; tenant confirmed resolved",
            "The Department of Housing Preservation and Development inspected the following conditions. Violations were issued. However, HPD also identified potential lead-based paint conditions and will attempt to contact you to schedule a follow-up inspection to test the paint for lead. Information about specific violations is available at www.nyc.gov/hpd.": "Inspected; violations issued",
            "More than one complaint was received for this building-wide condition.This complaint status is for the initial complaint. The following complaint conditions are still open. HPD may attempt to contact you to verify the correction of the condition or may conduct an inspection.": "Complaint remains open",
            "The Department of Housing Preservation and Development was unable to access the rooms where the following  conditions were reported. No violations were issued. The complaint has been closed.": "Unable to gain access",
            "The Department of Housing Preservation and Development inspected the following conditions. A Section 8 Failure was issued. Both the tenant and the property owner will receive a notice in the mail regarding the details of the Failure and the resulting action by the Agency.": "Inspected; violations issued",
            "UNKNOWN STATUS" : "UNKNOWN STATUS"
        }

        self.data["statusdescriptionshort"] = self.data["statusdescription"].map(descriptions)

    def __load_pluto(self) -> None:
        """
        Fetches and merges the PLUTO dataset to the Brownsville dataset. 
        """
        with Client(*self.config["sodapy"].values(), data_path=self.path) as c:
            df_pluto = c.load_pluto(
                fetch_all=True,
                verbose=self.fetch_remote,
                select="bbl, bldgclass, bldgarea, numbldgs, numfloors, unitsres, unitstotal,"
                + "landuse, ownertype, ownername, yearbuilt, yearalter1, yearalter2",
                where="cd=316"
            )

            df_pluto["bbl"] = df_pluto["bbl"].astype("Int64")
            self.data = pd.merge(
                self.data,
                df_pluto,
                on="bbl",
                how="left"
            )

            owner_types = {
                "C": "CITY OWNERSHIP",
                "M": "MIXED CITY & PRIVATE OWNERSHIP",
                "O": "OTHER (PUBLIC AUTHORITY OR THE STATE/FEDERAL GOVERNMENT)",
                "P": "PRIVATE OWNERSHIP",
                "X": "FULLY TAX-EXEMPT PROPERTY (MAYBE OWNED BY THE CITY)"
            }

            self.data["ownertypelong"] = self.data["ownertype"].map(
                owner_types)

    def __fill_na(self) -> None:
        """
        """
        values = {
            "numbldgs": 0,
            "numfloors": 0,
            "unitsres": 0,
            "unitstotal": 0,
            "landuse": 0,
            "yearbuilt": 0,
            "yearalter1": 0,
            "yearalter2": 0,
            "ownertypelong": "UNKNOWN (USUALLY PRIVATE OWNERSHIP)",
            "statusdescription": "UNKNOWN STATUS"
        }
        self.data.fillna(value=values, inplace=True)

    def __get_BBL(self) -> None:
        """
        """
        self.data["bbl"] = self.data["boroughid"].astype(str)                \
            + self.data["block"].astype(str).apply(str.zfill, args=(5,))     \
            + self.data["lot"].astype(str).apply(str.zfill, args=(4,))

        self.data["bbl"] = self.data["bbl"].astype('int64')

    def __load_config(self) -> None:
        """
        Load the configuration file necessary for the API's
        """
        try:
            # Load the configuration files with all the credentials for the Socrata API
            with open("./config.yaml", "r") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                return config
        except FileNotFoundError:
            print(
                "Configuration file not found. Loading client with default arguments."
            )
            return ()
