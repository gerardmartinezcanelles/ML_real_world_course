import os
from typing import List

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())


class Config(BaseSettings):
    kafka_broker_address: str = os.environ['KAFKA_BROKER_ADDRESS']
    kafka_topic_name: str = 'trade'
    product_ids: List[str] = [
        'ETH/USD'
        # 'BTC/USD',
        # 'ETH/EUR'
    ]
    # Challenge: validate that `live_or_historical` is either
    # 'live' or 'historical' using pydantic settings.
    live_or_historical: str = os.environ['LIVE_OR_HISTORICAL'] #'historical' #'live'
    last_n_days: int = os.environ['LAST_N_DAYS']

config = Config()
