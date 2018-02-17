import ffn
import currency_data

from constants import CURRENCIES
from collections import OrderedDict
from itertools import product

np = ffn.core.np
pd = ffn.data.pd
plt = ffn.core.plt

PERIOD_IN_DAYS = 30

pairs = currency_data.get_pairs()

PAIRS = ["USD/{}".format(currency) for currency in CURRENCIES]

# extract closing price for each instrument
close = pd.DataFrame(index=pairs["USD/EUR"].index)
for pair_name in PAIRS: close[pair_name] = pairs[pair_name].filter(like="close")

# remove metals because yahoo sucks at this instruments!
close.drop(columns=PAIRS[-2:], inplace=True)
CURRENCIES.remove("XAG")
CURRENCIES.remove("XAU")
# print close.tail(5)

# compute heatmap
H = pd.DataFrame(data=np.nan, index=CURRENCIES, columns=CURRENCIES)
print "Time window: {}".format(pairs["USD/EUR"].index[[-PERIOD_IN_DAYS, -1]].values)
for i, j in product(range(len(CURRENCIES)), range(len(CURRENCIES))):
    if CURRENCIES[i] == CURRENCIES[j]: continue

    # compute exchange rate of j/i
    ex_rate = close["USD/{}".format(CURRENCIES[i])] / close["USD/{}".format(CURRENCIES[j])]
    H.loc[CURRENCIES[i]][CURRENCIES[j]] = (ex_rate.iloc[-1] - ex_rate.iloc[-PERIOD_IN_DAYS]) / ex_rate.iloc[-PERIOD_IN_DAYS] * 100.0

ffn.core.plot_heatmap(H, cmap="RdBu_r")
plt.show()
