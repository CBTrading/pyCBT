import pandas as pd
from .account import get_client

from pyCBT.common._constants import (
    indices_symbols, sp500_sectors_symbols, stocks_symbols, commodities_symbols,
    currencies_symbols, economical_symbols, features_params, features_types
)

class DriveTables(object):
    # parent ID of data tables in Google Drive
    DATA_ID = "1etaxbcHUa8YKiNw0tEkIyMtnC8DShRxQ"
    RESOLUTIONS = ["daily", "weekly", "monthly"]
    CATEGORIES = features_types

    def __init__(self, symbols, reference, resolution="daily", client=None):
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
        # initialize files list from Google Drive
        self.filenames = {}
        for file in self.client.ListFile({"q": "'{}' in parents".format(self.DATA_ID)}).GetList():
            self.filenames[file.get("title")] = file.get("id")

        # initialize object attributes
        self.symbols = symbols
        self.reference = reference
        # download tables
        self.reference_table = self._download_reference_symbol()
        self.symbols_table = self._download_other_symbols()
        self.features = None

    def _get_filename(self, symbol):
        if self.symbols.get(symbol)["category"] == "economic-calendar":
            return "{}.csv".format(self.symbols.get(symbol)["instrument"])
        else:
            return "{}-{}.csv".format(self.resolution, self.symbols.get(symbol)["instrument"])

    def _download_reference_symbol(self):
        _id = self.filenames.get(self._get_filename(self.reference))
        reference_table = pd.read_csv(
            filepath_or_buffer=io.StringIO(self.client.CreateFile({"id":_id}).GetContentString().decode("utf-8")),
            index_col="Date",
            parse_dates=True
        )
        return reference_table

    def _download_other_symbols(self):
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

    def build(self, lag_periods=1):
        ref_index = ref_table.index.copy()
        X = pd.DataFrame(
            index=ref_index,
            columns=pd.MultiIndex.from_tuples(
                tuples=list(it.product(["Indices"], sorted(major_indices.keys()))),
                names=["Type", "Name"]
            ),
            data=None
        )
