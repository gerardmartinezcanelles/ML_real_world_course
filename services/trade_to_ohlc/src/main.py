from datetime import timedelta

from loguru import logger
from quixstreams import Application

from src.config import config


def trade_to_olhc(
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_broker_address: str,
    ohcl_window_seconds: int,
) -> None:
    """
    Reads trades from the kafka input topic.
    Aggregates them into OHLC candles using the specificied window in `ohlc_window_seconds``
    Saves the ohloc data into another kafka topic

    Args:
        kafka_input_topic: str: Kafka topic to read trade data from
        kafka_output_topic: str: Kafka topic to write ohlc data to
        kafka_broker_address: str: Kafka broker adress
        ohcl_window_seconds: str: window size in seconds for OHLC aggregation

    Returns:
        None
    """

    # This handles all low communication with Kafka
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group='trade_to_ohlc',
        auto_offset_reset='earliest',  # process all messages from the input topic when this service starts
        # auto_create_reset="latest",  # forget about pass messages, process only the ones coming from this moment
    )

    # specify input and output topics for this application
    input_topic = app.topic(name=kafka_input_topic, value_deserializer='json')
    output_topic = app.topic(name=kafka_output_topic, value_deserializer='json')

    # Create StreamingDataFrame and applying transformations to the data
    sdf = app.dataframe(input_topic)

    def init_ohlc_candle(value: dict) -> dict:
        """
        Initialzie the OHLC candle with the first trade
        """
        return {
            'open': value['price'],
            'high': value['price'],
            'low': value['price'],
            'close': value['price'],
            'product_id': value['product_id'],
        }

    def update_ohlc_candle(ohlc_candle: dict, trade: dict) -> dict:
        """
        Update the OHLC candle with the new trade and return the updated candle

        Args:
            ohlc_candle: dict: The current OHLC candle
            trade:  The incoming trade

        Returns:
            dict: The updated OHLC candle
        """

        return {
            'open': ohlc_candle['open'],
            'high': max(ohlc_candle['high'], trade['price']),
            'low': min(ohlc_candle['low'], trade['price']),
            'close': trade['price'],
            'product_id': trade['product_id'],
        }

    # apply transformation to the incoming data - start
    # Here we need to define how we transform the incoming trades into OHLC candles
    sdf = sdf.tumbling_window(duration_ms=timedelta(seconds=ohcl_window_seconds))
    sdf = sdf.reduce(reducer=update_ohlc_candle, initializer=init_ohlc_candle).current()

    # Extract the open, high, low, close prices from the values
    # The current format of the messages is the following:
    # {
    #   'start': 171766794000,
    #   'end': 171776794000,
    #   'value':
    #   {'open': 3535.98, 'high': 3534.9 , 'low':3535.98 , 'close': 3537.11}}
    # unpacking the values
    sdf['open'] = sdf['value']['open']
    sdf['high'] = sdf['value']['high']
    sdf['low'] = sdf['value']['low']
    sdf['close'] = sdf['value']['close']
    sdf['product_id'] = sdf['value']['product_id']

    # Adding timestamp key
    sdf['timestamp'] = sdf['end']

    # Let's keep only the keys we want in our final message
    sdf = sdf[['timestamp', 'open', 'high', 'low', 'close', 'product_id']]

    # Apply transformations on the incoming data - end

    sdf = sdf.update(logger.info)

    # Publish data to the output topic
    sdf = sdf.to_topic(output_topic)

    # Run the pipeline
    app.run(sdf)


if __name__ == '__main__':
    trade_to_olhc(
        kafka_input_topic=config.kafka_input_topic,
        kafka_output_topic=config.kafka_output_topic,
        kafka_broker_address=config.kafka_broker_address,
        ohcl_window_seconds=config.ohcl_window_seconds,
    )
