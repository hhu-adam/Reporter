"""
This script converts a given pandas DataFrame into a latex table given
a certain specification.
"""
import os
import re
import sys
import time
import calendar
from datetime import date, datetime

import typer
import pandas


class NoLogsFoundError(Exception):
    pass


def relative_path(rel_path: str) -> str:
    script_path = os.path.abspath(__file__)
    script_dir = os.path.split(script_path)[0]
    return os.path.join(script_dir, rel_path)


def extract_log_files(log_dir: str) -> list[str]:
    logs = []
    for _, __, files in os.walk(log_dir):
        for file in files:
            _match = re.search(r'locations-[0-9]+-[0-9]+-[0-9]+\.log', file)

            if _match is None:
                continue

            logs.append(log_dir + "/" + file)

    if len(logs) == 0:
        raise NoLogsFoundError(
            "No log files found. See if log files are available in your log directory")

    return logs


def get_log_range(log_list: list[str]) -> tuple[str]:
    start = re.search(r'(?<=\-)\d+\-\d+\-\d+(?=.)', log_list[0]).group()
    end = re.search(r'(?<=\-)\d+\-\d+\-\d+(?=.)', log_list[-1]).group()
    return start, end


def get_all_DataFrames(log_files: list[str]) -> list[pandas.DataFrame]:
    data_frames = []

    for log_file in log_files:
        df = pandas.read_csv(log_file, delimiter=';')
        data_frames.append(df)

    return data_frames


def get_interval_DataFrames(start: str, end: str, log_files: list[str], date_format: str) -> list[pandas.DataFrame]:
    data_frames = []
    start_date = time.strptime(start, date_format)
    end_date = time.strptime(end, date_format)

    for log_file in log_files:
        _match = re.search(r'(?<=\-)\d+\-\d+\-\d+(?=.)', log_file)

        log_date = time.strptime(_match.group(0), date_format)
        if log_date >= start_date and log_date <= end_date:
            df = pandas.read_csv(log_file, delimiter=';')
            data_frames.append(df)

    return data_frames


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


def get_location_cross_table_latex(agg: pandas.DataFrame, start: str, end: str) -> str:

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
        r"toprule", "toprule ~multicolumn{11}{c}{~large ~textbf{Timeframe: From " + start + " to " + end + "}} ~\ ~toprule", latex_table)
    latex_table = latex_table.replace('~', '\\')
    latex_table = latex_table.replace('_', '\_')
    header = "\\documentclass{standalone} \n\\usepackage{booktabs} \n\\begin{document} \n"
    footer = "\\end{document}"
    return header + latex_table + footer


def main(start: str = date.today().replace(day=1), end: str = date.today().strftime("%Y-%m-%d"), month: str = "", full: bool = False):
    """
    Create a Latex booktabs cross-table from daily .csv logs from the beginning of the current
    month until the current day.


    If no date is provided for the --end flag, a report is generated beginning from START
    and ending at todays date.

    If no date is provided for the --start flag, a report is generated beginning from the first day of the current 
    month and ending at the END date.

    With the --month flag the user can specify to get a report by month. For example
    --month 3 would result in a report compiled for all logs created in march.
    """
    date_formate = "%Y-%m-%d"
    log_dir = ""
    log_files = []

    try:
        log_dir = os.environ['LOG_DIR']
    except KeyError as no_key:
        print(
            f"Environment variable {no_key} could not be found.", file=sys.stderr)
        return

    try:
        log_files = extract_log_files(log_dir)
    except NoLogsFoundError as no_logs:
        print(no_logs, file=sys.stderr)
        return

    if month != "":
        assert re.search(
            r'0[1-9]|1[0-2]', month) is not None, "Months have to be specified in the following format: 01, 02, ..., 09, 10, 11, 12"

        start = f"2025-{month}-01"
        end_month = calendar.monthrange(datetime.now().year, int(month))[1]
        end = f"2025-{month}-{end_month}"

    if full:
        start, end = get_log_range(log_files)
        dfs = get_all_DataFrames(log_files)
    else:
        dfs = get_interval_DataFrames(start, end, log_files, date_formate)

    agg = aggregate_over_interval(dfs)
    latex_table = get_location_cross_table_latex(agg, start, end)

    f = open(relative_path(
        f"reports/report-{start}-{end}.tex"), mode='w', encoding='utf_8')
    f.write(latex_table)


if __name__ == "__main__":
    typer.run(main)
