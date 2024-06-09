import os

from dotenv import find_dotenv, load_dotenv

from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())

class Config(BaseSettings):
    kafka_input_topic: str = os.environ['KAFKA_INPUT_TOPIC']
    kafka_output_topic: str = os.environ['KAFKA_OUTPUT_TOPIC']
    kafka_broker_address: str = os.environ['KAFKA_BROKER_ADDRESS']
    ohcl_window_seconds: int = os.environ['OHCL_WINDOW_SECONDS']

config = Config()