"""
This script converts a given pandas DataFrame into a latex table given
a certain specification.
"""
import os
import re
import sys
import time
import typer
import pandas


def relative_path(rel_path: str) -> str:
    script_path = os.path.abspath(__file__)
    script_dir = os.path.split(script_path)[0]
    return os.path.join(script_dir, rel_path)


DATE_FORMAT = "%Y-%m-%d"
LOG_DIR = relative_path("../Logging/Location/logs")


def get_interval_DataFrames(start_date, end_date) -> list[pandas.DataFrame]:
    logs = []

    for _, __, files in os.walk(LOG_DIR):
        for file in files:
            print(file)
            mtch = re.search(r'(?<=\-)\d+\-\d+\-\d+(?=.)', file)

            if mtch == None:
                continue

            log_date = time.strptime(mtch.group(0), DATE_FORMAT)
            if log_date >= start_date and log_date <= end_date:
                df = pandas.read_csv(LOG_DIR + "/" + file, delimiter=';')
                logs.append(df)

    return logs


def merge_translations(old_df: pandas.DataFrame, new_df: pandas.DataFrame) -> pandas.DataFrame:
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


def aggregate_over_interval(dfs: list[pandas.DataFrame]) -> pandas.DataFrame:
    assert len(
        dfs) > 0, "Provided list of DataFrames is empty. See if log files are available!"
    agg = dfs[0]

    if len(dfs) == 1:
        return agg

    for df in dfs[1:]:
        agg = merge_translations(agg, df)

    return agg


def to_sum_cross_table(df: pandas.DataFrame) -> pandas.DataFrame:
    assert list(df.columns) == [
        'country', 'game', 'n'], f"You can only convert Dataframes with columns {['country', 'game', 'n']} not {list(df.columns)}"
    countries = df['country']
    split_column = pandas.DataFrame(df['game'].str.split("/", expand=True))
    users, games = split_column[0], split_column[1]
    ten_min_blocks = df['n']

    ctab = pandas.crosstab(index=countries, columns=[
                           users, games], values=ten_min_blocks, margins=True, aggfunc='sum')

    def to_hours(x): return round(x*(1/6), 2)
    hctab = ctab.map(to_hours)
    return hctab


def get_location_cross_table_latex(agg: pandas.DataFrame) -> str:

    def sort_sum_cross_table(ctab: pandas.DataFrame) -> pandas.DataFrame:
        col_sum = ctab.sum(axis=0)
        row_sum = ctab.sum(axis=1)

        col_sorted = ctab[col_sum.sort_values(ascending=False).index]
        row_and_col_sorted = col_sorted.loc[row_sum.sort_values(
            ascending=False).index]
        return row_and_col_sorted

    def get_location_cross_table(agg: pandas.DataFrame):
        table = to_sum_cross_table(agg)
        return sort_sum_cross_table(table)

    sorted_table = get_location_cross_table(agg)
    latex_table = sorted_table.fillna('').to_latex(float_format="%.2f")
    latex_table = re.sub(r"begin{tabular}\{.*\}",
                         "begin{tabular}{lrrrrrrrrrr}", latex_table)
    latex_table = re.sub(
        r"toprule", "toprule ~multicolumn{11}{c}{~large ~textbf{Timeframe: From " + start_date + " to " + end_date + "}} ~\ ~toprule", latex_table)
    latex_table = latex_table.replace('~', '\\')
    latex_table = latex_table.replace('_', '\_')
    header = "\\documentclass{standalone} \n\\usepackage{booktabs} \n\\begin{document} \n"
    footer = "\\end{document}"
    return header + latex_table + footer


def main():
    # TODO: Allow aggregation from date until today
    # TODO: Allow aggregation of all logs over the whole time line
    assert len(sys.argv) == 3, "You have to provide a start and end date!"
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    sts = time.strptime(start_date, DATE_FORMAT)
    ets = time.strptime(end_date, DATE_FORMAT)

    dfs = get_interval_DataFrames(sts, ets)
    agg = aggregate_over_interval(dfs)

    latex_table = get_location_cross_table_latex(agg)

    f = open(relative_path(
        f"reports/report-{start_date}-{end_date}.tex"), mode='w')
    f.write(latex_table)
    f.close


if __name__ == "__main__":
    typer.run(main)
