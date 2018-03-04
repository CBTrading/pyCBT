import numpy as np
import pandas as pd
import oandapyV20
from collections import OrderedDict
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
from oandapyV20.types import DateTime

from pyCBT.constants import OHLCV
from .account import Config
from .timezone import tz_to_utc, utc_to_tz


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
        self.from_date = tz_to_utc(from_date, timezone=self.timezone)
        self.to_date = tz_to_utc(to_date, timezone=self.timezone)
        self.candles_params = {
            "granularity": self.resolution,
            "alignmentTimezone": self.timezone,
            "from": self.from_date,
            "to": self.to_date
        }
        # generate request for candles
        self.requests = InstrumentsCandlesFactory(self.instrument, self.candles_params)

        # initialize response
        self._response = None

        print self.account_summary

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
                        table["DATETIME"] += [utc_to_tz(candle[kw], timezone=self.timezone)]
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
