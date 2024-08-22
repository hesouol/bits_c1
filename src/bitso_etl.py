import csv
import os

import requests
import time
import pandas as pd
from datetime import datetime, timezone
import logging

# Constants
API_URL = "https://api.bitso.com/v3/order_book/"
INTERVAL = 1  # in seconds
SAVE_INTERVAL = 6  # Save every 6 records, to run every 10 minutes change to 600

# Spread thresholds for alerts
SPREAD_THRESHOLDS = {
    'alert_0.1%': 0.1,
    'alert_0.5%': 0.5,
    'alert_1.0%': 1.0
}


class BitsoETL:
    def __init__(self, book, data=[], save_interval=SAVE_INTERVAL):
        self.book = book
        self.data = data
        self.save_interval = save_interval

    def extract(self):
        response = requests.get(API_URL, params={'book': self.book})
        if response.ok:
            response_data = response.json()
            if response_data['success']:
                return response_data['payload']

        raise ConnectionError(f"Error trying to connect to {API_URL}. http_status={response.status_code} book={self.book} response={response.text}")

    def calculate_spread(self, bid, ask):
        return (ask - bid) * 100 / ask

    def transform(self, payload):
        float_bids = [float(bid['price']) for bid in payload['bids']]
        float_asks = [float(ask['price']) for ask in payload['asks']]
        best_bid = max(float_bids)
        best_ask = min(float_asks)
        timestamp = payload['updated_at']
        spread = self.calculate_spread(bid=best_bid, ask=best_ask)
        return timestamp, best_bid, best_ask, spread

    def load(self, data):
        """
        Method for loading the data, default: writing to a partitioned parquet file
        Args:
          data: List of records to be written.
        """
        df = pd.DataFrame(data)
        now = datetime.now(timezone.utc)
        output_dir = now.strftime(f'book={self.book}/year=%Y/month=%m/day=%d')
        file_name = now.strftime(f'{self.book}_%Y%m%d%H%M%S.csv')
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, file_name)
        df.to_csv(file_path, index=False, quoting=csv.QUOTE_MINIMAL)

    def check_alerts(self, spread):
        for alert_name, threshold in SPREAD_THRESHOLDS.items():
            if spread > threshold:
                # TODO: replace with proper alert system
                logging.warning(f"{self.book} spread {spread:.3f}% exceeds {alert_name} threshold.")

    def run(self):
        try:
            payload = self.extract()
            timestamp, bid, ask, spread = self.transform(payload)
            self.check_alerts(spread)
            self.data.append({
                'orderbook_timestamp': timestamp,
                'book': self.book,
                'bid': bid,
                'ask': ask,
                'spread': spread
            })
            if len(self.data) >= self.save_interval:
                self.load(self.data)
                self.data.clear()

            time.sleep(INTERVAL)
        except Exception as e:
            logging.error(f"Error fetching data: {e}")

    def run_daemon(self):
        logging.info(f"Starting BitsoETL for book={self.book}.")
        while True:
            self.run()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Bitso ETL")
    parser.add_argument(
        "--book",
        required=True,
        type=str,
        help="Book to be extracted from Bitso api",
    )
    args = parser.parse_args()
    etl = BitsoETL(book=args.book)
    etl.run_daemon()
