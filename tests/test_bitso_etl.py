import csv
import unittest
from unittest.mock import patch, Mock
from freezegun import freeze_time

# Enabling test modules
import sys
import os

from src.bitso_etl import BitsoETL

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestBitsoETL(unittest.TestCase):

    @patch("requests.get")
    def test_extract(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "payload": "fake_payload"
        }
        mock_request.return_value = mock_response

        subject = BitsoETL(book='fake_book')
        result_payload = subject.extract()
        self.assertEqual(result_payload, "fake_payload")

    @patch("requests.get")
    def test_extract_fail(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "success": False,
            "payload": "ERROR"
        }
        mock_request.return_value = mock_response

        subject = BitsoETL(book='fake_book')
        self.assertRaises(ConnectionError, subject.extract)

    def test_transform(self):
        subject = BitsoETL(book='fake_book')
        mock_payload = {'updated_at': 'fake_updated_at', 'sequence': 'fake_sequence',
            'bids': [
                    {'book': 'fake_book', 'price': '100.00', 'amount': '1.0'},
                    {'book': 'fake_book', 'price': '150.00', 'amount': '1.0'}
                    ],
            'asks': [
                    {'book': 'fake_book', 'price': '100.00', 'amount': '1.0'},
                    {'book': 'fake_book', 'price': '101.00', 'amount': '1.0'}
            ]}
        updated_at, best_bid, best_ask, spread = subject.transform(mock_payload)
        self.assertEqual(updated_at, 'fake_updated_at')
        self.assertEqual(best_bid, 150)
        self.assertEqual(best_ask, 100)
        self.assertEqual(spread, -50)

    @patch("os.makedirs")
    @patch("pandas.DataFrame.to_csv")
    @freeze_time("2024-01-01")
    def test_load(self, mock_to_csv, mock_makedirs):
        fake_book = 'fake_book'
        subject = BitsoETL(book=fake_book)
        subject.load([{'fake_column': 'fake_value'}])

        expected_dir = f"book={fake_book}/year=2024/month=01/day=01"
        expected_file_path = expected_dir + "/fake_book_20240101000000.csv"

        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
        mock_to_csv.assert_called_once_with(expected_file_path, index=False, quoting=csv.QUOTE_MINIMAL)

    def test_run(self):
        subject = BitsoETL('fake_book', data=[], save_interval=2)
        subject.extract = lambda: "fake_payload"  # total_records=1
        subject.transform = lambda payload: ('fake_updated_at', 150, 100, -50) if payload == 'fake_payload' else 'error'
        subject.load = lambda data: self.assertEqual(data[0]["orderbook_timestamp"], "fake_updated_at")
        subject.run()
        self.assertEqual(1, len(subject.data))
        subject.run()
        self.assertEqual(0, len(subject.data))


if __name__ == "__main__":
    unittest.main()
