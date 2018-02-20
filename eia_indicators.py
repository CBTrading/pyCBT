# np = ffn.core.np
# pd = ffn.data.pd
# plt = ffn.core.plt
#
# # economic data
# # supply raw data
# # monthly production (thousand barrels)
# production = pd.read_csv("data/eia-production_mbbl.csv", index_col="DATE").sort_index()
# production.index = pd.DatetimeIndex(production.index)
# production.index = production.index.shift(-1, freq="B")
#
# # weekly stocks (thousand barrels)
# stocks = pd.read_csv("data/eia-stocks_mbbl.csv", index_col="DATE").sort_index()
# # resample monthly
# stocks.index = pd.DatetimeIndex(stocks.index)
# stocks = stocks.resample("M").first()
# stocks_growth = stocks.diff()
#
# # demand raw data
# # weekly e/i thousand barrels per day
# exports = pd.read_csv("data/eia-exports_mbbl-day.csv", index_col="DATE").sort_index()
# exports.index = pd.DatetimeIndex(exports.index)
# # resample monthly & convert to net number of barrels
# exports = exports.resample("M").first() * 30.0
#
# imports = pd.read_csv("data/eia-imports_mbbl-day.csv", index_col="DATE").sort_index()
# imports.index = pd.DatetimeIndex(imports.index)
# # resample monthly & convert to net number of barrels
# imports = imports.resample("M").first() * 30.0
#
# # finance raw data
# wti_crude = pd.read_csv("data/wti-crude.csv", index_col="DATE").sort_index()
# wti_crude.index = pd.DatetimeIndex(wti_crude.index)
# wti_crude = wti_crude.resample("M").first()
# # wti_crude["VOLUME"] = signal.medfilt(wti_crude["VOLUME"], 31)
#
# brent_crude = pd.read_csv("data/brent-crude.csv", index_col="DATE").sort_index()
# brent_crude.index = pd.DatetimeIndex(brent_crude.index)
# brent_crude = brent_crude.resample("M").first()
# brent_crude["VOLUME"] = signal.medfilt(brent_crude["VOLUME"], 31)

# --------------------------------------------------------------------------------------------------

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
joint_eia = pd.concat(dfs, axis=1)
joint_eia.dropna(inplace=True)


# indicators
joint_eia["PRODUCTS"] = joint_eia["PRODUCTION"] + joint_eia["IMPORTS"] - \
                       (joint_eia["STOCKS_GROWTH"] + joint_eia["EXPORTS"])
# supply
joint_eia["SUPPLY"] = joint_eia["STOCKS"] / joint_eia["PRODUCTION"]
# demand
joint_eia["DEMAND"] = 1 / joint_eia["SUPPLY"]

# correlations
corr_supply_price = pd.Series(index=joint_eia.index,
                         data=np.correlate(joint_eia["SUPPLY"],
                                           joint_eia["BRENT"], mode="same"))
corr_demand_price = pd.Series(index=joint_eia.index,
                         data=np.correlate(joint_eia["DEMAND"],
                                           joint_eia["BRENT"], mode="same"))
# plots --------------------------------------------------------------------------------------------
# drop some sweet plots here
