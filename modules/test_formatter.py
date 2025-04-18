import unittest
import re
from datetime import date

from formatter import Formatter

from pandas import DataFrame


class TestFormatter(unittest.TestCase):

    def test_correct_time_interval(self):
        agg = DataFrame({'country': ['US', 'DE', 'JP'],
                         'game': ['User1/Logic', 'User2/Probability', 'User3/Functions'],
                         'n': [7, 6, 5]})

        start = date(2025, 3, 1)
        end = date(2025, 3, 31)

        fmtr = Formatter(agg, start, end, "%Y-%m-%d")
        latex_table = fmtr.generate_report(31, 31)

        pattern = re.compile("from: .+ 2025-03-01 .* to: .* 2025-03-31")
        _match = re.search(pattern, latex_table)

        self.assertIsNotNone(_match)

    def test_correct_ratio_of_available_logs(self):
        agg = DataFrame({'country': ['US', 'DE', 'JP'],
                         'game': ['User1/Logic', 'User2/Probability', 'User3/Functions'],
                         'n': [7, 6, 5]})

        start = date(2025, 3, 1)
        end = date(2025, 3, 31)

        fmtr = Formatter(agg, start, end, "%Y-%m-%d")
        latex_table = fmtr.generate_report(31, 31)

        _match = re.search("days with reports: 31/31", latex_table)

        self.assertIsNotNone(_match)
