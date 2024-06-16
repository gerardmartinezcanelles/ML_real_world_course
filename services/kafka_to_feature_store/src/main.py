import json
from typing import Optional

from loguru import logger
from quixstreams import Application

from src.config import config
from src.hopsworks_api import push_data_to_feature_store


def get_current_utc_sec() -> int:
    """
    Returns the current UTC time expressed in seconds since the epoch.

    Args:
        None

    Returns:
        int: The current UTC time expressed in seconds since the epoch.
    """
    from datetime import datetime, timezone

    return int(datetime.now(timezone.utc).timestamp())


def kafka_to_feature_store(
    kafka_topic: str,
    kafka_broker_address: str,
    feature_group_name: str,
    feature_group_version: int,
    buffer_size: Optional[int] = 1,
    live_or_historical: Optional[str] = 'live'
) -> None:
    """
    Reads `ohlc` data from the kafka topic and writes it to the feature store.
    More specifically, it writes the data to the feature group specified by
    - feature_group_name` and `feature_group_version`.

    Args:
        kafka_topic (str): The Kakfa topic to read from.
        kafka_broker_address (str): The address of the Kafka broker.
        feature_group_name (str): The name of the feature group to write to.
        feature_group_version (int): The version of the feature group to write to.
        live_or_historical (str): Whether saving live data to the Feature or historical data.
            Live data goes to the online feature store
            While historical data goes to the offline feature store.
    Returns:
        None
    """

    app = Application(
        broker_address=kafka_broker_address,
        consumer_group='kafka_to_feature_store',
        auto_offset_reset='earliest',
    )

    # get current UTC time in seconds
    last_saved_to_feature_store_ts = get_current_utc_sec()

    # input = app.topic(name = kafka_topic, value_deserializer='json')

    # contains the list of trades to be written to the feature store at once
    # in the buffer that will never be written to the feature store.
    buffer = []

    # Create a consumer and start a polling loop
    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[kafka_topic])

        while True:
            msg = consumer.poll(1)

            if msg is None:
                # There are no new messages in the input topic.
                # Instead of just skipping, we will check when was the last time we 
                # pushed features to the feature store.
                # If more than N minutes have passed, we will push the data to the feature store
                n_sec = 10

                logger.debug(f'No new messages in the input topic {kafka_topic}')

                if (get_current_utc_sec() - last_saved_to_feature_store_ts) > n_sec:

                    logger.debug('Exceeded timer limit! Pushing data to feature store.')

                    # push the data to the feature store
                    push_data_to_feature_store(
                        feature_group_name=feature_group_name,
                        feature_group_version=feature_group_version,
                        data=buffer,
                        online_or_offline='online' if live_or_historical == 'live' else 'offline',
                    )

                    # reset the buffer
                    buffer = []
                    
                else:
                    logger.debug('We haven\'t exceeded the timer limit yet! Skip and \
                                 continue polling messages from Kafka.')
                    # we haven't hit the timer limit, so we skip and continue polling
                    # messages from the Kafka topic
                    continue


            elif msg.error():
                logger.error('Kafka error:', msg.error())
                continue

            else:
                # Let's process message. Send to feature store
                # Step 1 --> Parse message from kafka to dictionary
                ohlc = json.loads(msg.value().decode('utf-8'))

                buffer.append(ohlc)

                # logger.info(buffer)
                # if len(buffer)>=5:
                #     breakpoint()

                if len(buffer) >= buffer_size:
                    # Step 2 --> write data to feature store
                    push_data_to_feature_store(
                        feature_group_name=feature_group_name,
                        feature_group_version=feature_group_version,
                        data=buffer,
                        online_or_offline='online' if live_or_historical == 'live' else 'offline',
                    )

                    # reset the buffer
                    buffer = []

                    # update the `last_saved_to_feature_ts` to the current time
                    last_saved_to_feature_store_ts = get_current_utc_sec()

            # Store the offset of the processed message on the Consumer
            # for the auto-commit mechanism.
            # It will send it to Kafka in the background.
            # Storing offset only after the message is processed enables at-least-once delivery
            # guarantees.
            consumer.store_offsets(message=msg)


if __name__ == '__main__':
    logger.debug(config.model_dump())
    try:
        kafka_to_feature_store(
            kafka_topic=config.kafka_topic,
            kafka_broker_address=config.kafka_broker_address,
            feature_group_name=config.feature_group_name,
            feature_group_version=config.feature_group_version,
            buffer_size=config.buffer_size,
            live_or_historical=config.live_or_historical
        )
    except KeyboardInterrupt:
        logger.info('Exiting...')
