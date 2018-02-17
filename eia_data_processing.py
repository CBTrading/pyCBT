import ffn
import scipy.signal as signal

np = ffn.core.np
pd = ffn.data.pd
plt = ffn.core.plt

# finance raw data ---------------------------------------------------------------------------------
wti_crude = pd.read_csv("data/wti-crude.csv", index_col="DATE").sort_index()
wti_crude.index = pd.DatetimeIndex(wti_crude.index)
wti_crude = wti_crude.resample("W").first()
# wti_crude["VOLUME"] = signal.medfilt(wti_crude["VOLUME"], 31)

brent_crude = pd.read_csv("data/brent-crude.csv", index_col="DATE").sort_index()
brent_crude.index = pd.DatetimeIndex(brent_crude.index)
# brent_crude = brent_crude.resample("M").first()
brent_crude["VOLUME"] = signal.medfilt(brent_crude["VOLUME"], 31)

# economic data ------------------------------------------------------------------------------------
# supply raw data
# monthly production (thousand barrels)
production = pd.read_csv("data/eia-production_mbbl.csv", index_col="DATE").sort_index()
production.index = pd.DatetimeIndex(production.index)
# resample weekly
production = production.resample("W").pad()

# weekly stocks (thousand barrels)
stocks = pd.read_csv("data/eia-stocks_mbbl.csv", index_col="DATE").sort_index()
stocks.index = pd.DatetimeIndex(stocks.index)
# compute delta(weekly) in stocks
stocks_growth = stocks.diff()

# demand raw data
# weekly exp/imp thousand barrels per day & convert to net number of barrels
exports = pd.read_csv("data/eia-exports_mbbl-day.csv", index_col="DATE").sort_index() * 30.0
exports.index = pd.DatetimeIndex(exports.index)

imports = pd.read_csv("data/eia-imports_mbbl-day.csv", index_col="DATE").sort_index() * 30.0
imports.index = pd.DatetimeIndex(imports.index)
