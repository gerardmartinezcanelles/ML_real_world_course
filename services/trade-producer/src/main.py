from typing import Dict, List

from loguru import logger
from quixstreams import Application

from src.config import config
from src.kraken_api.websocket import KrakenWebsocketTradeAPI


def produce_trades(
    kafka_broker_adress: str,
    kafka_topic_name: str,
    product_ids: List[str],
    live_or_historical: str,
    last_n_days: int,
) -> None:
    """
    Reads trades from the Kraken websocket API and saves them into a Kafka topic.

    Args:
        kafka_broker_addres (str): The address of the Kafka broker.
        kafka_topic_name (str): The name of the Kafka topic.
        product_ids (List[str]): The product IDs for which we want to get the trades.
        live_or_historical (str): Whether we want to get live or historical data.
        last_n_days (int): The number of days from which we want to get historical data.

    Returns:
        None
    """
    # Let's keep it simple for now, but please do this validation in the
    # config.py file using pydantic settings
    assert live_or_historical in {
        'live',
        'historical',
    }, f'Invalid value for live_or_historical: {live_or_historical}'

    app = Application(broker_address=kafka_broker_adress)

    # Define a topic "my_topic" with JSON serialization
    topic = app.topic(name=kafka_topic_name, value_serializer='json')

    # event = {"id": "1", "text": "Lorem ipsum dolor sit amet"}

    # Create an instance of the Kraken API
    if live_or_historical == 'live':
        kraken_api = KrakenWebsocketTradeAPI(product_ids=product_ids)
    else:
        # I need historical data, so
        from src.kraken_api.rest import KrakenRestAPI  # KrakenRestAPIMultipleProducts

        kraken_api = KrakenRestAPI(
            product_id=product_ids,
            last_n_days=last_n_days,
        )

    logger.info('Creating the producer')

    # Create a Producer instance
    with app.get_producer() as producer:
        while True:
            # check if we are done fetching historical data
            if kraken_api.is_done():
                logger.info('Done fetching historical data')
                break

            # Get trades from the Kraken API
            trades: List[Dict] = kraken_api.get_trades()

            for trade in trades:
                # Serialize an event using the defined Topic
                message = topic.serialize(
                    key=trade['product_id'], 
                    value=trade,
                    timestamp_ms=trade['time'] * 1000
                )

                # Produce a message into the Kafka topic
                producer.produce(
                    topic=topic.name, 
                    value=message.value, 
                    key=message.key,
                    timestamp=message.timestamp
                )

                #logger.info('Message sent !')
                logger.info(trade)

                #from time import sleep

                #sleep(1)


if __name__ == '__main__':
    try:
        produce_trades(
            kafka_broker_adress=config.kafka_broker_address,  # "redpanda-0:9092", #localhost:19092 , "redpanda-0:9092"
            kafka_topic_name=config.kafka_topic_name,
            # Since just reading one using KrakenRestAPI instead of KrakenRestAPIMultipleProducts . 
            # When switching to KrakenRestAPIMultipleProducts  change following line for config.product_ids
            product_ids=config.product_ids[0],
            # extra parameters I need when running the trade_producer against
            # historical data from the KrakenREST API
            live_or_historical=config.live_or_historical,
            last_n_days=config.last_n_days,
        )
    except KeyboardInterrupt:
        logger.info("Exiting")