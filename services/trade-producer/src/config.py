import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

kafka_broker_adress = os.environ['KAFKA_BROKER_ADDRESS'] #localhost:19092" #localhost:19092 , "redpanda-0:9092"
kafka_topic_name = "trade"
product_id = 'ETH/EUR' #'BTC/USD'

# kafka_broker_adress = os.environ[
#     'KAFKA_BROKER_ADDRESS'
# ]  # localhost:19092" #localhost:19092 , "redpanda-0:9092"
# kafka_topic_name = 'trade'
# product_id = 'BTC/USD'
