import os

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())


class Config(BaseSettings):
    kafka_topic: str = os.environ['KAFKA_TOPIC']  #'ohlc',
    kafka_broker_address: str = os.environ['KAKFA_BROKER_ADDRESS']  #'localhost:19092',
    feature_group_name: str = os.environ['FEATURE_GROUP_NAME']  #'ohlc_feature_group',
    feature_group_version: int = os.environ['FEATURE_GROUP_VERSION']  # 1
    hopsworks_project_name: str = os.environ['HOPSWORKS_PROJECT_NAME']
    api_key_value: str = os.environ['HOPSWORKS_API_KEY']


config = Config()
