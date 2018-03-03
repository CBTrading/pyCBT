import numpy as np
import pandas as pd
import oandapyV20
from collections import OrderedDict
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
from oandapyV20.types import DateTime

import pytz
from dateutil.parser import parse
from datetime import datetime, timedelta

from pyCBT.constants import OHLCV
from .account import Config


class Candles(object):

    def __init__(self, account, instrument, resolution, from_date, to_date=None, timezone=None):
        # ERROR: remove config object. This class is meant to be used from cbt-config.py
        # get config summary
        config = Config()
        self.account_summary = config.get_from_file(open(config.get_filename(account), "r"))
        r_params = {
            "timeout": self.account_summary.pop("timeout")
        }
        # instantiate API client
        # ERROR: remove client functionality and make API client input parameter
        self.api = oandapyV20.API(
            access_token=self.account_summary.pop("token"),
            environment=self.account_summary.pop("environment"),
            request_params=r_params
        )
        # define params of candles
        self.instrument = instrument
        self.resolution = resolution
        # ERROR: this should be timezone or "UTC". Better yet, default to "UTC" in constructor
        self.timezone = timezone or self.account_summary.pop("timezone")
        self.from_date = self.timezone_to_utc(from_date)
        # ERROR: this will break if to_date==None
        self.to_date = self.timezone_to_utc(to_date)
        self.candles_params = {
            "granularity": self.resolution,
            "alignmentTimezone": self.timezone,
            "from": self.from_date,
            "to": self.to_date
        }
        # generate request for candles
        self.requests = InstrumentsCandlesFactory(self.instrument, self.candles_params)

    def timezone_to_utc(self, datetime_str, in_fmt=None, timezone=None):
        """Turns a datetime string in a given timezone into a datetime string in UTC

        Given 'datetime_str' in a arbitrary format and a 'timezone', this method
        returns a version of the same datetime in the RFC3339 format.

        Parameters
        ----------
        datetime_str: str
            a string representation of a datetime.
        in_fmt: str
            format of the given datetime string. Valid values are:
                * RFC3339 (default): {Y}-{m}-{d}T{H}:{M}:{S}Z
                * UNIX: {s}.{nnnnnnnnn}
                * None: any valid datetime string for dateutil.parser.parse
        timezone: str
            the name of a timezone (ex. EST, America/Caracas).
        """
        # parse arguments
        _timezone = timezone or self.timezone
        # take an arbitrary datetime string and turn it into a datetime object
        # parse datetime_str
        dt = timedelta(np.float64(dt_str)) + datetime(1970, 1, 1) if in_fmt == "UNIX" else parse(datetime_str)
        # if timezone not UTC
        if _timezone != "UTC":
        #   get timezone from database
            tz = pytz.timezone(_timezone)
        #   check if datetime_str has timezone information
        #   if has not:
            if dt.tzinfo is None:
        #       update tzinfo to tz
                dt = dt.replace(tzinfo=tz)
        #   because oandapyV20 uses UTC by default, convert current datetime to this system
            dt = dt.astimezone(pytz.UTC)
        # convert to string of RFC3339 format and return
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def utc_to_timezone(self, datetime_str, in_fmt=None, timezone=None):
        """Turns a datetime string in UTC into a datetime string in a given timezone

        Given 'datetime_str' in RFC3339 format and UTC, this method
        returns a version of the same datetime in a ISO-like format
        (%Y-%m-%dT%H:%M:%SZ%z).

        Parameters
        ----------
        datetime_str: str
            a string representation of a datetime.
        in_fmt: str
            format of the given datetime string. Valid values are:
                * RFC3339 (default): {Y}-{m}-{d}T{H}:{M}:{S}Z
                * UNIX: {s}.{nnnnnnnnn}
                * None: any valid datetime string for dateutil.parser.parse
        timezone: str
            the name of a timezone (ex. EST, America/Caracas).
        """
        # parse arguments
        _timezone = timezone or self.timezone
        # take an arbitrary datetime string and turn it into a datetime object
        # parse datetime_str
        dt = timedelta(np.float64(dt_str)) + datetime(1970, 1, 1) if in_fmt == "UNIX" else parse(datetime_str)
        dt.replace(tzinfo=pytz.UTC)
        # if timezone not UTC
        if _timezone != "UTC":
        #   get timezone from database
            tz = pytz.timezone(_timezone)
        #   convert into timezone
            dt = dt.astimezone(tz)
        # convert to string of ISO-like format and return
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ%z")

    # ERROR: this will break if called consecutive times. Implement setter for the candles_response
    def _get_response(self):
        """Return response with list of candles
        """
        # initialize list of candle responses
        candles_response = []
        # get candles
        for request in self.requests:
        #   submit request
            self.api.request(request)
        #   store candle in list
            candles_response += request.response.get("candles")
        # return candles
        return candles_response

    def as_dictionary(self):
        """Return candles response as tabulated dictionary
        """
        # get candles response
        candles_response = self._get_response()
        # initialize dictionary table
        table = OrderedDict(zip(["DATETIME"]+OHLCV, [[], [], [], [], [], []]))
        # for each candle in response
        for candle in candles_response:
        #   only take completed candles
            if candle.pop("complete"):
        #       for each keyword (ex.: volume, time) in candle
                for kw in candle:
        #           store prices in table
                    if kw in ["bid", "ask", "mid"]:
                        table["OPEN"] += [candle[kw]["o"]]
                        table["HIGH"] += [candle[kw]["h"]]
                        table["LOW"] += [candle[kw]["l"]]
                        table["CLOSE"] += [candle[kw]["c"]]
        #           store volume in table
                    elif kw == "volume":
                        table["VOLUME"] += [candle[kw]]
        #           store datetime in table
                    elif kw == "time":
                        table["DATETIME"] += [self.utc_to_timezone(candle[kw])]
        return table

    def as_dataframe(self):
        """Return candles response as Pandas DataFrame
        """
        # get dictionary table
        d = self.as_dictionary()
        # define index
        i = d.pop("DATETIME")
        # define table
        table = pd.DataFrame(d, index=i)
        return table
