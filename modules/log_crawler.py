"""
Module docstring
"""

import os
import re
import sys
from datetime import date, datetime

from pandas import DataFrame, read_csv


class NoLogsFoundError(Exception):
    """
    Simple Exception class indicating that no log-files
    could be found by the LogCrawler.
    """


class LogCrawler(object):
    """
    The log crawler hold information about logs in the directory
    specified by the LOG_DIR env. variable. It is used to retrieve
    information such as the list of available logs, their number
    range etc.
    """

    def __init__(self, log_dir: str, date_format: str) -> None:
        self.date_format = date_format
        self.log_dir: str = log_dir
        self.logs = self._extract_log_files()

        if len(self.logs) == 0:
            raise NoLogsFoundError(
                "No log files found. See if log files are available in your log directory")

    def _extract_log_files(self) -> list[str]:
        """
        Returns a list of path strings for each log in 
        the log directory.
        """

        logs = []
        for _, __, files in os.walk(self.log_dir):
            for file in files:
                _match = re.search(
                    r'locations-[0-9]+-[0-9]+-[0-9]+\.log', file)

                if _match is None:
                    continue

                logs.append(self.log_dir + "/" + file)

        return logs

    def extract_all_log_data_frames(self) -> list[DataFrame]:
        """
        Returns a list of all available log-files in DataFrame format.
        """

        data_frames = []

        for log_file in self.logs:
            df = read_csv(log_file, delimiter=';')
            data_frames.append(df)

        return data_frames

    def extract_log_data_frames(self, start: str, end: str) -> list[DataFrame]:
        """
        Given a start and end date returns a list of DataFrames corresponding
        to the logs of the specified time interval.
        """

        data_frames = []
        start_date = datetime.strptime(start, self.date_format).date()
        end_date = datetime.strptime(end, self.date_format).date()

        for log_file in self.logs:
            _match = re.search(r'(?<=\-)\d+\-\d+\-\d+(?=.)', log_file)
            log_date = datetime.strptime(
                _match.group(0), self.date_format).date()

            if log_date >= start_date and log_date <= end_date:
                df = read_csv(log_file, delimiter=';')
                data_frames.append(df)

        return data_frames

    def get_measured_dates(self, start: str, end: str) -> list[date]:
        """
        Returns a list of dates corresponding to all available logs for the given time frame.
        """

        dates = []
        start_date = datetime.strptime(start, self.date_format).date()
        end_date = datetime.strptime(end, self.date_format).date()

        for log_file in self.logs:
            _match = re.search(r'(?<=\-)\d+\-\d+\-\d+(?=.)', log_file)

            log_date = datetime.strptime(
                _match.group(0), self.date_format).date()
            if log_date >= start_date and log_date <= end_date:
                dates.append(log_date)

        return dates

    def get_missing_dates(self, start: str, end: str) -> int:
        """
        Returns all dates that are not found to be part of the log-files-
        """

        measured_dates = len(self.get_measured_dates(start, end))
        start = datetime.strptime(start, self.date_format).date()
        end = datetime.strptime(end, self.date_format).date()

        return (end - start) - measured_dates

    def get_latest(self) -> datetime.date:
        """
        Return the latest date of a log in the log directory.
        """

        latest: datetime.date = datetime.strptime(
            "2000-01-01", self.date_format).date()

        for log in self.logs:
            date_str = re.search(r'(?<=\-)\d+\-\d+\-\d+(?=.)', log).group()
            cur_date = datetime.strptime(date_str, self.date_format).date()
            latest = max(latest, cur_date)

        return latest

    def get_earliest(self) -> datetime.date:
        """
        Return the earliest date of a log in the log directory.
        """

        earliest: datetime.date = datetime.strptime(
            "3000-01-01", self.date_format).date()

        for log in self.logs:
            date_str = re.search(r'(?<=\-)\d+\-\d+\-\d+(?=.)', log).group()
            cur_date = datetime.strptime(date_str, self.date_format).date()
            earliest = min(earliest, cur_date)

        return earliest

    def get_time_span(self) -> tuple[datetime.date]:
        """
        Return a tuple with the earliest and latest dates available
        in the logs of the log directory
        """

        return self.get_latest(), self.get_earliest()
