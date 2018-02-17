import quandl

# source: https://www.quandl.com/data/CHRIS/ICE_T4-WTI-Crude-Futures-Continuous-Contract
wti_crude_futures = quandl.get(["CHRIS/ICE_T1.1", "CHRIS/ICE_T1.2", "CHRIS/ICE_T1.3", "CHRIS/ICE_T1.4", "CHRIS/ICE_T1.7"])
wti_crude_futures.index.name = "DATE"
wti_crude_futures.columns = "OPEN HIGH LOW SETTLE VOLUME".split()
wti_crude_futures.insert(3, "CLOSE", wti_crude_futures["OPEN"].shift(-1))
wti_crude_futures.reset_index().to_csv("data/wti-crude.csv", index=False)
