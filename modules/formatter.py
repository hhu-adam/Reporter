"""
Contains the Formatter class which is used to generate latex cross table
reports from a given (aggregated) pandas DataFrame.
"""

import re
from datetime import date
from pandas import DataFrame, crosstab


class Formatter:
    """
    Generates a report in form of a latex cross table that displays in descending
    order the countries which have the highest playtime for any particular game
    hosted on a Lean4Game server.
    """

    def __init__(self, aggregate: DataFrame, start: date, end: date, date_format: str):
        self.agg: DataFrame = aggregate
        self.start: str = start.strftime(date_format)
        self.end: str = end.strftime(date_format)

    def generate_report(self, measured_days: int, interval_days: int) -> str:
        """
        Generates a latex file showing a sorted cross tab.
        """

        c_tab = self.get_cross_table(self.agg) 
        latex_table = c_tab.fillna('').to_latex(float_format="%.2f")
        right_bounded_columns = (len(c_tab.columns))
        tabular_header = "begin{tabular}" + "{" +  "l" + "r"*right_bounded_columns +"}"
        latex_table = re.sub(r"begin{tabular}\{.*\}",
                             tabular_header, latex_table)

        latex_table = latex_table.replace('_', '\_')
        header = r"\documentclass[varwidth=\maxdimen]{standalone} \usepackage{booktabs} \begin{document} "
        preamble_1 = r"\begin{tabular}{rl} from: & " + \
            self.start + r" \\ to: & " + self.end + r"\\ \end{tabular}"
        preamble_2 = r"\hspace{10pt}days with reports: " + \
            str(measured_days) + r"/" + \
            str(interval_days) + r"\\[10pt]"
        footer = r"\end{document}"
        return header + preamble_1 + preamble_2 + latex_table + footer

    def get_cross_table(self, agg: DataFrame):
        """
        Return a row-wise and descending sorted pandas cross table.
        """

        table = self._to_sum_cross_table(agg)
        return self._sort_sum_cross_table(table)

    def _to_sum_cross_table(self, df: DataFrame) -> DataFrame:
        """
        Returns a cross table in which visit-measurements are computed into
        hourly play time on a Lean4Game server.
        """
        assert list(df.columns) == [
            'country', 'game', 'n'], f"You can only convert Dataframes with columns {['country', 'game', 'n']} not {list(df.columns)}"
        countries = df['country']
        split_column = DataFrame(df['game'].str.split("/", expand=True))
        users, games = split_column[0], split_column[1]
        ten_min_blocks = df['n']

        c_tab = crosstab(index=countries, columns=[
            users, games], values=ten_min_blocks, margins=True, aggfunc='sum')

        hour_c_tab = c_tab.map(lambda x: round(x*(1/6), 2))
        return hour_c_tab

    def _sort_sum_cross_table(self, c_tab: DataFrame) -> DataFrame:
        col_sum = c_tab.sum(axis=0)
        row_sum = c_tab.sum(axis=1)

        col_sorted = c_tab[col_sum.sort_values(ascending=False).index]
        row_and_col_sorted = col_sorted.loc[row_sum.sort_values(
            ascending=False).index]
        return row_and_col_sorted
