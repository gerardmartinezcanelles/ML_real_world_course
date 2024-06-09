import hopsworks
import pandas as pd

from src.config import config

def push_data_to_feature_store(
    feature_group_name: str,
    feature_group_version :str,
    data : dict
) -> None:
    """
    Pushes given `data` to the feature store, writing it to the feature group
    with name `feature_group_name` and version `feature_group_version``

    Args:
        feature_group_name (str) : The name of the feature group to write to.
        feature_group_version (str): The version of the feature group to write to.
        data (dict): The data to write to the feature store.
    """

    project = hopsworks.login(
        project= config.hopsworks_project_name,
        api_key_value = config.api_key_value
    )

    # Get feature store
    feature_store = project.get_feature_store()

    # Get or create the feature group where we will be saving feature data to

    # Get or create the 'transactions' feature group
    ohlc_feature_group = feature_store.get_or_create_feature_group(
        name = feature_group_name,
        version= feature_group_version,
        description="OHLC data coming from Kraken",
        primary_key=["product_id","timestamp"],
        event_time="timestamp",
        online_enabled=True
    )

    # Transform data into pandas dataframe
    data = pd.DataFrame([data])
    
    # Insert data into feature group
    ohlc_feature_group.insert(data)