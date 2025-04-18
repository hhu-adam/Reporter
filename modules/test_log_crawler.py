import unittest
from datetime import date

from log_crawler import LogCrawler


class TestLogCrawler(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.lc = LogCrawler(
            log_dir="./test_files", date_format="%Y-%m-%d")

    def test_correct_amount_of_data_frames_generated(self):
        dfs = self.lc.extract_log_data_frames("2025-04-13", "2025-04-17")
        self.assertEqual(len(dfs), 5)

    def test_correct_amount_of_dates_are_generated(self):
        dates = self.lc.get_measured_dates("2025-04-07", "2025-04-17")
        self.assertEqual(len(dates), 11)

    def test_all_data_frames_are_extracted(self):
        dfs = self.lc.extract_all_log_data_frames()
        self.assertEqual(len(dfs), 12)

    def test_get_earliest_log_date(self):
        res = self.lc.get_earliest()
        exp = date(2025, 4, 6)
        self.assertEqual(res, exp)

    def test_get_latest_log_date(self):
        res = self.lc.get_latest()
        exp = date(2025, 4, 17)
        self.assertEqual(res, exp)


if __name__ == '__main__':
    unittest.main()
