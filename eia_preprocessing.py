import ffn, os
import scipy.signal as signal

from pyCBT.constants import DATADIR

eia_path = os.path.join(DATADIR, "providers/eia")
wti_path = os.path.join(DATADIR, "providers/quandl")
brn_path = os.path.join(DATADIR, "providers/yahoo")

np = ffn.core.np
pd = ffn.data.pd
plt = ffn.core.plt

# finance raw data ---------------------------------------------------------------------------------
wti_crude = pd.read_csv("{}/wti-crude.csv".format(wti_path), index_col="DATE").sort_index()
wti_crude.index = pd.DatetimeIndex(wti_crude.index)
wti_crude = wti_crude.resample("B").pad()
wti_price = wti_crude.get("CLOSE")
wti_price.name = "WTI"
# wti_crude["VOLUME"] = signal.medfilt(wti_crude["VOLUME"], 31)

brn_crude = pd.read_csv("{}/brent-crude.csv".format(brn_path), index_col="DATE").sort_index()
brn_crude.index = pd.DatetimeIndex(brn_crude.index)
brn_crude = brn_crude.resample("B").pad()
brn_price = brn_crude.get("CLOSE")
brn_price.name = "BRENT"
# brn_crude["VOLUME"] = signal.medfilt(brn_crude["VOLUME"], 31)

# economic data ------------------------------------------------------------------------------------
# supply raw data
# monthly production (thousand barrels)
production = pd.read_csv("{}/production_mbbl.csv".format(eia_path), index_col="DATE").sort_index()
production.index = pd.DatetimeIndex(production.index)
# resample weekly
production = production.resample("B").pad()

# weekly stocks (thousand barrels)
stocks = pd.read_csv("{}/stocks_mbbl.csv".format(eia_path), index_col="DATE").sort_index()
stocks.index = pd.DatetimeIndex(stocks.index)
stocks = stocks.resample("B").pad()
# compute delta(weekly) in stocks
stocks_growth = stocks.diff()
stocks_growth.columns = ["STOCKS_GROWTH"]

# demand raw data
# weekly exp/imp thousand barrels per day & convert to net number of barrels
exports = pd.read_csv("{}/exports_mbbl-day.csv".format(eia_path),
                      index_col="DATE").sort_index() * 30.0
exports.index = pd.DatetimeIndex(exports.index)
exports = exports.resample("B").pad()
imports = pd.read_csv("{}/imports_mbbl-day.csv".format(eia_path),
                      index_col="DATE").sort_index() * 30.0
imports.index = pd.DatetimeIndex(imports.index)
imports = imports.resample("B").pad()

# join tables
dfs = [
    wti_price,
    brn_price,
    exports,
    imports,
    production,
    stocks,
    stocks_growth
]
joint_eia_series = pd.concat(dfs, axis=1)
joint_eia_series.dropna(inplace=True)
print joint_eia_series.describe()
