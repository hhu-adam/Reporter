from pandas import DataFrame


class NoLogsFoundError(Exception):
    """
    Simple Exception class indicating that no log-files
    could be found by the LogCrawler.
    """


class Aggregator(object):
    def __init__(self) -> None:
        pass

    def aggregate_over_interval(self, dfs: list[DataFrame]) -> DataFrame:
        """
        Returns a single DataFrame that is the results of
        merging and updating a list of DataFrames.
        """

        if len(dfs) == 0:
            raise NoLogsFoundError("No logs for given time frame found")

        agg = dfs[0]

        if len(dfs) == 1:
            return agg

        for df in dfs[1:]:
            agg = self._merge_update_data_frames(agg, df)

        return agg

    def _merge_update_data_frames(self, old_df: DataFrame, new_df: DataFrame) -> DataFrame:
        """
        Update n values by joining DataFrames w.r.t. country and game and
        adding up n values of respected tables.
        """

        req_columns = ['country', 'game', 'n']
        assert list(
            old_df.columns) == req_columns, f"Columns  of doc. DataFrame must be {req_columns} but were {old_df.columns}"
        assert list(
            new_df.columns) == req_columns, f"Columns  of new DataFrame must be {req_columns} but were {new_df.columns}"

        # Replace NaN values with zero.
        old_df = old_df.merge(new_df, how="outer", on=['country', 'game'], suffixes=[
            '_old', '_new']).fillna(0)
        # Create a new column 'n'
        old_df['n'] = old_df['n_old'] + old_df['n_new']
        # Drop the columns 'n_old' and 'n_new'
        old_df = old_df.drop(['n_old', 'n_new'], axis=1)

        return old_df
