# def get_indicators():
import ffn
import scipy.signal as signal

np = ffn.core.np
pd = ffn.data.pd
plt = ffn.core.plt

# economic data
# supply raw data
# monthly production (thousand barrels)
production = pd.read_csv("data/eia-production_mbbl.csv", index_col="DATE").sort_index()
production.index = pd.DatetimeIndex(production.index)
production.index = production.index.shift(-1, freq="B")

# weekly stocks (thousand barrels)
stocks = pd.read_csv("data/eia-stocks_mbbl.csv", index_col="DATE").sort_index()
# resample monthly
stocks.index = pd.DatetimeIndex(stocks.index)
stocks = stocks.resample("M").first()
stocks_growth = stocks.diff()

# demand raw data
# weekly e/i thousand barrels per day
exports = pd.read_csv("data/eia-exports_mbbl-day.csv", index_col="DATE").sort_index()
exports.index = pd.DatetimeIndex(exports.index)
# resample monthly & convert to net number of barrels
exports = exports.resample("M").first() * 30.0

imports = pd.read_csv("data/eia-imports_mbbl-day.csv", index_col="DATE").sort_index()
imports.index = pd.DatetimeIndex(imports.index)
# resample monthly & convert to net number of barrels
imports = imports.resample("M").first() * 30.0

# finance raw data
wti_crude = pd.read_csv("data/wti-crude.csv", index_col="DATE").sort_index()
wti_crude.index = pd.DatetimeIndex(wti_crude.index)
wti_crude = wti_crude.resample("M").first()
# wti_crude["VOLUME"] = signal.medfilt(wti_crude["VOLUME"], 31)

brent_crude = pd.read_csv("data/brent-crude.csv", index_col="DATE").sort_index()
brent_crude.index = pd.DatetimeIndex(brent_crude.index)
brent_crude = brent_crude.resample("M").first()
brent_crude["VOLUME"] = signal.medfilt(brent_crude["VOLUME"], 31)

# indicators
products = pd.DataFrame()
products["PRODUCTS"] = production["PRODUCTION"] + imports["IMPORTS"] - (stocks_growth["STOCKS"] + exports["EXPORTS"])

# supply
supply = pd.DataFrame()
supply["SUPPLY"] = stocks["STOCKS"] / production["PRODUCTION"]
# resample supply daily
supply = supply.dropna().resample("D").pad()

# demand
demand = pd.DataFrame(index=supply.index)
demand["DEMAND"] = 1 / supply["SUPPLY"]

# combine datasets
wti_indicators = pd.concat([wti_crude, supply, demand], axis=1, join_axes=[wti_crude.index])
brent_indicators = pd.concat([brent_crude, supply, demand], axis=1, join_axes=[brent_crude.index])

# correlations
# supply_price = pd.Series(index=wti_indicators.index,
#                          data=np.correlate(wti_indicators["SUPPLY"],
#                                            wti_indicators["CLOSE"], mode="same"))
# demand_price = pd.Series(index=wti_indicators.index,
#                          data=np.correlate(wti_indicators["DEMAND"],
#                                            wti_indicators["CLOSE"], mode="same"))
# plots --------------------------------------------------------------------------------------------
# plt.figure()
# wti_indicators["CLOSE"].plot(title="price")
# plt.figure()
# wti_indicators["SUPPLY"].plot(title="supply")
# plt.figure()
# wti_indicators["DEMAND"].plot(title="demand")
#
# plt.figure()
# supply_price.plot(title="supply-price correlation")
#
# plt.figure()
# demand_price.plot(title="demand-price correlation")
#
# plt.show()

# if __name__ == "__main__":
#     indicators = get_indicators()
#
#     print indicators.describe()
