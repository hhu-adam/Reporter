"""
This script converts a given pandas DataFrame into a latex table given
a certain specification.
"""

import os
import re
import calendar
from datetime import date, datetime

import typer

from modules.log_crawler import LogCrawler
from modules.aggregator import Aggregator
from modules.formatter import Formatter
from modules.utils import relative_path, get_timeframe


def main(start: str = date.today().replace(day=1).strftime("%Y-%m-%d"),
         end: str = date.today().strftime("%Y-%m-%d"),
         month: str = "",
         full: bool = False):
    """
    Create a Latex booktabs cross-table from daily .csv logs from the beginning of the current
    month until the current day.


    If no date is provided for the --end flag, a report is generated beginning from START
    and ending at todays date.

    If no date is provided for the --start flag, a report is generated beginning from the 
    first day of the current month and ending at the END date.

    With the --month flag the user can specify to get a report by month. For example
    --month 3 would result in a report compiled for all logs created in march.
    """
    date_f = "%Y-%m-%d"
    lc = LogCrawler(log_dir=os.environ['LOG_DIR'], date_format=date_f)
    ag = Aggregator()

    if month != "":
        assert re.search(
            r'0[1-9]|1[0-2]', month) is not None, "Month format: 01, 02, ..., 09, 10, 11, 12"

        start = f"2025-{month}-01"
        end_month = calendar.monthrange(datetime.now().year, int(month))[1]
        end = f"2025-{month}-{end_month}"

    if full:
        start, end = lc.get_time_span_strs()
        dfs = lc.extract_all_log_data_frames()
    else:
        dfs = lc.extract_log_data_frames(start, end)

    start = datetime.strptime(start, date_f).date()
    end = datetime.strptime(end, date_f).date()

    measured_days = len(lc.get_measured_dates(start, end))
    interval_days = get_timeframe(start, end)
    agg = ag.aggregate_over_interval(dfs)

    fm = Formatter(agg, start, end, date_f)

    latex_table = fm.generate_report(measured_days, interval_days)

    f = open(relative_path(__file__,
                           f"reports/report-{start}-{end}.tex"), mode='w', encoding='utf_8')
    f.write(latex_table)


if __name__ == "__main__":
    typer.run(main)
