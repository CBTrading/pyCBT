import pandas as pd
import oandapyV20
import oandapyV20.enpoints.instruments as instruments
from oandapyV20.types import DateTime
from datetime import datetime
from .account import Config

class Candles(object):

    def __init__(self, account, instrument, resolution, from_date, to_date=None, timezone=None):

        # get config summary
        config = Config(account=account)
        self.account_summary = config.get_from_file()
        r_params = {
            "timeout": self.account_summary.pop("timeout"),
            "Accept-Datetime-Format": self.account_summary.pop("datetime_format")
        }
        # instantiate API client
        self.api = oandapyV20.API(
            access_token=self.account_summary.pop("token"),
            environment=self.account_summary.pop("environment"),
            request_params=r_params
        )
        # define params of candles
        self.instrument = instrument
        self.resolution = resolution
        self.from_date = datetime(from_date)
        self.to_date = datetime(to_date)
        self.timezone = self.account_summary.pop("timezone") if timezone is None else timezone
        self.candles_params = {
            "granularity": self.resolution,
            "alignmentTimezone": self.timezone,
            "from": self.from_date,
            "to": self.to_date
        }
        # generate request for candles
        self.request = InstrumentsCandlesFactory(
        instrument=self.instrument,
        params=self.candles_params
        )
        # generate request for candles
        self.requests = instruments.InstrumentsCandlesFactory(instrument, params)

    def get_response(self):
        self.candles_responses = []
        for request in self.requests:
            self.api.request(request)
        self.candles_responses += [request.response.get("candles")]
        return self.candles_responses

    def as_pandas(self):
        pass
