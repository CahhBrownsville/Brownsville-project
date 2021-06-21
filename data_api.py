import pandas as pd
from sodapy import Socrata
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Union
import textwrap

_DOMAIN = "data.cityofnewyork.us"

@dataclass
class DatasetMetaInformation:

    endpoint:str
    name:str
    attribution:str
    category:str
    description:str
    last_update:int
    loaded:bool = False

    def __init__(self, client:Socrata, endpoint:str):
        """
        Initialize the Datset Meta Infomation class according to the provided endpoint.

        Parameters:
        -----------
        client: `Socrata`
            Socrata client used by the `Client` class.
        endpoint: `str`
            Endpoint used to fetch metadata.
        """
        results = client.get_metadata(endpoint)

        self.endpoint = results["id"]
        self.name = results["name"]
        self.attribution = results["attribution"]
        self.category = results["category"]
        self.description = results["description"]
        self.last_update = datetime.fromtimestamp(results["rowsUpdatedAt"])

    @property
    def information(self) -> str:
        """
        Returns a string containing the dataset's metadata
        """
        if not self.loaded:
            return ""

        wrapped_description  = textwrap.fill(self.description, width=80)
        description = textwrap.indent(wrapped_description, "\t\t")
        return f"{self.name}:"                                                + \
                    f"\n\t- Endpoint: {self.endpoint}"                        + \
                    f"\n\t- Description:\n{description}"                      + \
                    f"\n\t- Category: {self.category}"                        + \
                    f"\n\t- Attribution: {self.attribution}"                  + \
                    f"\n\t- Data Last Updated: {self.last_update:%m-%d-%Y}"
        


class Client(object):
    """
    This class acts as a client for fetching the datasets mentioned in the proposal, i.e., 
    the `311 Service Requests from 2010 to Present`, `Complaint Problems` and `DOB Complaints Received`.

    This class uses the Sodapy client to communicate with the NYC OpenData API.
    """

    def __init__(
        self, app_token:str="",
        username:str=None, password:str=None,
        access_token:str=None, session_adapter:str=None,
    ) -> None:
        
        # Initialize the Sodapy client
        if len(app_token) == 0:
            self._client = Socrata(_DOMAIN, None, timeout=20)
        else:
            self._client = Socrata(_DOMAIN, app_token=app_token,
                                        username=username, password=password,
                                        timeout=20)

        # Fetch meta information from the proposed datasets
        self._311_metadata = DatasetMetaInformation(self._client, "erm2-nwe9")
        self._complaint_problems_metadata = DatasetMetaInformation(self._client, "a2nx-4u46")
        self._dob_complaints_metadata = DatasetMetaInformation(self._client, "eabe-havv")

    @property
    def datasets_information(self) -> str:
        # Concatenate all of the
        s = "\n\n".join([self._311_metadata.information, 
                        self._complaint_problems_metadata.information,
                        self._dob_complaints_metadata.information])
        return s

    def load_311(self, fetch_all:bool=False, limit:int=2000, offset:int=0) -> pd.DataFrame:
        """
        Return a DataFrame containing all records from the 311 Service Requests from 2010 to Present dataset.

        Parameters
        ----------
        fetch_all: `bool`
            Flag indicating whether all records should be feteched.
        limit:
            Maximum number of rows returned in the DataFrame. Default = 2000.
        offset: 
            Dataset page offset used when fetching the records. Default = 0.
        """

        # Set the metadata loaded flag
        if not self._311_metadata.loaded:
            self._311_metadata.loaded = True

        df = self.__get_results(self._311_metadata.endpoint,
                                    fetch_all=fetch_all, limit=limit, 
                                    offset=offset)
        
        return df

    def load_complaint_problems(self, fetch_all:bool=False, limit:int=2000, offset:int=0) -> pd.DataFrame:
        """
        Return a DataFrame containing all records from the Complaint Problems dataset.
        
        Parameters
        ----------
        fetch_all: `bool`
            Flag indicating whether all records should be feteched.
        limit:
            Maximum number of rows returned in the DataFrame. Default = 2000.
        offset: 
            Dataset page offset used when fetching the records. Default = 0.
        """
        # Set the metadata loaded flag
        if not self._complaint_problems_metadata.loaded:
            self._complaint_problems_metadata.loaded = True

        df = self.__get_results(self._complaint_problems_metadata.endpoint,
                                    fetch_all=fetch_all, limit=limit, 
                                    offset=offset)
        
        return df

    def load_dob_complaints(self, fetch_all:bool=False, limit:int=2000, offset:int=0) -> pd.DataFrame:
        """
        Return a DataFrame containing all records from the DOB Complaint Received dataset.

        Parameters
        ----------
        fetch_all: `bool`
            Flag indicating whether all records should be feteched.
        limit:
            Maximum number of rows returned in the DataFrame. Default = 2000.
        offset: 
            Dataset page offset used when fetching the records. Default = 0.
        """
        # Set the metadata loaded flag
        if not self._dob_complaints_metadata.loaded:
            self._dob_complaints_metadata.loaded = True
        
        df = self.__get_results(self._dob_complaints_metadata.endpoint,
                                    fetch_all=fetch_all, limit=limit, 
                                    offset=offset)
        return df

    def __get_results(
        self, endpoint:str,
        fetch_all:bool=False, 
        limit:int=2000, offset:int=0
    ) -> pd.DataFrame:
        """
        """

        # Return a dataset containing all records from the specified endpoint
        if fetch_all:
            results = self._client.get(endpoint)
        else:
            results = self._client.get(endpoint, limit=limit, offset=offset)
        
        return pd.DataFrame.from_records(results)
    
