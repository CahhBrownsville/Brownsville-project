"""
TODO: 
    - Parse keyword arguments in the __get_results method
"""

import os
import pickle
import textwrap
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from sodapy import Socrata

_DOMAIN = "data.cityofnewyork.us"

class UnknownDatasetException(Exception):
    def __init__(self, msg:str = "Passed dataset not in list of valid dataset") -> None:
        super().__init__(msg)

@dataclass
class DatasetMetaInformation:

    endpoint: str
    name: str
    filename: str
    updated_on: datetime
    cache_date: datetime
    attribution: str = ""
    category: str = ""
    description: str = ""
    offset: int = 0
    loaded: bool = False
    last_query: dict = None

    def __init__(self, client: Socrata = None, endpoint: str = "", **kwargs):
        """
        Initialize the Datset Meta Infomation class according to the provided endpoint.

        Parameters:
        -----------
        client: `Socrata`
            Socrata client used by the `Client` class.
        endpoint: `str`
            Endpoint used to fetch metadata.
        """
        if client:
            results = client.get_metadata(endpoint)
        else:
            results = kwargs

        self.endpoint = results["id"]
        self.name = results["name"]
        self.filename = self.name.lower().replace(" ", "-") + "-raw.csv"
        self.attribution = results["attribution"]
        self.category = results["category"]
        self.description = results["description"]
        self.updated_on = datetime.fromtimestamp(results["rowsUpdatedAt"])
        self.cache_date = datetime(1970, 12, 17)  # unix epoch time

    @property
    def information(self) -> str:
        """
        Returns a string containing the dataset's metadata
        """

        wrapped_description = textwrap.fill(self.description, width=80)
        description = textwrap.indent(wrapped_description, "\t\t")
        return (
            f"{self.name}:"
            + f"\n\t- Filename: {self.filename}"
            + f"\n\t- Endpoint: {self.endpoint}"
            + f"\n\t- Description:\n{description}"
            + f"\n\t- Category: {self.category}"
            + f"\n\t- Attribution: {self.attribution}"
            + f"\n\t- Dataset Updated on: {self.updated_on:%m-%d-%Y}"
            + f"\n\t- Cache date: {self.cache_date:%m-%d-%Y}"
            + f"\n\t- Number of records on cache: {self.offset}"
        )


class Client(object):
    """
    This class acts as a client for fetching the datasets mentioned in the proposal, i.e.,
    the `311 Service Requests from 2010 to Present`, `Complaint Problems`, `Housing Maintenance
    Code Complaints`, and `DOB Complaints Received`.

    This class uses the Sodapy client to communicate with the NYC OpenData API.
    """

    def __init__(
        self,
        app_token: str = "",
        username: str = None,
        password: str = None,
        data_path: str = "./data/",
        timeout: int = 20
    ) -> None:

        # Initialize the Sodapy client
        if len(app_token) == 0:
            self._client = Socrata(_DOMAIN, None, timeout=timeout)
        else:
            self._client = Socrata(
                _DOMAIN,
                app_token=app_token,
                username=username,
                password=password,
                timeout=timeout,
            )

        self._DATA_PATH = data_path
        self.__load_metadata()

    @property
    def information(self) -> str:
        """
        Display information about the data sources.
        """

        # Concatenate all of the metadata string
        s = "\n\n".join(
            [
                self.metadata_311.information,
                self.metadata_complaint_problems.information,
                self.metadata_housing_maintenance.information,
                self.metadata_dob_complaints.information,
                self.metadata_brownsville.information,
            ]
        )
        return s

    def load_311(self, fetch_all: bool = False, **kwargs) -> pd.DataFrame:
        """
        Return a DataFrame containing all records from the 311 Service Requests from 2010 to Present dataset.

        Parameters
        ----------
        fetch_all: `bool`
            Flag indicating whether all records should be feteched.
        """

        df = self.__get_results(self.metadata_311, fetch_all=fetch_all, **kwargs)

        return df

    def load_complaint_problems(
        self, fetch_all: bool = False, **kwargs
    ) -> pd.DataFrame:
        """
        Return a DataFrame containing all records from the Complaint Problems dataset.

        Parameters
        ----------
        fetch_all: `bool`
            Flag indicating whether all records should be feteched.
        """

        df = self.__get_results(
            self.metadata_complaint_problems, fetch_all=fetch_all, **kwargs
        )

        return df

    def load_housing_maintenance(
        self, fetch_all: bool = False, **kwargs
    ) -> pd.DataFrame:
        """
        Return a DataFrame containing all records from the Complaint Problems dataset.

        Parameters
        ----------
        fetch_all: `bool`
            Flag indicating whether all records should be feteched.
        """

        df = self.__get_results(
            self.metadata_housing_maintenance, fetch_all=fetch_all, **kwargs
        )

        return df

    def load_dob_complaints(self, fetch_all: bool = False, **kwargs) -> pd.DataFrame:
        """
        Return a DataFrame containing all records from the DOB Complaint Received dataset.

        Parameters
        ----------
        fetch_all: `bool`
            Flag indicating whether all records should be feteched.
        """

        df = self.__get_results(
            self.metadata_dob_complaints, fetch_all=fetch_all, **kwargs
        )
        return df

    def load_brownsville(self, fetch_all: bool = False) -> pd.DataFrame:
        """
        TODO: merge the housing maintenance and the complaint problems datasets
        """
        # if os.path.exists(self._DATA_PATH + self.metadata_brownsville.filename):
        #     df = pd.read_csv(self.metadata_brownsville.filename)
        #     return df

        convert_dict = {
            "complaintid" : "Int64",
            "statusid" : "Int64",
        }

        df_housing_maintenance = self.load_housing_maintenance(
            fetch_all=fetch_all,
            where="zip='11212' OR zip='11233'"
        )

        # df_housing_maintenance = df_housing_maintenance.astype(convert_dict, errors="ignore")
        min_date = min(df_housing_maintenance["statusdate"])

        df_complaint_problems = self.load_complaint_problems(
            fetch_all=fetch_all,
            select="complaintid, unittypeid, spacetypeid, "
                  +"typeid, majorcategoryid, minorcategoryid, codeid, "
                  +"statusid, statusdate, statusdescription",
            where=f"statusdate>='{min_date}'"
        )

        # df_complaint_problems = df_complaint_problems.astype(convert_dict, errors="ignore")
        merge_columns = ["complaintid", "statusdate"]

        df_brownsville = pd.merge(
            df_housing_maintenance,
            df_complaint_problems,
            on=merge_columns,
        )

        

        df_brownsville = df_brownsville[
            ['complaintid', 'buildingid', 'boroughid', 'borough', 'housenumber',
             'streetname', 'zip', 'block', 'lot', 'apartment', 'communityboard',
             'receiveddate', 'status', 'unittypeid', 'spacetypeid',
             'typeid', 'majorcategoryid', 'minorcategoryid', 'codeid', "statusdate",
             'statusdescription']
        ]

        df_brownsville.to_csv(self._DATA_PATH + self.metadata_brownsville.filename)

        return df_brownsville

    def __get_results(
        self, metadata: DatasetMetaInformation, fetch_all: bool = False, load_local=True, **kwargs
    ) -> pd.DataFrame:
        """
        Return a pandas dataframe containing all records from the specified endpoint. If a dataset is already
        cached, this method will return the stored information and update it if needed, else it will download and
        return the dataset from the NYC OpenData servers.

        Parameters
        ----------
        metadata: `DatasetMetaInfomation`
            Object containing the metadata information for the desired dataset.
        fetch_all: `bool`
            Boolean flag indicating whether to return the whole dataset or just a subset.
        """
        # Set the metadata loaded flag
        if not metadata.loaded:
            metadata.loaded = True

        # Fetch all the records for the selected dataset
        if fetch_all:

            fetch_remote = True
            # Verify that the queries for the current and previous requests are identical
            if metadata.last_query == kwargs:

                # Check if the datset is cached and the load_local flag is true
                if load_local and os.path.exists(self._DATA_PATH + metadata.filename):
                    print("Loading cached dataset...")

                    # Read the file stored in cache
                    df = pd.read_csv(self._DATA_PATH + metadata.filename, index_col=0)
                    fetch_remote = False

                    # Check if more rows have been added to the dataset
                    if metadata.cache_date < metadata.updated_on:
                        print("Updating records...")

                        kwargs["offset"] = metadata.offset

                        # Fetch the remaining records from the website
                        results = self._client.get_all(metadata.endpoint, **kwargs)
                        remote_df = pd.DataFrame.from_records(results)

                        # Append the new rows to the old dataframe and update the metadata
                        df = df.append(remote_df)

            # Fetch the whole dataset from the NYC OpenData servers
            if fetch_remote:
                print("Downloading dataset...")
                results = self._client.get_all(metadata.endpoint, **kwargs)
                df = pd.DataFrame.from_records(results)
                metadata.last_query = kwargs

            # Update the metadata for the desired dataset and store it
            metadata.offset = df.shape[0]
            metadata.cache_date = datetime.now()
            df.to_csv(self._DATA_PATH + metadata.filename)

        else:
            results = self._client.get(metadata.endpoint, **kwargs)
            df = pd.DataFrame.from_records(results)

        return df

    def __save_metadata(self) -> None:
        """
        Save the metadata information for each data source in a .pickle file.
        """
        objs = (
            self.metadata_311,
            self.metadata_complaint_problems,
            self.metadata_housing_maintenance,
            self.metadata_dob_complaints,
            self.metadata_brownsville
        )

        with open(self._DATA_PATH + "./metadata.pickle", "wb") as f:
            pickle.dump(objs, f)

    def __load_metadata(self) -> None:
        """
        Load the metadata information. If the pickle file exists, it loads the previous DatasetMetaInformation
        state for each of the data sources, else it fetches the information from the NYC OpenData servers.
        """
        # Fetch meta information from the proposed datasets if not already stored
        if not os.path.exists(self._DATA_PATH + "./metadata.pickle"):
            self.metadata_311 = DatasetMetaInformation(
                self._client, "erm2-nwe9"
            )
            self.metadata_complaint_problems = DatasetMetaInformation(
                self._client, "a2nx-4u46"
            )
            self.metadata_housing_maintenance = DatasetMetaInformation(
                self._client, "uwyv-629c"
            )
            self.metadata_dob_complaints = DatasetMetaInformation(
                self._client, "eabe-havv"
            )

            date_1 = self.metadata_housing_maintenance.updated_on.timestamp()
            date_2 = self.metadata_complaint_problems.updated_on.timestamp()

            self.metadata_brownsville = DatasetMetaInformation(
                id="",
                name="Brownsville complaints",
                attribution="Team Survey-Fix",
                category="Housing complaints",
                description="Complaint reports on the Brownsville area",
                rowsUpdatedAt=min(date_1, date_2) 
            )
        else:
            # Load the metadata information from storage
            with open(self._DATA_PATH + "./metadata.pickle", "rb") as f:
                objs = pickle.load(f)
                self.metadata_311 = objs[0]
                self.metadata_complaint_problems = objs[1]
                self.metadata_housing_maintenance = objs[2]
                self.metadata_dob_complaints = objs[3]
                self.metadata_brownsville = objs[4]

        self.metadata_311.loaded = False
        self.metadata_complaint_problems.loaded = False
        self.metadata_housing_maintenance.loaded = False
        self.metadata_dob_complaints.loaded = False
        self.metadata_brownsville.loaded = False

    def close(self):
        """
        Close the SodaPY Socrata client
        """
        self.__save_metadata()
        self._client.close()

    def __enter__(self):
        """
        Open the context manager
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Close the context manager
        """
        return self.close()
