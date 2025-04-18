"""
A collection of several utility function used
in several other modules.
"""

import os
from datetime import date


def relative_path(cur_dir: str, rel_path: str) -> str:
    """
    Allows to use relative paths by supplying the file
    from which to look and the relative path to the wished
    for file.
    """
    script_path = os.path.abspath(cur_dir)
    script_dir = os.path.split(script_path)[0]
    return os.path.join(script_dir, rel_path)


def get_timeframe(start: date, end: date) -> int:
    """
    Inclusively return the days between the start and end date.
    """
    return (end-start).days + 1
