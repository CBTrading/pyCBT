import ffn

from collections import OrderedDict
from itertools import product
from pyCBT.data.providers.mt.pairs import get_mt_pairs

np = ffn.core.np
pd = ffn.data.pd
plt = ffn.core.plt

# define constants
# time frame in periods/minutes (because data is sampled in minutes)
TIME_FRAME = 5*30
# define target price
PRICE = "CLOSE"
# define volume column
VOLUME = "VOLUME"

pairs = get_mt_pairs()

PAIRS = pairs.keys()
CURRENCIES = np.unique([currency for pair in PAIRS for currency in [pair[:3], pair[3:]]])

# extract price for each instrument
price = pd.DataFrame(index=range(5*TIME_FRAME))
for pair_name in PAIRS: price[pair_name] = pairs[pair_name].filter(like=PRICE).values[-5*TIME_FRAME:]

# compute heatmap
H = pd.DataFrame(data=np.nan, index=CURRENCIES, columns=CURRENCIES)
for i, j in product(range(len(CURRENCIES)), range(len(CURRENCIES))):
    if CURRENCIES[i] == CURRENCIES[j]: continue
    pair_name = "{}{}".format(CURRENCIES[j], CURRENCIES[i])

    # compute exchange rate of j/i
    if pair_name in PAIRS:
        ex_rate = price[pair_name]
    else:
        # get j/USD
        if "USD{}".format(CURRENCIES[j]) in PAIRS:
            price_j = 1.0 / price["USD{}".format(CURRENCIES[j])]
        elif "{}USD".format(CURRENCIES[j]) in PAIRS:
            price_j = price["{}USD".format(CURRENCIES[j])]
        # get i/USD
        if "USD{}".format(CURRENCIES[i]) in PAIRS:
            price_i = 1.0 / price["USD{}".format(CURRENCIES[i])]
        elif "{}USD".format(CURRENCIES[i]) in PAIRS:
            price_i = price["{}USD".format(CURRENCIES[i])]

        ex_rate = price_j / price_i

    H.loc[CURRENCIES[i]][CURRENCIES[j]] = (ex_rate.iloc[-1] - ex_rate.iloc[-TIME_FRAME]) / ex_rate.iloc[-TIME_FRAME] * 100.0

ffn.core.plot_heatmap(H, cmap="RdBu_r")
plt.show()
