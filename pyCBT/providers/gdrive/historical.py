import pandas as pd
import io
import string
import itertools as it
import pickle as pk

from talib import MA, EMA, WMA, RSI, CCI, ROC, MOM, WILLR

from pyCBT.providers.gdrive.account import get_client
from pyCBT.common.path import exist


class DriveTables(object):
    # parent ID of data tables in Google Drive
    RESOLUTIONS = ["daily", "weekly", "monthly"]

    def __init__(self, symbols, reference, resolution="daily", client=None, drive_data_id="1etaxbcHUa8YKiNw0tEkIyMtnC8DShRxQ"):
        if resolution not in self.RESOLUTIONS:
            raise ValueError, "{} not in resolution valid values: {}".format(resolution, string.join(self.RESOLUTIONS, ", "))
        # authenticate user & start Google Drive client
        if not reference in symbols.keys():
            raise ValueError, "{} not in symbols list.".format(reference)
        if not client:
            self.client = get_client()
        else:
            self.client = client

        self.resolution = resolution
        self.DATA_ID = drive_data_id
        self.PICKLE = "gdrive-{}.p".format(self.DATA_ID)
        # initialize files list from Google Drive
        self.filenames = {}
        for file in self.client.ListFile({"q": "'{}' in parents".format(self.DATA_ID)}).GetList():
            self.filenames[file.get("title")] = file.get("id")

        # initialize object attributes
        self.symbols = symbols
        self.reference = reference
        # download tables
        if exist(self.PICKLE):
            self.reference_table, self.symbols_table = pk.load(open(self.PICKLE, "rb"))
        else:
            self.reference_table = self._download_reference_symbol()
            self.symbols_table = self._download_other_symbols()
            pk.dump((self.reference_table, self.symbols_table), open(self.PICKLE, "wb"))

        # initialize features
        self._features_params = None
        self.features = None

    def _get_filename(self, symbol):
        """Returns filename corresponding to given symbol."""
        if self.symbols.get(symbol)["category"] == "economic-calendar":
            return "{}.csv".format(self.symbols.get(symbol)["instrument"])
        else:
            return "{}-{}.csv".format(self.resolution, self.symbols.get(symbol)["instrument"])

    def _get_category(self, symbol):
        """Returns category of given symbol."""
        category = self.symbols.get(symbol)["category"]
        category = category.replace("-", " ")
        category = category.capitalize()
        return category

    def _download_reference_symbol(self):
        """Downloads reference symbol"""
        _id = self.filenames.get(self._get_filename(self.reference))
        reference_table = pd.read_csv(
            filepath_or_buffer=io.StringIO(self.client.CreateFile({"id":_id}).GetContentString().decode("utf-8")),
            index_col="Date",
            parse_dates=True
        )
        return reference_table

    def _download_other_symbols(self):
        """Downloads other symbols from symbols' dictionary."""
        tables = {}
        for symbol in self.symbols:
            print "downloading... \t{}".format(symbol)
            _id = self.filenames.get(self._get_filename(symbol))
            if symbol == self.reference:
                tables[symbol] = self.reference_table.get("Close")
            else:
                tables[symbol] = pd.read_csv(
                    filepath_or_buffer=io.StringIO(self.client.CreateFile({"id":_id}).GetContentString().decode("utf-8")),
                    index_col="Date",
                    parse_dates=True,
                    usecols=("Date", ("Actual" if self.symbols.get(symbol)["category"] == "economic-calendar" else "Close"),)
                )
        return tables

    def get_features(self, lag_periods=1, ti_periods=5):
        """Returns features table."""

        # check if features exist with same parameters
        if self.features is not None and self._features_params == (lag_periods, ti_periods): return self.features
        # define features parameters
        self._features_params = (lag_periods, ti_periods)
        # copy reference index to build features table
        ref_index = self.reference_table.index.copy()
        # extract columns from raw data
        # initialize columns list
        tables = []
        for category in set(map(lambda p: self.symbols.get(p)["category"], self.symbols)):
            category_name = category.replace("-", " ").capitalize()
            # extract symbols of current catagory
            cat_symbols = filter(lambda s: self.symbols.get(s)["category"] == category, self.symbols)
            # define lag for given category (economic calendars will not be lagged)
            lag = lag_periods if category != "economical-calendar" else 0
            # fill tables list with symbols of current category
            table = pd.DataFrame(
                index=ref_index,
                columns=pd.MultiIndex.from_tuples(
                    tuples=list(it.product([category_name], cat_symbols)),
                    names=["Category", "Name"]
                ),
                data=None
            )
            for symbol in cat_symbols: table[category_name, symbol] = self.symbols_table.get(symbol).shift(lag)
            tables += [table]

        # add to tables list technical indicators from reference symbol
        table = pd.DataFrame(
            index=ref_index,
            columns=pd.MultiIndex.from_tuples(
                tuples=list(it.product(["Technical"], ["EMA", "MA", "WMA", "%R", "CCI", "MOM", "ROC", "RSI"])),
                names=["Category", "Name"]
            ),
            data=None
        )
        table["Technical", "EMA"] = EMA(self.reference_table.Close.shift(lag), ti_periods)
        table["Technical", "MA"] = MA(self.reference_table.Close.shift(lag), ti_periods, matype=0)
        table["Technical", "WMA"] = WMA(self.reference_table.Close.shift(lag), ti_periods)
        table["Technical", "%R"] = WILLR(self.reference_table.High.shift(lag), self.reference_table.Low.shift(lag), self.reference_table.Close.shift(lag), ti_periods)
        table["Technical", "CCI"] = CCI(self.reference_table.High.shift(lag), self.reference_table.Low.shift(lag), self.reference_table.Close.shift(lag), ti_periods)
        table["Technical", "MOM"] = MOM(self.reference_table.Close.shift(lag), ti_periods)
        table["Technical", "ROC"] = ROC(self.reference_table.Close.shift(lag), ti_periods)
        table["Technical", "RSI"] = RSI(self.reference_table.Close.shift(lag), ti_periods)
        tables += [table]
        # define features
        self.features = pd.concat(tables, axis="columns")
        self.features.dropna(how="all", axis="index", inplace=True)
        self.features.interpolate(method="time", limit_direction="both", inplace=True)
        return self.features
