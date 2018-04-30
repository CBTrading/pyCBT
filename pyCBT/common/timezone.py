import pytz, re
import numpy as np
from dateutil.parser import parse
from datetime import datetime, timedelta


# TODO: implement resolution (H1, D, etc.) to timedelta to download only data needed in correlation,
#       volatility and other charts
# TODO: implement parser as a decorator
# TODO: implement checking if datetime_str is JSON or UNIX
# TODO: time parsing will break when replacing months with different number of days
def parse_tz(datetime_str=None, in_tz="America/Caracas", remove_pattern=None, replace_pattern=None):
    if datetime_str is None:
        dt = datetime.now(tz=pytz.timezone(in_tz))
    else:
        if replace_pattern:
            m1 = re.findall(replace_pattern[0], datetime_str)
            m2 = re.findall(replace_pattern[1], datetime_str)
            if m2:
                _ = m2.pop()
                datetime_str = datetime_str.replace(_, "")
                datetime_str = datetime_str.replace(m1.pop(), _.strip("()"))
                datetime_str = datetime_str.strip()
        if remove_pattern:
            m = re.findall(remove_pattern, datetime_str)
            if m:
                datetime_str = datetime_str.replace(m.pop(), "")
        try:
            dt = parse(datetime_str)
        except ValueError:
            try:
                dt = timedelta(np.float64(datetime_str)) + datetime(1970, 1, 1)
            except ValueError:
                raise ValueError("Unknown datetime format for {}.".format(datetime_str))

    if dt.tzinfo is None: dt = pytz.timezone(in_tz).localize(dt, is_dst=False)

    return dt

# TODO: check if need to parse or if datetime is already a datetime object
def timezone_shift(datetime_str=None, in_tz="America/Caracas", out_tz="UTC", fmt="RFC3339", remove_pattern=None, replace_pattern=None):
    """Turns a datetime string from one timezone to another in a given format

    Given a datetime string in a timezone 'in_tz', this function performs the
    conversion to 'out_tz' (only if 'in_tz' not equal to 'out_tz') and returns
    the result in a given format 'fmt'.

    Parameters
    ----------
    datetime_str: str
        A string representation of a datetime.
    in_tz, out_tz: str
        The name of a timezone (ex. EST, America/Caracas).
    fmt: str
        A datetime format string (valid for datetime.strftime)
        or one of the options:
            - RFC3339
            - UNIX
            - JSON
        Any the listed options will be in UTC regardless of 'out_tz'.
    """
    dt = parse_tz(datetime_str, in_tz, remove_pattern, replace_pattern)
    if fmt in ["RFC3339", "UNIX", "JSON"]: out_tz = "UTC"
    if in_tz != out_tz: dt = dt.astimezone(pytz.timezone(out_tz))

    # TODO: turn UNIX and JSON into strings
    if fmt == "UNIX":
        dt_str = round((dt - datetime(1970, 1, 1, tzinfo=pytz.UTC)).total_seconds(), 9)
    elif fmt == "JSON":
        dt_str = round((dt - datetime(1970, 1, 1, tzinfo=pytz.UTC)).total_seconds()*1000.0, 6)
    elif fmt == "RFC3339":
        dt_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
    # TODO: if invalid format, use ISO
        dt_str = dt.strftime(fmt)

    return dt_str
