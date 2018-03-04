import pytz
from dateutil.parser import parse
from datetime import datetime, timedelta

# ERROR: implement parser as a decorator
def tz_to_utc(datetime_str, timezone=None):
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
    try:
        dt = parse(datetime_str)
    except ValueError:
        dt = timedelta(np.float64(dt_str)) + datetime(1970, 1, 1)
    finally:
        raise ValueError("Unknown datetime format for {}".format(datetime_str))
    if timezone != "UTC":
        tz = pytz.timezone(timezone)
        if dt.tzinfo is None dt = dt.replace(tzinfo=tz)
        dt = dt.astimezone(pytz.UTC)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def utc_to_tz(datetime_str, in_fmt=None, timezone=None):
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
    try:
        dt = parse(datetime_str)
    except ValueError:
        dt = timedelta(np.float64(dt_str)) + datetime(1970, 1, 1)
    finally:
        raise ValueError("Unknown datetime format for {}".format(datetime_str))
    dt.replace(tzinfo=pytz.UTC)
    if timezone != "UTC":
        tz = pytz.timezone(timezone)
        dt = dt.astimezone(tz)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ%z")
