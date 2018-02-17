import stockstats
import ffn
import fxchoice_data

from itertools import combinations
from collections import OrderedDict

np = ffn.core.np
pd = ffn.data.pd
plt = ffn.core.plt

instruments = fxchoice_data.get_instruments()

# transform into stockstats type to apply finance indicators
for symbol in instruments:
    instruments[symbol] = stockstats.StockDataFrame.retype(instruments[symbol])

    # Stochastic Oscillator follows the speed or the momentum of the price. As a rule,
    # momentum changes before the price changes. It measures the level of the closing price
    # relative to low-high range over a period of time (14 days in this case).
    instruments[symbol].get("kdjk_14")
    # instruments[symbol].get("kdjd_14")
    # instruments[symbol].get("kdjj_14")

    # Williams %R ranges from -100 to 0. When its value is above -20, it indicates a sell signal
    # and when its value is below -80, it indicates a buy signal (14 days).
    instruments[symbol].get("wr_14")

    # When the MACD goes below the SingalLine, it indicates a sell signal. When it goes above the
    # SignalLine, it indicates a buy signal.
    # instruments[symbol].get("macd")

    # Price Rate of Change (PROC) measures the most recent change in price with respect to the price
    # in n days ago (using closing price).
    # instruments[symbol].get("close_-14_r")

    # Bollinger Bands, se define como la region entre K desviaciones estandar respecto de
    # la media movil en N periodos. Es una medida de la volatilidad.
    # instruments[symbol].get("boll")
    # instruments[symbol].get("boll_ub")
    # instruments[symbol].get("boll_lb")

    # RSI is a popular momentum indicator which determines whether the stock is overbought
    # or oversold. A stock is said to be overbought when the demand unjustifiably pushes
    # the price upwards.
    instruments[symbol].get("rsi_14")

ti_names = instruments[symbol].columns.values[5:]

correlations = OrderedDict()
print len(ti_names), len(list(combinations(ti_names, 2)))
for ti_a, ti_b in combinations(ti_names, 2):
    # define domain
    time = instruments[symbol].index.values
    # compute bins
    # bins = np.diff(time, 7)
    binned_time = pd.cut(time, bins=10)
    binned_ti_a = instruments[symbol][ti_a].groupby(binned_time)
    binned_ti_b = instruments[symbol][ti_b].groupby(binned_time)
    # compute correlation in each bin
    key = "corr-{}-{}".format(ti_a, ti_b)
    correlations[key] = []
    for bin_name in sorted(binned_ti_a.groups):
        correlations[key].append(np.corrcoef(
                                            binned_ti_a.get_group(bin_name),
                                            binned_ti_b.get_group(bin_name)
                                            )[1,0]
                                )
corrs = pd.DataFrame(correlations, index=sorted(binned_ti_a.groups))
corrs.plot(legend=False)
plt.show()
