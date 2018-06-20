import pandas as pd
import io
import string
import itertools as it
import pickle as pk

from talib.abstract import MA, EMA, WMA, RSI, CCI, ROC, MOM, WILLR

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
        self.all_symbols = symbols
        self.ref_symbol = reference
        # download tables
        if exist(self.PICKLE):
            self.ref_dataframe, self.all_dataframes = pk.load(open(self.PICKLE, "rb"))
        else:
            self.ref_dataframe = self._download_ref_data()
            self.all_dataframes = self._download_all_data()
            pk.dump((self.ref_dataframe, self.all_dataframes), open(self.PICKLE, "wb"))

        # initialize joint dataframe
        self.joint_dataframe = None

    def _get_filename(self, symbol):
        """Returns filename corresponding to given symbol."""
        if self.all_symbols.get(symbol)["category"] == "economic-calendar":
            return "{}.csv".format(self.all_symbols.get(symbol)["instrument"])
        else:
            return "{}-{}.csv".format(self.resolution, self.all_symbols.get(symbol)["instrument"])

    def _get_category(self, symbol):
        """Returns category of given symbol."""
        category = self.all_symbols.get(symbol)["category"]
        category = category.replace("-", " ")
        category = category.capitalize()
        return category

    def _download_ref_data(self):
        """Downloads reference symbol"""
        _id = self.filenames.get(self._get_filename(self.ref_symbol))
        reference_table = pd.read_csv(
            filepath_or_buffer=io.StringIO(self.client.CreateFile({"id":_id}).GetContentString().decode("utf-8")),
            index_col="Date",
            parse_dates=True
        )
        return reference_table

    def _download_all_data(self):
        """Downloads other symbols from symbols' dictionary."""
        tables = {}
        for symbol in self.all_symbols:
            print "downloading... \t{}".format(symbol)
            _id = self.filenames.get(self._get_filename(symbol))
            if symbol == self.ref_symbol:
                tables[symbol] = self.ref_dataframe.get("Close")
            else:
                tables[symbol] = pd.read_csv(
                    filepath_or_buffer=io.StringIO(self.client.CreateFile({"id":_id}).GetContentString().decode("utf-8")),
                    index_col="Date",
                    parse_dates=True,
                    usecols=("Date", ("Actual" if self.all_symbols.get(symbol)["category"] == "economic-calendar" else "Close"),)
                )
        return tables

    def get_technical(self, indicators={"EMA": EMA, "MA": MA, "WMA": WMA, "%R": WILLR, "CCI": CCI, "MOM": MOM, "ROC": ROC, "RSI": RSI}, periods=5):
        """Returns technical indicators for reference symbol."""
        # make a copy of reference table to handle TaLib functions
        df = self.ref_dataframe.copy()
        df.rename(str.lower, axis="columns", inplace=True)

        table = pd.DataFrame(
            index=self.ref_dataframe.index.copy(),
            columns=pd.MultiIndex.from_tuples(
                tuples=list(it.product(["Technical"], sorted(indicators.keys()))),
                names=["Category", "Name"]
            ),
            data=None
        )
        for name in sorted(indicators):
            table["Technical", name] = indicators[name](df, timeperiod=periods)

        return table

    def get_joint_dataframe(self):
        """Returns joint table with all symbols."""
        if self.joint_dataframe is not None: return self.joint_dataframe
        # initialize columns list
        tables = []
        for category in set(map(lambda s: self.all_symbols.get(s)["category"], self.all_symbols)):
            category_name = category.replace("-", " ").capitalize()
            # extract symbols of current catagory
            cat_symbols = sorted(filter(lambda s: self.all_symbols.get(s)["category"] == category, self.all_symbols))
            # fill tables list with symbols of current category
            table = pd.DataFrame(
                index=self.ref_dataframe.index.copy(),
                columns=pd.MultiIndex.from_tuples(
                    tuples=list(it.product([category_name], cat_symbols)),
                    names=["Category", "Name"]
                ),
                data=None
            )
            for symbol in cat_symbols: table[category_name, symbol] = self.all_dataframes.get(symbol)
            tables += [table]

        # add to tables list technical indicators from reference symbol
        tables += [self.get_technical()]
        # define joint dataframe
        self.joint_dataframe = pd.concat(tables, axis="columns")
        self.joint_dataframe.dropna(how="all", axis="index", inplace=True)
        self.joint_dataframe.interpolate(method="time", limit_direction="both", inplace=True)
        return self.joint_dataframe

    def get_prices(self):
        """Returns prices for the financial instruments."""
        if self.joint_dataframe is None: self.get_joint_dataframe()

        symbols = filter(lambda s: self.all_symbols.get(s)["category"] != "economic-calendar", self.all_symbols)
        symbols = map(lambda s: (self._get_category(s), s), symbols)

        df = self.joint_dataframe.filter(items=symbols)
        return df

    def get_returns(self):
        """Returns fraction of change for the financial instruments."""
        if self.joint_dataframe is None: self.get_joint_dataframe()

        symbols = filter(lambda s: self.all_symbols.get(s)["category"] != "economic-calendar", self.all_symbols)
        symbols = map(lambda s: (self._get_category(s), s), symbols)

        df = self.joint_dataframe.filter(items=symbols)
        df = df.pct_change()
        return df

    def get_economical(self):
        """Returns economic indicators."""
        if self.joint_dataframe is None: self.get_joint_dataframe()

        symbols = filter(lambda s: self.all_symbols.get(s)["category"] == "economic-calendar", self.all_symbols)
        symbols = map(lambda s: (self._get_category(s), s), symbols)

        df = self.joint_dataframe.filter(items=symbols)
        return df
