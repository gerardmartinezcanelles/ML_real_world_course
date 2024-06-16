import datetime
from time import sleep
import json
from typing import Dict, List, Tuple

from loguru import logger


class KrakenRestAPI:
    URL = 'https://api.kraken.com/0/public/Trades?pair={product_id}&since={since_sec}'

    def __init__(
        self,
        product_id: str,
        last_n_days: int,
    ) -> None:
        """
        Returns the from_ms and to_ms timestamps for the historical data.
        These values are computed using today's date at midnight and the last_n_days.

        Args:
            last_n_days (int): The number of days from which we want to get historical data.

        Returns:
            Tuple[int, int]: A tuple containing the from_ms and to_ms timestamps.
        """

        self.product_id = product_id
        self.from_ms, self.to_ms = self._init_from_to_ms(last_n_days)

        logger.debug(
            f'Initializing KrakenRestAPI: from_ms={self.from_ms}, to_ms={self.to_ms}'
        )

        # Enriching logger
        logger.debug(
            f"Initializing KrakenRestAPI: from={datetime.datetime.fromtimestamp(self.from_ms/1000).strftime('%Y-%m-%d %H:%M:%S')}, to={datetime.datetime.fromtimestamp(self.to_ms/1000).strftime('%Y-%m-%d %H:%M:%S')}"
        )

        #breakpoint()

        # the timestamp from which we want to fetch historical data
        # this will be updated after each batch of trades is fetched from the API
        # self.since_ms = from_ms
        self.last_trade_ms = self.from_ms

        # are we done fetching historical data?
        # Yes, if the last batch of trades has a data['result'][product_id]['last'] >= self.to_ms
        self._is_done = False

    @staticmethod
    def _init_from_to_ms(last_n_days: int) -> Tuple[int, int]:
        """
        Returns the from_ms and to_ms timestamps for the historical data.
        These values are computed using today's date at midnight and the last_n_days.

        Args:
            last_n_days (int): The number of days from which we want to get historical data.

        Returns:
            Tuple[int, int]: A tuple containing the from_ms and to_ms timestamps.
        """
        # get the current date at midnight using UTC
        from datetime import datetime, timezone

        today_date = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # today_date to milliseconds
        to_ms = int(today_date.timestamp() * 1000)

        # from_ms is last_n_days ago from today, so
        from_ms = to_ms - last_n_days * 24 * 60 * 60 * 1000

        return from_ms, to_ms

    def get_trades(self) -> List[Dict]:
        """
        Fetches a batch of trades from the Kraken Rest API and returns them as a list
        of dictionaries.

        Args:
            None

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary contains the trade data.
        """
        import requests

        payload = {}
        headers = {'Accept': 'application/json'}

        # replacing the placeholders in the URL with the actual values for
        # - product_id
        # - since_ms
        since_sec = self.last_trade_ms // 1000
        url = self.URL.format(product_id=self.product_id, since_sec=since_sec)

        response = requests.request('GET', url, headers=headers, data=payload)

        # parse string into dictionary
        data = json.loads(response.text)

        # TODO/CHALLENGE
        # It can happen that we get an error response from KrakenRESTAP like the following:
        # data = {'error': ['EGeneral:Too many requests']}
        # To solve this have several options
        #
        # Option 1. Check if the `error` key is present in the `data` and has
        # a non-empty list value. If so, we could raise an exception, or even better, implment
        # a retry mechanism, using a library like `retry` https://github.com/invl/retry
        #
        # Option 2. Simply slow down the rate at which we are making requests to the Kraken API,
        # and cross your fingers.
        #
        # Option 3. Implement both Option 1 and Option 2, so you don't need to cross your fingers.


        # TODO: check if there is an error in the response, right now we don't do any
        # error handling
        if ('error' in data) and ('EGeneral:Too many requests' in data['error']):
            # slow down the rate at which we are making requests to the Kraken API
            logger.info('Too many requests. Sleeping for 30 seconds')
            sleep(30)   

        # little trick. Instead of initializing an empty list and appending to it, you
        # can use a list comprehension to do the same thing
        trades = [
            {
                'price': float(trade[0]),
                'volume': float(trade[1]),
                'time': int(trade[2]),
                'product_id': self.product_id,
            }
            for trade in data['result'][self.product_id]
        ]

        # filter out trades that are after the end timestamp
        trades = [trade for trade in trades if trade['time'] <= self.to_ms // 1000]

        # check if we are done fetching historical data
        last_ts_in_ns = int(data['result']['last'])
        self.last_trade_ms = last_ts_in_ns // 1_000_000
        self._is_done = self.last_trade_ms >= self.to_ms

        # breakpoint()

        logger.debug(f'Fetched {len(trades)} trades')
        # log the last trade timestamp
        logger.debug(f'Last trade timestamp: {self.last_trade_ms}')
        # log the last trade timestamp in hour
        logger.debug(f"Last trade hour: {datetime.datetime.fromtimestamp(self.last_trade_ms/1000).strftime('%Y-%m-%d %H:%M:%S')}")

        # slow down the rate at which we are making requests to the Kraken API
        sleep(1)

        return trades

    def is_done(self) -> bool:
        return self._is_done
        # return self.since_ms >= self.to_ms



class KrakenRestAPIMultipleProducts:
    def __init__(
        self,
        product_ids: List[str],
        last_n_days: int,
    ) -> None:
        self.product_ids = product_ids

        self.kraken_apis = [
            KrakenRestAPI(product_id=product_id, last_n_days=last_n_days)
            for product_id in product_ids
        ]

    def get_trades(self) -> List[Dict]:
        """
        Gets trade data from each kraken_api in self.kraken_apis and retuns a list
        with all trades from all kraken_apis.

        Args:
            None

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary contains the trade
            data, for all product_ids in self.product_ids
        """
        trades: List[Dict] = []

        for kraken_api in self.kraken_apis:

            if kraken_api.is_done():
                # if we are done fetching historical data for this product_id, skip it
                continue
            else:
                trades += kraken_api.get_trades()

        return trades

    def is_done(self) -> bool:
        """
        Returns True if all kraken_apis in self.kraken_apis are done fetching historical.
        It returns False otherwise.
        """
        for kraken_api in self.kraken_apis:
            if not kraken_api.is_done():
                return False
            
        return True


# print(KrakenRestAPI._init_from_to_ms(10))
#kraken_api = KrakenRestAPI(product_ids=['ETH/USD'], last_n_days=2)
#kraken_api.get_trades()
