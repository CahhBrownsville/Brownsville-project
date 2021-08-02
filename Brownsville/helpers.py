import numpy as np
import pandas as pd 
from typing import List, Union

def get_feature_occurrences_by_building(
    df:pd.DataFrame, 
    building_id:int, by:Union[List[str], str],
    find_all:bool=False, n:int=10,
    warning:bool=False
) -> pd.Series:
    """
    Returns a list of the most common features provided in the brownsville.csv dataset.
    
    Parameters:
    -----------
    df: `pd.DataFame`
        Pandas DataFrame used as the source.
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
    df_filter = (df["BuildingID"] == building_id)
    common_categories = df[df_filter][by].value_counts()

    if not find_all:
        # Limit the size of the common_categories series to n.
        # If n exceeds the size of common_categories, change n to be this szie.
        if n > len(common_categories):
            n = len(common_categories)
            if warning:
                print("n exceeds number of categories. Changing n to", n)

        common_categories = common_categories[:n]
    return common_categories

def format_BBL(borough:str, block:str, lot:str) -> str:
    borough = str(borough)
    block = str(block).zfill(5)
    lot = str(lot).zfill(4)
    
    return borough + block + lot