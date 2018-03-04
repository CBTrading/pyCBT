import numpy as np
import pandas as pd
import oandapyV20
from collections import OrderedDict
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
from oandapyV20.types import DateTime

from pyCBT.constants import OHLCV
from .account import Config
from pyCBT.tools.timezone import timezone_shift


class Candles(object):
    """Build candles for a given 'instrument' tradeable trough a given API 'client'

    Given an API 'client', a 'instrument', a time 'resolution' and a 'from_date'
    and 'to_date' both in 'timezone', this class build the corresponding
    candlesticks, aligned to the same 'timezone'.

    Parameters
    ----------
    client: a account.Client() instance
        The API client stablishing connection to OANDA.
    instrument: str
        The instrument for which to get the candlesticks.
    resolution:
        The time resolution (granularity) of the candlesticks.
    from_date, to_date: str
        The datetimes range of the candlesticks. 'to_date' defaults to now in the
        given 'timezone'.
    timezone: str
        The timezone of the given datetimes. Also used to align the candlesticks.
        Defaults to timezone in the config file (see '.account.Config').
    """

    def __init__(self, client, instrument, resolution, from_date, to_date=None, timezone=None):
        self.client = client
        self.account_summary = client.account_summary
        self.api = client.api
        # define params of candles
        self.instrument = instrument
        self.resolution = resolution
        self.timezone = timezone or self.account_summary.pop("timezone")
        self.from_date = timezone_shift(from_date, in_tz=self.timezone)
        self.to_date = timezone_shift(to_date, in_tz=self.timezone)
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
        # initialize dictionary table
        self._dict_table = None
        # initialize dataframe table
        self._dataframe_table = None

        print self.account_summary

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

    def set_response(self):
        """Set response for candles request
        """
        self._response = self._get_response()
        return None

    def as_dictionary(self):
        """Return candles response as tabulated dictionary
        """
        if self._dict_table is not None: return self._dict_table
        # get candles response
        if self._response is None: self.set_response()
        # initialize dictionary table
        table = OrderedDict(zip(["DATETIME"]+OHLCV, [[], [], [], [], [], []]))
        # for each candle in response
        for candle in self._response:
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
        # ERROR: check this is truth:
        #           candles are aligned to self.timezone, but their datetime is is
        #           still in UTC, so it has to be converted to self.timezone
                        table["DATETIME"] += [timezone_shift(candle[kw], in_tz="UTC", out_tz=self.timezone)]
        self._dict_table = table
        return table

    def as_dataframe(self):
        """Return candles response as Pandas DataFrame
        """
        if self._dataframe_table is not None: return self._dataframe_table
        # get dictionary table
        d = self.as_dictionary()
        # define index
        i = d.pop("DATETIME")
        # define table
        table = pd.DataFrame(d, index=i)
        self._dataframe_table = table
        return table
