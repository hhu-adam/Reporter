import unittest

from aggregator import Aggregator

from pandas import DataFrame


class TestAggregator(unittest.TestCase):

    def test_aggregate_over_interval(self):
        aggregator = Aggregator()

        df1 = DataFrame({'country': ['US', 'DE', 'JP'],
                         'game': ['Logic', 'Probability', 'Functions'],
                         'n': [1, 2, 3]})

        df2 = DataFrame({'country': ['US', 'DE', 'JP'],
                         'game': ['Logic', 'Probability', 'Functions'],
                         'n': [3, 2, 1]})

        df3 = DataFrame({'country': ['US', 'DE', 'JP'],
                         'game': ['Logic', 'Probability', 'Functions'],
                         'n': [3, 2, 1]})

        dfs = [df1, df2, df3]

        exp = DataFrame({'country': ['US', 'DE', 'JP'],
                         'game': ['Logic', 'Probability', 'Functions'],
                         'n': [7, 6, 5]})

        res = aggregator.aggregate_over_interval(
            dfs).sort_values(by='n', ascending=False).reset_index(drop=True)

        self.assertTrue(res.equals(exp))


if __name__ == '__main__':
    unittest.main()
