import pytz
from dateutil.parser import parse
from datetime import datetime, timedelta

# ERROR: join this methods
def tz_to_utc(datetime_str=None, timezone=None):
    """Turns a datetime string in a given timezone into a datetime string in UTC

    Given 'datetime_str' in a arbitrary format and a 'timezone', this method
    returns a version of the same datetime in the RFC3339 format.

    The given 'datetime_str' can be in any valid format to dateutil.parser.parse.
    or in UNIX timestamp.

    Parameters
    ----------
    datetime_str: str
        a string representation of a datetime.

    timezone: str
        the name of a timezone (ex. EST, America/Caracas).
    """
    # ERROR: implement parser as a decorator
    if datetime_str is None:
        dt = datetime.now(tzinfo=pytz.timezone(timezone))
    else:
        try:
            dt = parse(datetime_str)
        except ValueError:
            try:
                dt = timedelta(np.float64(dt_str)) + datetime(1970, 1, 1)
            except ValueError:
                raise ValueError("Unknown datetime format for {}.".format(datetime_str))
    if timezone is None: timezone = "UTC"

    if timezone != "UTC":
        tz = pytz.timezone(timezone)
        if dt.tzinfo is None: dt = dt.replace(tzinfo=tz)
        dt = dt.astimezone(pytz.UTC)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def utc_to_tz(datetime_str=None, timezone=None):
    """Turns a datetime string in UTC into a datetime string in a given timezone

    Given 'datetime_str' in RFC3339 format and UTC, this method returns a version
    of the same datetime in a ISO-like format (%Y-%m-%dT%H:%M:%SZ%z).

    The given 'datetime_str' can be in any valid format to dateutil.parser.parse.
    or in UNIX timestamp.

    Parameters
    ----------
    datetime_str: str
        a string representation of a datetime.
    timezone: str
        the name of a timezone (ex. EST, America/Caracas).
    """
    # ERROR: implement parser as a decorator
    if datetime_str is None:
        dt = datetime.now(tzinfo=pytz.timezone(timezone))
    else:
        try:
            dt = parse(datetime_str)
        except ValueError:
            try:
                dt = timedelta(np.float64(dt_str)) + datetime(1970, 1, 1)
            except ValueError:
                raise ValueError("Unknown datetime format for {}.".format(datetime_str))
    if timezone is None: timezone = "UTC"

    dt.replace(tzinfo=pytz.UTC)
    if timezone != "UTC":
        tz = pytz.timezone(timezone)
        dt = dt.astimezone(tz)
    # ERROR: implement format string as decorator to ease changing to UNIX
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ%z")
