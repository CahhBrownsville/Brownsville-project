from typing import List, Union
import pandas as pd
from dataclasses import dataclass

from data_api import Client
import yaml
import os


class Brownsville:
    def __init__(self, path="./data/brownsville/") -> None:
        self.path = path

        # Create the directory where the dataset will be stored
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.__load_dataset()
        self.__translate_ids()
        self.__parse_datatypes()
        
    @property
    def buildings(self) -> set:
        return set(self.data["buildingid"])

    def records_by_season(self) -> set:
        date_counts = self.records_by_date(period="month")

        seasons = ["Winter", "Spring", "Summer", "Autumn"]
        values = [
            date_counts.loc[["Jan", "Feb", "Mar"]].sum(),
            date_counts.loc[["Apr", "May", "Jun"]].sum(),
            date_counts.loc[["Jul", "Aug", "Sep"]].sum(),
            date_counts.loc[["Oct", "Nov", "Dec"]].sum()
        ]
        print(f"{seasons[0]}: {values[0]}")
        print(f"{seasons[1]}: {values[1]}")
        print(f"{seasons[2]}: {values[2]}")
        print(f"{seasons[3]}: {values[3]}")

        return seasons, values

    def records_by_date(self, period:int="month", step:int=1, num_years:int=0) -> set:
        """
        TODO: FIX TIME PERIODS
        """
        if period == "month":
            dates = self.data["statusdate"].dt.month.astype("Int64")
            date_counts = dates.value_counts()
            date_counts = date_counts.sort_index()

            date_counts.index = pd.Index([
                "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ])

        if period == "year":
            dates = self.data["statusdate"].dt.year.astype("Int64")

            date_counts = dates.value_counts()
            date_counts = date_counts.sort_index()

            if num_years > len(date_counts):
                raise "The number of years must be less than the number of available years in the dataset"
                return

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

    def __parse_datatypes(self):
        self.data["receiveddate"] = self.data["receiveddate"].astype("datetime64")
        self.data["statusdate"] = self.data["statusdate"].astype("datetime64")

    def __load_dataset(self):

        config = self.__load_config()
        with Client(*config, data_path=self.path) as c:

            update_due = (
                c.metadata_complaint_problems.cache_date
                < c.metadata_complaint_problems.updated_on
                or c.metadata_housing_maintenance.cache_date
                < c.metadata_housing_maintenance.updated_on
            )

            if not update_due and os.path.exists(
                self.path + c.metadata_brownsville.filename
            ):
                print("Loading cached dataset...")
                self.data = pd.read_csv(
                    self.path + c.metadata_brownsville.filename, index_col=0
                )
            else:
                self.data = c.load_brownsville(fetch_all=True)

    def __translate_ids(self):
        with open("./brownsville_translations.yaml", "r") as f:
            translations = yaml.load(f, Loader=yaml.FullLoader)
            for key in translations:
                value = translations[key]
                self.data[key] = self.data[key + "id"].map(value)

    def __load_config(self):
        try:
            # Load the configuration files with all the credentials for the Socrata API
            with open("./config.yaml", "r") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                # app_token, username, password = config["sodapy"].values()

                if "sodapy" in config:
                    app_token, username, password = config["sodapy"].values()
                    return app_token, username, password
        except FileNotFoundError:
            print(
                "Configuration file not found. Loading client with default arguments."
            )
            return ()