
import pandas as pd
import numpy as np

from collections import OrderedDict
from pyCBT.data.providers.mt.pairs import get_mt_pairs

# define constants
# time frame in periods/minutes (because data is sampled in minutes)
TIME_FRAME = 30
# define target price
PRICE = "CLOSE"
# define volume column
VOLUME = "VOLUME"

# load data pairs
pairs = get_mt_pairs()

historical_volatility = OrderedDict()
for symbol in pairs:
    time = pairs[symbol].index.values
    price = pairs[symbol][PRICE]
    binned_time = pd.cut(time, bins=time[::TIME_FRAME])
    # print binned_time
    binned_pair = price.groupby(binned_time)

    historical_volatility[symbol] = []
    for _bin in sorted(binned_pair.groups):
        sample = binned_pair.get_group(_bin)
        mean = np.mean(sample)
        stdd = np.std(sample)

        historical_volatility[symbol] += [stdd / mean * 100.0]

recent_volatility = OrderedDict()
for symbol in historical_volatility:
    recent_volatility[symbol] = historical_volatility[symbol][-50:]

recent_volatility = pd.DataFrame(recent_volatility)
print recent_volatility.tail(5)
